from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
import re

from opencc import OpenCC


BASE = Path(r"C:\Users\lx\Desktop\前期准备\prepare")
FULLTEXT = BASE / "fulltext.txt"
TRANSITIONAL = BASE / "酉阳杂俎方南生校.txt"
REFERENCE = BASE / "酉阳杂俎-许逸民校-2015.md"
OUTPUT = BASE / "酉阳杂俎-初校.md"


cc_t2s = OpenCC("t2s")
cc_s2t = OpenCC("s2t")

PUNCT_RE = re.compile(r"[\s\u3000，。、「」『』【】〔〕（）()《》〈〉；：？！—…,.!?:;\-·‧“”‘’\"'\[\]{}<>|]")
PAGE_RE = re.compile(r"【第\d+页】")
TRAILING_NOTE_RE = re.compile(r"[︹〔\[][^︺〕\]]{1,12}[︺〕\]]")
INLINE_NOTE_RE = re.compile(r"一作[「『﹁][^」』﹂]{1,20}[」』﹂]")
LEADING_NUM_RE = re.compile(r"^[0-9０-９]+")
HEADING_NUM_RE = re.compile(r"^卷[一二三四五六七八九十百]+")
DOUBLE_BRACE_RE = re.compile(r"\{\{[^}]+\}\}")
PAREN_NOTE_RE = re.compile(r"[（(][一二三四五六七八九十百千0-9]+[）)]")
OCR_PREFIX_RE = re.compile(r"^[0-9０-９A-Za-z&＆《。?“？#＃\$\*+\-=]+")
RUNNING_HEADER_RE = re.compile(r"^(前集卷|續集卷|酉陽雜俎前集卷之|酉陽雜俎續集卷之)")
HEADINGS = {
    "序",
    "忠志",
    "禮異",
    "天咫",
    "玉格",
    "壺史",
    "貝編",
    "境異",
    "喜兆",
    "禍兆",
    "物革",
    "詭習",
    "怪術",
    "藝絶",
    "器奇",
    "樂",
    "酒食",
    "醫",
    "黥",
    "雷",
    "夢",
    "事感",
    "盜俠",
    "物異",
    "廣知",
    "語資",
    "冥蹟",
    "尸穸",
    "諾臯記上",
    "諾臯記下",
    "廣動植之一",
    "羽篇",
    "毛篇",
    "廣動植之二",
    "鱗介篇",
    "蟲篇",
    "廣動植之三",
    "木篇",
    "廣動植之四",
    "草篇",
    "肉攫部",
    "支諾臯上",
    "支諾臯中",
    "支諾臯下",
    "貶誤",
    "寺塔記上",
    "寺塔記下",
    "金剛經鳩異",
    "支動",
    "支植上",
    "支植下",
}


@dataclass
class Section:
    heading: str
    blocks: list[str]


def normalize_compare(text: str) -> str:
    text = PAGE_RE.sub("", text.strip())
    text = DOUBLE_BRACE_RE.sub("", text)
    text = TRAILING_NOTE_RE.sub("", text)
    text = PAREN_NOTE_RE.sub("", text)
    text = INLINE_NOTE_RE.sub("", text)
    text = OCR_PREFIX_RE.sub("", text)
    text = LEADING_NUM_RE.sub("", text)
    if "|" in text:
        text = text.split("|")[-1]
    text = PUNCT_RE.sub("", text)
    return cc_t2s.convert(text)


def parse_original_sections(path: Path) -> list[Section]:
    lines = path.read_text(encoding="utf-8").splitlines()
    markers: list[int] = []
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        before = lines[i - 2 : i]
        after = lines[i + 1 : i + 3]
        if len(before) == 2 and len(after) == 2 and all(not x.strip() for x in before + after):
            markers.append(i)

    sections: list[Section] = []
    for marker_index, start in enumerate(markers):
        end = markers[marker_index + 1] if marker_index + 1 < len(markers) else len(lines)
        heading = lines[start].strip()
        blocks: list[str] = []
        current: list[str] = []
        for line in lines[start + 3 : end]:
            if line.strip():
                current.append(line.strip())
            elif current:
                blocks.append("".join(current))
                current = []
        if current:
            blocks.append("".join(current))
        sections.append(Section(heading=heading, blocks=blocks))
    return sections


def parse_target_lines(path: Path, body_start_hint: str) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    started = False
    for raw in lines:
        line = PAGE_RE.sub("", raw).strip()
        if not line:
            out.append("")
            continue
        if not started:
            if body_start_hint in normalize_compare(line):
                started = True
            else:
                continue
        out.append(line)
    return out


def line_match_score(block_text: str, candidate_line: str) -> float:
    block_norm = normalize_compare(block_text)
    line_norm = normalize_compare(candidate_line)
    if len(block_norm) < 4 or len(line_norm) < 2:
        return 0.0
    block_prefix = block_norm[: min(18, len(block_norm))]
    line_prefix = line_norm[: min(18, len(line_norm))]

    common = 0
    for ch1, ch2 in zip(block_prefix, line_prefix):
        if ch1 == ch2:
            common += 1
        else:
            break
    ratio = SequenceMatcher(None, block_prefix, line_prefix).ratio()
    score = max(common / max(4, min(len(block_prefix), len(line_prefix))), ratio * 0.7)
    if block_prefix[:4] == line_prefix[:4]:
        score += 0.4
    elif block_prefix[:3] == line_prefix[:3]:
        score += 0.25
    return score


def is_skip_line(line: str) -> bool:
    if not line:
        return True
    if RUNNING_HEADER_RE.match(line):
        return True
    if line in HEADINGS:
        return True
    if line == "# 前集卷":
        return True
    if line in {"禮", "異"}:
        return True
    return False


def find_block_start(lines: list[str], start_pos: int, block: str, note_marker: str) -> int | None:
    best_idx: int | None = None
    best_score = 0.0
    for idx in range(start_pos, len(lines)):
        line = lines[idx]
        if not line or is_skip_line(line) or line == "校勘記" or line.startswith("本條"):
            continue
        score = line_match_score(block, line)
        if score > best_score:
            best_score = score
            best_idx = idx
        if score >= 1.0:
            break
        if best_idx is not None and idx - best_idx > 80:
            break
    if best_idx is not None and best_score >= 0.52:
        return best_idx
    return None


def collect_block(lines: list[str], start_idx: int, next_block: str | None, note_marker: str) -> tuple[str, int]:
    parts: list[str] = []
    idx = start_idx
    while idx < len(lines):
        line = lines[idx]
        if idx != start_idx:
            if note_marker == "校勘記" and line == "校勘記":
                break
            if note_marker == "本條" and line.startswith("本條"):
                break
            if next_block and not is_skip_line(line) and line_match_score(next_block, line) >= 0.72:
                break
        if not is_skip_line(line) and line != "校勘記" and not line.startswith("本條"):
            parts.append(line)
        idx += 1
    return "".join(parts), idx


def align_target_blocks(lines: list[str], original_blocks: list[str], note_marker: str) -> list[str]:
    aligned: list[str] = []
    pos = 0
    for i, block in enumerate(original_blocks):
        start_idx = find_block_start(lines, pos, block, note_marker)
        if start_idx is None:
            aligned.append("")
            continue
        next_block = original_blocks[i + 1] if i + 1 < len(original_blocks) else None
        text, pos = collect_block(lines, start_idx, next_block, note_marker)
        aligned.append(text)
    return aligned


def cleanup_final_text(text: str) -> str:
    text = PAGE_RE.sub("", text.strip())
    text = RUNNING_HEADER_RE.sub("", text)
    text = DOUBLE_BRACE_RE.sub("", text)
    text = TRAILING_NOTE_RE.sub("", text)
    text = PAREN_NOTE_RE.sub("", text)
    text = INLINE_NOTE_RE.sub("", text)
    text = OCR_PREFIX_RE.sub("", text)
    text = LEADING_NUM_RE.sub("", text)
    return cc_t2s.convert(text)


def should_replace(original: str, transitional: str, reference: str) -> bool:
    if not transitional or not reference:
        return False
    o = normalize_compare(original)
    t = normalize_compare(transitional)
    r = normalize_compare(reference)
    if not t or not r:
        return False
    if t != r:
        return False
    return o != r


def fix_block(original: str, reference: str) -> str:
    fixed = cleanup_final_text(reference)
    if not fixed:
        return original
    return fixed


def rebuild_markdown(sections: list[Section], corrected_blocks: list[str]) -> str:
    out: list[str] = []
    block_pos = 0
    for section in sections:
        out.append(section.heading)
        out.append("")
        out.append("")
        for _block in section.blocks:
            out.append(corrected_blocks[block_pos])
            out.append("")
            block_pos += 1
        if out and out[-1] == "":
            out.append("")
    while out and not out[-1].strip():
        out.pop()
    return "\n".join(out) + "\n"


def main() -> None:
    sections = parse_original_sections(FULLTEXT)
    original_blocks = [block for section in sections for block in section.blocks]
    body_start = normalize_compare(original_blocks[0])[:12]
    transitional_lines = parse_target_lines(TRANSITIONAL, body_start)
    reference_lines = parse_target_lines(REFERENCE, normalize_compare(original_blocks[1])[:12])

    aligned_transitional = align_target_blocks(transitional_lines, original_blocks, "校勘記")
    aligned_reference = align_target_blocks(reference_lines, original_blocks[1:], "本條")
    aligned_reference = [""] + aligned_reference

    corrected_blocks: list[str] = []
    replacements = 0
    for original, transitional, reference in zip(original_blocks, aligned_transitional, aligned_reference):
        if should_replace(original, transitional, reference):
            corrected_blocks.append(fix_block(original, reference))
            replacements += 1
        else:
            corrected_blocks.append(original)

    OUTPUT.write_text(rebuild_markdown(sections, corrected_blocks), encoding="utf-8")

    print(f"original_blocks={len(original_blocks)}")
    print(f"transitional_lines={len(transitional_lines)}")
    print(f"reference_lines={len(reference_lines)}")
    print(f"replacements={replacements}")
    print(f"wrote={OUTPUT.name}")


if __name__ == "__main__":
    main()

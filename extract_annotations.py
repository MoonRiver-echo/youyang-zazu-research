from __future__ import annotations

from difflib import SequenceMatcher
from pathlib import Path
import re


BASE = Path(r"C:\Users\lx\Desktop\前期准备\prepare")
FULLTEXT = BASE / "fulltext.txt"
TRANSITIONAL = BASE / "酉阳杂俎方南生校.txt"
REFERENCE = BASE / "酉阳杂俎-许逸民校-2015.md"
TRANSITIONAL_OUT = BASE / "酉阳杂俎方南生校-annotations.txt"
REFERENCE_OUT = BASE / "酉阳杂俎-许逸民校-2015-annotations.txt"


PAGE_RE = re.compile(r"【第\d+页】")
PUNCT_RE = re.compile(
    r"[\s\u3000\|，。、「」『』【】〔〕（）()《》〈〉；：？！—…,.!?:;\-·‧“”‘’\"'\[\]{}<>]"
)
ASCII_NOISE_RE = re.compile(r"[0-9０-９A-Za-zＯｏoOnnrDlRuH]")
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


def is_heading_line(text: str) -> bool:
    stripped = PAGE_RE.sub("", text.strip())
    if not stripped:
        return False
    if stripped in HEADINGS:
        return True
    if stripped.startswith("酉陽雜俎前集卷之") or stripped.startswith("酉陽雜俎續集卷之"):
        return True
    if stripped.startswith("卷") and len(stripped) <= 4:
        return True
    return False


def split_blocks(lines: list[str]) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    for line in lines:
        if line.strip():
            current.append(line)
        elif current:
            blocks.append("\n".join(current))
            current = []
    if current:
        blocks.append("\n".join(current))
    return blocks


def normalize_for_match(text: str) -> str:
    text = text.strip()
    text = PAGE_RE.sub("", text)
    text = re.sub(r"^[0-9０-９]+", "", text)
    text = re.sub(r"^[A-Za-z\$D&＆]+", "", text)
    text = re.sub(r"^[︹〔\[\(][^\s]{0,8}[︺〕\]\)]", "", text)
    if "|" in text:
        text = text.split("|")[-1]
    text = PUNCT_RE.sub("", text)
    text = ASCII_NOISE_RE.sub("", text)
    return text


def parse_main_original_blocks(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    section_markers: list[int] = []
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        before = lines[i - 2 : i]
        after = lines[i + 1 : i + 3]
        if len(before) == 2 and len(after) == 2 and all(not x.strip() for x in before + after):
            section_markers.append(i)

    blocks: list[str] = []
    started = False
    for marker_index, start in enumerate(section_markers):
        title = lines[start].strip()
        if title == "卷一·忠志":
            started = True
        if not started:
            continue
        end = section_markers[marker_index + 1] if marker_index + 1 < len(section_markers) else len(lines)
        current: list[str] = []
        for line in lines[start + 3 : end]:
            if line.strip():
                current.append(line.strip())
            elif current:
                block = normalize_for_match("".join(current))
                if block:
                    blocks.append(block)
                current = []
        if current:
            block = normalize_for_match("".join(current))
            if block:
                blocks.append(block)
    return blocks


def line_matches_original_block(line: str, block: str) -> bool:
    candidate = normalize_for_match(line)
    if len(candidate) < 4:
        return False

    block_prefix = block[:28]
    candidate_prefix = candidate[:28]

    if block_prefix.startswith(candidate_prefix[:6]) or candidate_prefix.startswith(block_prefix[:6]):
        return True

    ratio = SequenceMatcher(None, candidate_prefix, block_prefix).ratio()
    common = sum(1 for char in candidate_prefix[:12] if char in block_prefix)
    return ratio >= 0.42 and common >= 4


def is_noise_block(block: str) -> bool:
    text = PAGE_RE.sub("", block).strip()
    if not text:
        return True
    compact = re.sub(r"\s+", "", text)
    if compact.startswith("前集卷") or compact.startswith("續集卷"):
        return True
    if compact.startswith("#") or compact.startswith("##"):
        return True
    if compact in HEADINGS:
        return True
    if re.fullmatch(r"[一二三四五六七八九十〇○零\d]+", compact):
        return True
    return False


def is_noise_line(text: str) -> bool:
    stripped = PAGE_RE.sub("", text.strip())
    if not stripped:
        return False
    compact = re.sub(r"\s+", "", stripped)
    if compact.startswith("前集卷") or compact.startswith("續集卷"):
        return True
    if compact in HEADINGS:
        return True
    if compact.startswith("#"):
        return True
    if re.fullmatch(r"[一二三四五六七八九十〇○零\d]+", compact):
        return True
    return False


def next_significant_block_index(blocks: list[str], start: int) -> int | None:
    for index in range(start, len(blocks)):
        if not is_noise_block(blocks[index]):
            return index
    return None


def extract_transitional_annotations(lines: list[str]) -> tuple[list[str], int]:
    out_lines: list[str] = []
    in_annotation = False
    section_count = 0

    for current_index, line in enumerate(lines):
        stripped = line.strip()

        if stripped == "校勘記":
            in_annotation = True
            section_count += 1
            if out_lines and out_lines[-1] != "":
                out_lines.append("")
            out_lines.append("校勘記")
            continue

        if in_annotation:
            if is_heading_line(stripped):
                in_annotation = False
                if out_lines and out_lines[-1] != "":
                    out_lines.append("")
                continue
            if PAGE_RE.fullmatch(stripped):
                continue
            out_lines.append(line)

    while out_lines and not out_lines[-1].strip():
        out_lines.pop()

    return out_lines, section_count


def next_annotation_distance(lines: list[str], start: int) -> int | None:
    distance = 0
    for index in range(start, len(lines)):
        stripped = lines[index].strip()
        if not stripped or PAGE_RE.fullmatch(stripped) or is_noise_line(stripped):
            continue
        distance += 1
        if stripped.startswith("本條"):
            return distance
        if distance >= 8:
            return None
    return None


def looks_like_annotation_starter(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    if stripped.startswith("本條"):
        return True
    if stripped[0] in "（(〔︹":
        return True
    return "：" in stripped[:18] or ":" in stripped[:18]


def looks_like_text_line(text: str) -> bool:
    stripped = text.strip()
    if not stripped or looks_like_annotation_starter(stripped):
        return False
    if re.search(r"[（(][一二三四五六七八九十百千0-9]", stripped):
        return True
    return bool(re.match(r"^[\u4e00-\u9fff]{2,12}[一二三四五六七八九十0-9]*[，。﹁「『]", stripped))


def extract_reference_annotations(lines: list[str], original_blocks: list[str]) -> tuple[list[str], int, int]:
    out_lines: list[str] = []
    annotation_count = 0
    started = False
    in_annotation = False
    matched_blocks = 0

    for current_index, line in enumerate(lines):
        stripped = line.strip()

        if not started:
            if stripped.startswith("本條") or (original_blocks and line_matches_original_block(line, original_blocks[0])):
                started = True
            continue

        if stripped.startswith("本條"):
            in_annotation = True
            annotation_count += 1
            if out_lines and out_lines[-1] != "":
                out_lines.append("")
            out_lines.append(line)
            continue

        if in_annotation:
            distance = next_annotation_distance(lines, current_index + 1)
            if stripped and looks_like_text_line(stripped) and distance is not None:
                in_annotation = False
                matched_blocks += 1
                if out_lines and out_lines[-1] != "":
                    out_lines.append("")
                continue

            if PAGE_RE.fullmatch(stripped) or is_noise_line(stripped):
                continue
            out_lines.append(line)
            continue

        if stripped and looks_like_text_line(stripped):
            matched_blocks += 1

    while out_lines and not out_lines[-1].strip():
        out_lines.pop()

    return out_lines, annotation_count, matched_blocks


def main() -> None:
    transitional_lines = TRANSITIONAL.read_text(encoding="utf-8").splitlines()
    reference_lines = REFERENCE.read_text(encoding="utf-8").splitlines()
    original_blocks = parse_main_original_blocks(FULLTEXT)

    trans_out, trans_sections = extract_transitional_annotations(transitional_lines)
    ref_lines, ref_annotations, ref_matched = extract_reference_annotations(reference_lines, original_blocks)

    TRANSITIONAL_OUT.write_text("\n".join(trans_out) + "\n", encoding="utf-8")
    REFERENCE_OUT.write_text("\n".join(ref_lines) + "\n", encoding="utf-8")

    print(f"transitional_annotation_sections={trans_sections}")
    print(f"transitional_output_lines={len(trans_out)}")
    print(f"reference_annotation_starts={ref_annotations}")
    print(f"reference_output_lines={len(ref_lines)}")
    print(f"reference_matched_blocks={ref_matched}")
    print(f"original_blocks={len(original_blocks)}")
    print(f"wrote={TRANSITIONAL_OUT.name}")
    print(f"wrote={REFERENCE_OUT.name}")


if __name__ == "__main__":
    main()

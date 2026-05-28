#!/usr/bin/env python3
"""
Automated classification tool for 酉阳杂俎-初校.md
Usage: python3 scripts/youyang_classifier.py --input path/to/酉阳杂俎-初校.md --output-dir path/to/GLM处理/

Notes:
- This is a heuristic classifier intended to provide a first-pass categorization for narrative-structure and subject matter.
- It is not perfect; you should review and refine results manually or with refinement rules.
"""
import argparse
import re
from pathlib import Path
from collections import defaultdict, Counter

def is_volume_header(line: str) -> bool:
    return line.strip().startswith("卷") and "·" in line

def extract_volumes(lines):
    vols = []  # list of (idx, title)
    for i, line in enumerate(lines, start=1):
        if is_volume_header(line):
            vols.append((i, line.strip()))
    # build ranges
    ranges = []
    total = len(lines)
    for idx, (start, title) in enumerate(vols):
        end = (vols[idx+1][0]-1) if idx+1 < len(vols) else total
        ranges.append({"title": title, "start": start, "end": end})
    return ranges

def segment_paragraphs(lines, volumes):
    # Return list of (paragraph_text, vol_title, para_index)
    paragraphs = []
    for v in volumes:
        for i in range(v["start"], v["end"]+1):
            text = lines[i-1].strip()
            if not text:
                continue
            if is_volume_header(text):
                continue
            paragraphs.append((text, v["title"], i))
    return paragraphs

def classify_narrative(text: str) -> str:
    t = text
    # simple keyword-based heuristics for narrative structure
    if any(w in t for w in ["帝", "王", "朝", "将", "兵", "政", "官"]):
        return "历史纪事"
    if any(w in t for w in ["鬼", "神", "妖", "怪", "梦", "幻"]):
        return "志怪故事"
    if any(w in t for w in ["佛", "道", "经", "僧", "禅"]):
        # prefer Buddhist/Daoist scripture when 佛/僧 appear together with 经/典
        if any(w in t for w in ["佛", "经", "僧"]):
            return "佛道典籍"
        return "方术异闻"
    if any(w in t for w in ["术", "法", "术数", "道"]):
        return "方术异闻"
    if any(w in t for w in ["药", "医"]):
        return "博物考证"  # treat as natural/history medicinal notes
    if any(w in t for w in ["礼", "仪", "婚", "丧"]):
        return "礼仪制度"
    if any(w in t for w in ["艺", "器", "技"]):
        return "技艺杂录"
    if any(w in t for w in ["梦", " omen", " omen"]):
        return "梦兆预言"
    return "杂记"

def classify_subject(text: str) -> list:
    t = text
    subjects = []
    if any(w in t for w in ["帝王", "王", "将"]):
        subjects.append("帝王将相")
    if any(w in t for w in ["兽", "鹿", "马", "鸟", "蛇", "虎", "狼", "鱼", "鹿"]):
        subjects.append("动物")
    if any(w in t for w in ["树", "花", "草", "木", "竹", "芝"]):
        subjects.append("植物")
    if any(w in t for w in ["鬼", "神", "妖", "怪"]):
        subjects.append("鬼神妖怪")
    if any(w in t for w in ["佛", "道", "仙", "术"]):
        subjects.append("仙术道法")
    if any(w in t for w in ["僧", "佛寺", "经"]):
        subjects.append("佛事僧徒")
    if any(w in t for w in ["海", "天", "地", "山"]):
        subjects.append("天文地理")
    if any(w in t for w in ["器", "宝", "金"]):
        subjects.append("器物宝物")
    if any(w in t for w in ["药", "医"]):
        subjects.append("医术药理")
    if any(w in t for w in ["兵", "军", "战"]):
        subjects.append("军事武艺")
    if any(w in t for w in ["婚", "丧"]):
        subjects.append("婚丧礼俗")
    if any(w in t for w in ["幻", "异事", "奇人", "怪事"]):
        subjects.append("轶事传闻")
    if not subjects:
        subjects.append("掌故杂识")
    return sorted(set(subjects))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to 酉阳杂俎-初校.md")
    parser.add_argument("--output-dir", required=True, help="Directory to write output MD files")
    args = parser.parse_args()

    p = Path(args.input).resolve()
    lines = [ln.rstrip("\n") for ln in p.read_text(encoding="utf-8").splitlines()]

    volumes = extract_volumes(lines)
    # Build paragraphs with their vol
    paras = []
    for v in volumes:
        for ln in range(v["start"], v["end"]+1):
            text = lines[ln-1].strip()
            if not text:
                continue
            if is_volume_header(text):
                continue
            paras.append((ln, text, v["title"]))

    # Classification results
    narr_counts = Counter()
    subj_counts = Counter()
    cross = []  # (para_no, text, narr_class, subj_classes)
    all_lines = [p[1] for p in paras]
    narr_classes = []
    subj_classes = []
    for line_no, text, vol in paras:
        narr = classify_narrative(text)
        narr_counts[narr] += 1
        s = classify_subject(text)
        for sub in s:
            subj_counts[sub] += 1
        cross.append({"段落": line_no, "段落文本": text, "叙事结构": narr, "描写对象": s, "卷": vol})
        narr_classes.append(narr)
        subj_classes.append(s)

    outdir = Path(args.output_dir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    def write_md(fname, title, rows):
        path = outdir / fname
        lines = [f"# {title}", "", "|" + " |".join([""]+[]) + "|"]
        # simple JSON-like representation for compatibility; replace with proper Markdown if needed
        with path.open("w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            f.write("| 段落 | 内容简览 | 结构 | 描写对象 | 卷 |\n")
            f.write("|---|---|---|---|---|\n")
            for item in rows:
                seg = item.get("段落", "")
                text = item.get("段落文本", "")[0:40].replace("|"," ")
                narr = item.get("叙事结构", "")
                subs = ",".join(item.get("描写对象", []))
                vol = item.get("卷", "")
                f.write(f"| {seg} | {text} | {narr} | {subs} | {vol} |\n")

    # Write a small selection to the output; this is a starting point
    write_md("02-叙事结构分类表.md", "叙事结构分类表（初步）", [r for r in cross[:200]])
    # 03/04/05/06 files will be filled by the same mechanism in a more complete version
    # Additionally, store basic counts as JSON-like sections in the 02 file for quick inspection

    # Write basic summaries
    summary = {
        "总段落": len(paras),
        "叙事结构": narr_counts,
        "描写对象": subj_counts,
    }
    with (outdir / "02-叙事结构分类表.md").open("a", encoding="utf-8") as f:
        f.write("\n\n## 统计摘要\n\n")
        f.write("```json\n" + str(summary) + "\n" + "```\n")

    print("Classification scaffold written to:", outdir)

if __name__ == "__main__":
    main()

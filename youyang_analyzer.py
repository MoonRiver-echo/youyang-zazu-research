#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Youyang Analyzer (complete rewrite)

This script rewrites the old youyang_analyzer to a new 14-narrative + 14-theme
classification system, matching the reference CSV formats provided in the prompt.
It:
- Reads the reference CSVs to understand exact formats and headers.
- Parses an input text (volume collection) into volumes and paragraphs.
- Classifies each paragraph into a single narrative category using a chapter heuristic
  plus keyword matching.
- Performs multi-label theme classification using a keyword lexicon for the 14 broad
  theme categories (level1, level2, specific).
- Outputs six Markdown files and six CSV files with the exact column names required.
- Is fully UTF-8 and uses only the Python standard library.

Usage:
  python youyang_analyzer.py --input <path-to-input-text>
  (If no --input is given, it looks for input.txt in the same directory.)
"""

from __future__ import annotations

import csv
import os
import re
import sys
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional


# 1) Reference CSVs - exact names and expected headers (UTF-8)
REF_ROOT = r"C:\Users\lx\Desktop\前期准备\prepare"
REF_FILES = {
    "叙事明细": {
        "path": os.path.join(REF_ROOT, "酉阳杂俎-初校-叙事分类明细-据注三次修订.csv"),
        "headers": [
            "narrative_category",
            "volume_index",
            "volume_title",
            "source",
            "paragraph_id",
            "text",
        ],
    },
    "叙事统计": {
        "path": os.path.join(REF_ROOT, "酉阳杂俎-初校-叙事分类统计-据注三次修订.csv"),
        "headers": ["narrative_category", "paragraph_count", "absolute_percentage"],
    },
    "主题明细": {
        "path": os.path.join(REF_ROOT, "酉阳杂俎-初校-主题分类明细-据注三次修订.csv"),
        "headers": [
            "broad_category",
            "level1_subject",
            "level2_subject",
            "specific_subject",
            "volume_index",
            "volume_title",
            "source",
            "paragraph_id",
            "primary_subject",
            "annotation_supported",
            "original_subject",
            "text",
        ],
    },
    "主题统计": {
        "path": os.path.join(REF_ROOT, "酉阳杂俎-初校-主题分类统计-据注三次修订.csv"),
        "headers": ["broad_category", "paragraph_count", "absolute_percentage"],
    },
    "主题频次": {
        "path": os.path.join(REF_ROOT, "酉阳杂俎-初校-主题频次统计-据注三次修订.csv"),
        "headers": ["level1_subject", "level2_subject", "appearance_count"],
    },
    "重复主题": {
        "path": os.path.join(REF_ROOT, "酉阳杂俎-初校-重复主题分类-据注三次修订.csv"),
        "headers": ["volume_index", "volume_title", "source", "paragraph_id", "duplicate_broad_categories", "duplicate_specific_subjects", "text"],
    },
}


NARRATIVE_CATEGORIES = [
    "动植物谱录",
    "异闻志怪",
    "人物轶事",
    "礼俗制度",
    "佛道异闻",
    "神仙方术",
    "征兆占验",
    "异境异域",
    "知识考辨",
    "饮食医药",
    "器艺技法",
    "器物名物",
    "冥界报应",
    "天文地理",
]


HIERARCHY_THEMES: Dict[str, List[Tuple[str, str, str]]] = {}


def _build_lexicon() -> Dict[str, List[Tuple[str, str, str]]]:
    """Return a lexicon mapping broad_category -> list of (keyword, level1, level2, specific)."""
    # A pragmatic lexicon with representative keywords. This is extensible.
    lex = defaultdict(list)

    # 人物政事
    lex["人物政事"].extend([
        ("僧", "人物政事", "僧", "僧"),
        ("僧一行", "人物政事", "僧", "僧一行"),
        ("玄宗", "人物政事", "帝王", "玄宗"),
        ("高祖", "人物政事", "帝王", "高祖"),
        ("僧人", "人物政事", "僧", "僧人"),
    ])

    # 动物
    lex["动物"].extend([
        ("马", "动物", "马", "马"),
        ("龙", "动物", "龙", "龙"),
        ("虎", "动物", "虎", "虎"),
        ("蛙", "动物", "蛙", "蛙"),
    ])

    # 神怪妖魅
    lex["神怪妖魅"].extend([
        ("鬼", "神怪妖魅", "鬼", "鬼"),
        ("精", "神怪妖魅", "精", "精"),
        ("妖", "神怪妖魅", "妖", "妖"),
        ("仙", "神怪妖魅", "仙", "仙"),
    ])

    # 植物
    lex["植物"].extend([
        ("竹", "植物", "竹", "竹"),
        ("桃", "植物", "桃", "桃"),
        ("柳", "植物", "柳", "柳"),
        ("桑", "植物", "桑", "桑"),
    ])

    # 器物技艺
    lex["器物技艺"].extend([
        ("剑", "器物技艺", "兵器", "剑"),
        ("镜", "器物技艺", "器物", "镜"),
        ("鼓", "器物技艺", "器物", "鼓"),
        ("鞭", "器物技艺", "器物", "鞭"),
    ])

    # 建筑寺塔
    lex["建筑寺塔"].extend([
        ("殿", "建筑寺塔", "建筑", "殿"),
        ("宫", "建筑寺塔", "建筑", "宫"),
        ("楼", "建筑寺塔", "建筑", "楼"),
        ("塔", "建筑寺塔", "建筑", "塔"),
    ])

    # 异域物产
    lex["异域物产"].extend([
        ("波斯", "异域物产", "地域", "波斯"),
        ("昆仑", "异域物产", "地域", "昆仑"),
    ])

    # 饮食医药
    lex["饮食医药"].extend([
        ("酒", "饮食医药", "饮食", "酒"),
        ("药", "饮食医药", "药材", "药"),
        ("汤", "饮食医药", "药材", "汤"),
    ])

    # 异人方术
    lex["异人方术"].extend([
        ("术", "异人方术", "技艺", "术"),
        ("法", "异人方术", "技艺", "法"),
        ("符", "异人方术", "符咒", "符"),
    ])

    # 梦兆占验
    lex["梦兆占验"].extend([
        ("梦", "梦兆占验", "梦", "梦"),
        ("兆", "梦兆占验", "征兆", "兆"),
        ("瑞", "梦兆占验", "征兆", "瑞"),
    ])

    # 丧葬冥界
    lex["丧葬冥界"].extend([
        ("尸", "丧葬冥界", "尸体", "尸"),
        ("墓", "丧葬冥界", "墓葬", "墓"),
        ("地狱", "丧葬冥界", "冥界", "地狱"),
    ])

    # 佛道信仰
    lex["佛道信仰"].extend([
        ("佛", "佛道信仰", "信仰", "佛"),
        ("道", "佛道信仰", "信仰", "道"),
    ])

    # 天文地理
    lex["天文地理"].extend([
        ("北斗", "天文地理", "天文", "北斗"),
        ("星", "天文地理", "天文", "星"),
    ])

    # 礼俗制度
    lex["礼俗制度"].extend([
        ("婚礼", "礼俗制度", "婚俗", "婚礼"),
        ("礼", "礼俗制度", "礼仪", "礼"),
    ])

    return lex


@dataclass
class Paragraph:
    volume_index: int
    volume_title: str
    paragraph_index: int
    text: str
    narrative_category: Optional[str] = None
    themes: List[Tuple[str, str, str, str, str]] = field(default_factory=list)  # (broad, l1, l2, specific, keyword_found)

    def paragraph_id(self) -> str:
        return f"V{self.volume_index}-P{self.paragraph_index}"

    def short_text(self, maxlen: int = 120) -> str:
        t = self.text.replace("\n", " ")
        t = re.sub(r"\s+", " ", t).strip()
        if len(t) <= maxlen:
            return t
        return t[: maxlen - 3] + "..."


class YouyangAnalyzer:
    def __init__(self, input_path: str):
        self.input_path = input_path
        self.paragraphs: List[Paragraph] = []
        self.total_paragraphs = 0
        self.lexicon = _build_lexicon()
        self.narrative_by_para: List[str] = []
        # Will be loaded from reference CSVs if available
        self.ref_headers: Dict[str, List[str]] = {}

    @staticmethod
    def _make_empty_df_row(headers: List[str], fill: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        row = {h: "" for h in headers}
        if fill:
            row.update(fill)
        return row

    def load_reference_csvs(self) -> None:
        """Read the reference CSVs to understand exact formats and headers."""
        for name, info in REF_FILES.items():
            path = info["path"]
            if not os.path.exists(path):
                # If reference files are missing, continue with defaults
                continue
            with open(path, encoding="utf-8") as f:
                reader = csv.reader(f)
                try:
                    header = next(reader)
                except StopIteration:
                    header = []
                self.ref_headers[name] = header
        # After loading, print debug once (not to stdout in normal runs)
        # (Keeping this quiet to avoid polluting outputs.)

    def parse_input(self) -> None:
        if not os.path.exists(self.input_path):
            print(f"Input file not found: {self.input_path}")
            sys.exit(1)
        with open(self.input_path, encoding="utf-8") as f:
            lines = f.read().splitlines()

        # Identify volumes by headers like: 卷一·忠志
        vol_header_re = re.compile(r"^卷([一二三四五六七八九十]+)·(.+)$")
        current_vol_index = None
        current_vol_title = ""
        vol_paragraphs: List[str] = []
        para_counter = 0
        i = 0
        while i < len(lines):
            line = lines[i].rstrip()
            m = vol_header_re.match(line)
            if m:
                # flush any previous volume paragraphs
                if current_vol_index is not None:
                    self._flush_volume(current_vol_index, current_vol_title, vol_paragraphs, para_counter)
                    vol_paragraphs = []
                    para_counter = 0
                chinese_num = m.group(1)
                current_vol_index = self._map_chinese_num(chinese_num)
                current_vol_title = m.group(2).strip()
                i += 1
                continue

            # skip header like 钦定四库全书|酉阳杂俎卷一唐段成式撰写|忠志|...
            if line.strip().startswith("钦定四库全书"):
                i += 1
                continue
            # collect paragraph until a blank line or next vol header
            if line.strip() == "":
                if vol_paragraphs:
                    para_text = "\n".join(vol_paragraphs).strip()
                    para_counter += 1
                    self.paragraphs.append(
                        Paragraph(
                            volume_index=current_vol_index if current_vol_index is not None else 0,
                            volume_title=current_vol_title,
                            paragraph_index=para_counter,
                            text=para_text,
                        )
                    )
                    vol_paragraphs = []
                i += 1
                continue
            vol_paragraphs.append(line)
            i += 1

        # flush last volume
        if current_vol_index is not None and vol_paragraphs:
            self._flush_volume(current_vol_index, current_vol_title, vol_paragraphs, para_counter)

        self.total_paragraphs = len(self.paragraphs)

        # After parsing, classify narratives and themes for each paragraph
        for p in self.paragraphs:
            p.narrative_category = self.classify_narrative(p.text)
            p.themes = self.extract_themes(p.text, p.volume_index, p.volume_title, p.paragraph_index)

    def _flush_volume(self, vindex: int, vtitle: str, paras: List[str], start_index: int) -> None:
        if not paras:
            return
        local_idx = 0
        for text in paras:
            local_idx += 1
            self.paragraphs.append(Paragraph(volume_index=vindex, volume_title=vtitle, paragraph_index=local_idx, text=text))

    @staticmethod
    def _map_chinese_num(ch: str) -> int:
        table = {
            "一": 1,
            "二": 2,
            "三": 3,
            "四": 4,
            "五": 5,
            "六": 6,
            "七": 7,
            "八": 8,
            "九": 9,
            "十": 10,
        }
        return table.get(ch, 0)

    def classify_narrative(self, text: str) -> str:
        t = text
        # Flatten for heuristic matching
        s = t
        # Priority-based heuristic as per mapping in prompt
        if re.search(r"广动植[一二三四]?|肉攫", s):
            return "动植物谱录"
        if re.search(r"天咫|物革|冥迹|诺皋记上|诺皋记下|器奇|雷|诺皋记|上|下", s):
            return "异闻志怪"
        if re.search(r"忠志|事感|乐|语资|盗侠", s):
            return "人物轶事"
        if re.search(r"礼异", s):
            return "礼俗制度"
        if re.search(r"玉格|贝编", s):
            return "佛道异闻"
        if re.search(r"壶史|怪术|诡习", s):
            # keyword override for exceptions - kept simple here
            return "神仙方术"
        if re.search(r"喜兆|祸兆|梦", s):
            return "征兆占验"
        if re.search(r"境异", s):
            return "异境异域"
        if re.search(r"广知", s):
            return "知识考辨"
        if re.search(r"酒食|医|汤|药", s):
            return "饮食医药"
        if re.search(r"黥|艺绝", s):
            return "器艺技法"
        if re.search(r"物异", s):
            return "器物名物"
        if re.search(r"序", s):
            return "知识考辨"
        # default fallback
        return "知识考辨"

    def extract_themes(self, text: str, vindex: int, vtitle: str, pidx: int) -> List[Tuple[str, str, str, str, str]]:
        results: List[Tuple[str, str, str, str, str]] = []
        # For each broad category, check keywords
        for broad, entries in self.lexicon.items():
            for kw, (l1, l2, specific) in entries:
                if kw in text:
                    results.append((broad, l1, l2, specific, kw))
        # Ensure deterministic order by broad then l1
        results.sort()
        return results

    def write_outputs(self, out_dir: Optional[str] = None) -> None:
        if not self.paragraphs:
            print("No paragraphs to output.")
            return
        out_dir = out_dir or os.path.dirname(self.input_path)
        os.makedirs(out_dir, exist_ok=True)

        # Prepare data for CSVs
        narrative_rows: List[Dict[str, str]] = []
        topic_rows: List[Dict[str, str]] = []
        # Counters
        narrative_counter = Counter()
        topic_counter = Counter()
        topic_pair_counter = Counter()
        # Build per-paragraph records
        for p in self.paragraphs:
            # Narrative detail row
            narrative_rows.append({
                "narrative_category": p.narrative_category or "",
                "volume_index": str(p.volume_index),
                "volume_title": p.volume_title,
                "source": p.volume_title,
                "paragraph_id": p.paragraph_id(),
                "text": p.text,
            })
            narrative_counter[p.narrative_category] += 1
            # Theme details per paragraph
            for (broad, l1, l2, specific, kw) in p.themes:
                topic_rows.append({
                    "broad_category": broad,
                    "level1_subject": l1,
                    "level2_subject": l2,
                    "specific_subject": specific,
                    "volume_index": str(p.volume_index),
                    "volume_title": p.volume_title,
                    "source": p.volume_title,
                    "paragraph_id": p.paragraph_id(),
                    "primary_subject": l1,
                    "annotation_supported": "False",
                    "original_subject": kw,
                    "text": p.text,
                })
                topic_counter[(broad, l1, l2, specific)] += 1
                topic_pair_counter[(l1, l2)] += 1

        total_paragraphs = len(self.paragraphs)
        # 叙事分类明细.csv
        narrative_csv_path = os.path.join(out_dir, "叙事分类明细.csv")
        with open(narrative_csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "narrative_category",
                "volume_index",
                "volume_title",
                "source",
                "paragraph_id",
                "text",
            ])
            writer.writeheader()
            for row in narrative_rows:
                writer.writerow(row)

        narrative_stat_path = os.path.join(out_dir, "叙事分类统计.csv")
        with open(narrative_stat_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["narrative_category", "paragraph_count", "absolute_percentage"])
            for cat in NARRATIVE_CATEGORIES:
                count = narrative_counter.get(cat, 0)
                pct = (count / total_paragraphs * 100) if total_paragraphs else 0
                writer.writerow([cat, count, f"{pct:.4f}"])

        # 主题明细.csv
        topic_csv_path = os.path.join(out_dir, "主题分类明细.csv")
        with open(topic_csv_path, "w", encoding="utf-8", newline="") as f:
            if not topic_rows:
                # write header only
                writer = csv.DictWriter(f, fieldnames=[
                    "broad_category",
                    "level1_subject",
                    "level2_subject",
                    "specific_subject",
                    "volume_index",
                    "volume_title",
                    "source",
                    "paragraph_id",
                    "primary_subject",
                    "annotation_supported",
                    "original_subject",
                    "text",
                ])
                writer.writeheader()
            else:
                writer = csv.DictWriter(f, fieldnames=[
                    "broad_category",
                    "level1_subject",
                    "level2_subject",
                    "specific_subject",
                    "volume_index",
                    "volume_title",
                    "source",
                    "paragraph_id",
                    "primary_subject",
                    "annotation_supported",
                    "original_subject",
                    "text",
                ])
                writer.writeheader()
                for row in topic_rows:
                    writer.writerow(row)

        topic_stat_path = os.path.join(out_dir, "主题分类统计.csv")
        with open(topic_stat_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["broad_category", "paragraph_count", "absolute_percentage"])
            for broad in sorted({r[0] for r in topic_counter}):
                count = sum(n for (bb, ll1, ll2, sp), n in topic_counter.items() if bb == broad)
                pct = (count / total_paragraphs * 100) if total_paragraphs else 0
                writer.writerow([broad, count, f"{pct:.4f}"])

        # 主题频次统计.csv
        freq_path = os.path.join(out_dir, "主题频次统计.csv")
        with open(freq_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["level1_subject", "level2_subject", "appearance_count"])
            for (l1, l2), cnt in sorted(
                topic_pair_counter.items(), key=lambda x: (x[0][0], x[0][1])
            ):
                writer.writerow([l1, l2, cnt])

        # 重复主题分类.csv
        dup_path = os.path.join(out_dir, "重复主题分类.csv")
        with open(dup_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["volume_index", "volume_title", "source", "paragraph_id", "duplicate_broad_categories", "duplicate_specific_subjects", "text"])
            for p in self.paragraphs:
                dup_broad = []
                dup_specs = []
                for (broad, l1, l2, sp, kw) in p.themes:
                    dup_broad.append(broad)
                    dup_specs.append(f"{l1}:{l2}:{sp}")
                writer.writerow([
                    str(p.volume_index), p.volume_title, p.volume_title, p.paragraph_id(), ",".join(sorted(set(dup_broad))), ",".join(dup_specs), p.text
                ])

        # Write Markdown reports as well (6 files)
        self._write_markdown_reports(out_dir)

        print(f"输出完成：{out_dir}")

    def run(self) -> None:
        self.load_reference_csvs()
        self.parse_input()
        self.write_outputs()

    def _write_markdown_reports(self, out_dir: str) -> None:
        """Produce 6 Markdown files describing the results."""
        md1 = os.path.join(out_dir, "01-卷目分段.md")
        md2 = os.path.join(out_dir, "02-叙事结构分类表.md")
        md3 = os.path.join(out_dir, "03-描写对象分类表.md")
        md4 = os.path.join(out_dir, "04-交叉分类表.md")
        md5 = os.path.join(out_dir, "05-描写对象频次表.md")
        md6 = os.path.join(out_dir, "06-同类描写对象汇总.md")

        # 01-卷目分段.md
        with open(md1, "w", encoding="utf-8") as f:
            f.write("# 01-卷目分段\n\n")
            for p in self.paragraphs:
                f.write(f"- {p.paragraph_id()} | {p.volume_title} | {p.short_text()}\n")

        # 02-叙事结构分类表.md
        with open(md2, "w", encoding="utf-8") as f:
            f.write("# 02-叙事结构分类表\n\n")
            f.write("| Paragraph_ID | Volume | Narrative_Category | Text_snippet |\n")
            f.write("|---|---|---|---|\n")
            for p in self.paragraphs:
                text_snip = p.short_text(80)
                f.write(f"| {p.paragraph_id()} | {p.volume_title} | {p.narrative_category} | {text_snip} |\n")

        # 03-描写对象分类表.md
        with open(md3, "w", encoding="utf-8") as f:
            f.write("# 03-描写对象分类表\n\n")
            f.write("| Paragraph_ID | Broad_Category | Level1 | Level2 | Specific | Text_snippet |\n")
            f.write("|---|---|---|---|---|---|\n")
            for p in self.paragraphs:
                if not p.themes:
                    f.write(f"| {p.paragraph_id()} | - | - | - | - | {p.short_text(60)} |\n")
                else:
                    for broad, l1, l2, sp, kw in p.themes:
                        f.write(f"| {p.paragraph_id()} | {broad} | {l1} | {l2} | {sp} | {p.short_text(60)} |\n")

        # 04-交叉分类表.md
        with open(md4, "w", encoding="utf-8") as f:
            f.write("# 04-交叉分类表\n\n")
            f.write("Paragraph_ID | Narrative_Category | Theme_Broad | Theme_L1 | Theme_L2 | Theme_Specific | Text_snippet\n")
            f.write("|---|---|---|---|---|---|---|\n")
            for p in self.paragraphs:
                if not p.themes:
                    f.write(f"| {p.paragraph_id()} | {p.narrative_category} | - | - | - | - | {p.short_text(60)} |\n")
                else:
                    for broad, l1, l2, sp, kw in p.themes:
                        f.write(f"| {p.paragraph_id()} | {p.narrative_category} | {broad} | {l1} | {l2} | {sp} | {p.short_text(60)} |\n")

        # 05-描写对象频次表.md
        with open(md5, "w", encoding="utf-8") as f:
            f.write("# 05-描写对象频次表\n\n")
            f.write("| Level1_Subject | Level2_Subject | Appearance_Count |\n")
            f.write("|---|---|---|\n")
            # Count by (level1, level2)
            counts = Counter()
            for p in self.paragraphs:
                for broad, l1, l2, sp, kw in p.themes:
                    counts[(l1, l2)] += 1
            for (l1, l2), cnt in sorted(counts.items(), key=lambda x: (x[0], x[1])):
                f.write(f"| {l1} | {l2} | {cnt} |\n")

        # 06-同类描写对象汇总.md
        with open(md6, "w", encoding="utf-8") as f:
            f.write("# 06-同类描写对象汇总\n\n")
            f.write("| Broad_Category | Count |\n")
            f.write("|---|---|\n")
            broad_counts = Counter()
            for p in self.paragraphs:
                for broad, _l1, _l2, _sp, _kw in p.themes:
                    broad_counts[broad] += 1
            for broad, cnt in sorted(broad_counts.items(), key=lambda x: x[0]):
                f.write(f"| {broad} | {cnt} |\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Youyang Analyzer - classification and export to MD/CSV")
    parser.add_argument("--input", help="Path to input text containing volumes", default=None)
    parser.add_argument("--out", help="Output directory", default=None)
    args = parser.parse_args()

    input_path = args.input
    if input_path is None:
        # Fallback to data/input.txt relative to this script
        cand = os.path.join(os.path.dirname(__file__), "input.txt")
        if os.path.exists(cand):
            input_path = cand
        else:
            print("请提供 --input 参数或在脚本目录放置 input.txt 作为输入。")
            sys.exit(1)

    analyzer = YouyangAnalyzer(input_path)
    analyzer.run()

    # Outputs to same dir as input unless --out overrides
    out_dir = args.out or os.path.dirname(input_path)
    analyzer.write_outputs(out_dir)


if __name__ == "__main__":
    main()

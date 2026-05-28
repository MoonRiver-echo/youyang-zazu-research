from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
import csv
import re

from opencc import OpenCC


BASE = Path(r"C:\Users\lx\Desktop\前期准备\prepare")
TARGET = BASE / "酉阳杂俎-初校.md"

cc_t2s = OpenCC("t2s")


@dataclass
class Paragraph:
    paragraph_id: str
    volume_index: int
    volume_title: str
    section_name: str
    paragraph_index_in_volume: int
    text: str


def normalize(text: str) -> str:
    return cc_t2s.convert(text)


def parse_paragraphs(path: Path) -> list[Paragraph]:
    lines = path.read_text(encoding="utf-8").splitlines()
    paragraphs: list[Paragraph] = []
    current_volume = ""
    current_volume_index = 0
    para_index = 0
    buffer: list[str] = []

    def flush() -> None:
        nonlocal para_index, buffer
        if not buffer or not current_volume:
            buffer = []
            return
        para_index += 1
        text = "".join(buffer).strip()
        paragraphs.append(
            Paragraph(
                paragraph_id=f"V{current_volume_index:02d}-P{para_index:03d}",
                volume_index=current_volume_index,
                volume_title=current_volume,
                section_name=current_volume.split("·", 1)[1] if "·" in current_volume else current_volume,
                paragraph_index_in_volume=para_index,
                text=text,
            )
        )
        buffer = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("卷"):
            flush()
            current_volume = stripped
            current_volume_index += 1
            para_index = 0
            continue
        if not current_volume:
            continue
        if stripped:
            buffer.append(stripped)
        else:
            flush()
    flush()
    return paragraphs


NARRATIVE_BY_SECTION = {
    "忠志": "人物轶事",
    "礼异": "礼俗制度",
    "天咫": "天文地理",
    "玉格": "神仙方术",
    "壶史": "神仙方术",
    "贝编": "佛道异闻",
    "境异": "异境异域",
    "喜兆": "征兆占验",
    "祸兆": "征兆占验",
    "物革": "器物名物",
    "诡习": "礼俗制度",
    "怪术": "神仙方术",
    "艺绝": "器艺技法",
    "器奇": "器艺技法",
    "乐": "器艺技法",
    "酒食": "饮食医药",
    "医": "饮食医药",
    "黥": "器艺技法",
    "雷": "征兆占验",
    "梦": "征兆占验",
    "事感": "人物轶事",
    "盗侠": "人物轶事",
    "物异": "异闻志怪",
    "广知": "知识考辨",
    "语资": "知识考辨",
    "冥迹": "冥界报应",
    "尸穸": "丧葬制度",
    "诺皋记上": "异闻志怪",
    "诺皋记下": "异闻志怪",
    "广动植之一": "动植物谱录",
    "广动植之二": "动植物谱录",
    "广动植之三": "动植物谱录",
    "广动植之四": "动植物谱录",
    "羽篇": "动植物谱录",
    "毛篇": "动植物谱录",
    "鳞介篇": "动植物谱录",
    "虫篇": "动植物谱录",
    "木篇": "动植物谱录",
    "草篇": "动植物谱录",
    "肉攫部": "动植物谱录",
    "支诺皋上": "异闻志怪",
    "支诺皋中": "异闻志怪",
    "支诺皋下": "异闻志怪",
    "贬误": "知识考辨",
    "寺塔记上": "建筑寺塔",
    "寺塔记下": "建筑寺塔",
    "金刚经鸠异": "佛道异闻",
    "支动": "动植物谱录",
    "支植上": "动植物谱录",
    "支植下": "动植物谱录",
}


SUBJECT_PATTERNS = [
    ("龙脑", "植物"),
    ("白鹊", "动物"),
    ("雌雉", "动物"),
    ("雕", "动物"),
    ("鸢", "动物"),
    ("马", "动物"),
    ("鱼", "动物"),
    ("龙", "神怪妖魅"),
    ("蜗", "动物"),
    ("猿", "动物"),
    ("鹤", "动物"),
    ("虎", "动物"),
    ("蛇", "动物"),
    ("兔", "动物"),
    ("猪", "动物"),
    ("龟", "动物"),
    ("凤", "动物"),
    ("麒麟", "动物"),
    ("虾蟆", "动物"),
    ("虫", "动物"),
    ("桂", "植物"),
    ("槐", "植物"),
    ("柳", "植物"),
    ("桃", "植物"),
    ("李", "植物"),
    ("桑", "植物"),
    ("竹", "植物"),
    ("木瓜", "植物"),
    ("木兰", "植物"),
    ("槟榔", "植物"),
    ("芝", "植物"),
    ("草", "植物"),
    ("树", "植物"),
    ("花", "植物"),
    ("鬼", "神怪妖魅"),
    ("魅", "神怪妖魅"),
    ("妖", "神怪妖魅"),
    ("怪", "神怪妖魅"),
    ("精", "神怪妖魅"),
    ("狐", "神怪妖魅"),
    ("神", "神怪妖魅"),
    ("西王母", "神怪妖魅"),
    ("女娲", "神怪妖魅"),
    ("河伯", "神怪妖魅"),
    ("僧", "异人方术"),
    ("道士", "异人方术"),
    ("真人", "异人方术"),
    ("仙", "异人方术"),
    ("法师", "异人方术"),
    ("术", "异人方术"),
    ("佛", "佛道信仰"),
    ("经", "佛道信仰"),
    ("寺", "建筑寺塔"),
    ("塔", "建筑寺塔"),
    ("殿", "建筑寺塔"),
    ("宫", "建筑寺塔"),
    ("楼", "建筑寺塔"),
    ("观", "建筑寺塔"),
    ("苑", "建筑寺塔"),
    ("门", "建筑寺塔"),
    ("镜", "器物技艺"),
    ("剑", "器物技艺"),
    ("弓", "器物技艺"),
    ("箭", "器物技艺"),
    ("鞭", "器物技艺"),
    ("盘", "器物技艺"),
    ("瓶", "器物技艺"),
    ("屏风", "器物技艺"),
    ("钟", "器物技艺"),
    ("鼓", "器物技艺"),
    ("琵琶", "器物技艺"),
    ("琴", "器物技艺"),
    ("酒", "饮食医药"),
    ("食", "饮食医药"),
    ("药", "饮食医药"),
    ("汤", "饮食医药"),
    ("臛", "饮食医药"),
    ("口脂", "饮食医药"),
    ("梦", "梦兆占验"),
    ("兆", "梦兆占验"),
    ("瑞", "梦兆占验"),
    ("庆云", "梦兆占验"),
    ("墓", "丧葬冥界"),
    ("坟", "丧葬冥界"),
    ("葬", "丧葬冥界"),
    ("尸", "丧葬冥界"),
    ("地狱", "丧葬冥界"),
    ("冥", "丧葬冥界"),
    ("波斯", "异域物产"),
    ("交趾", "异域物产"),
    ("昆仑", "异域物产"),
    ("扶桑", "异域物产"),
]

GENERIC_SUBJECTS = {
    "未判定",
    "国",
    "食",
    "经",
    "神",
    "怪",
    "门",
    "花",
    "树",
    "草",
    "又言",
}


SECTION_BROAD_DEFAULTS = {
    "礼异": {"礼俗制度"},
    "诡习": {"礼俗制度"},
    "天咫": {"天文地理"},
    "玉格": {"佛道信仰", "异人方术"},
    "壶史": {"异人方术"},
    "贝编": {"佛道信仰"},
    "境异": {"异域物产", "天文地理"},
    "喜兆": {"梦兆占验"},
    "祸兆": {"梦兆占验"},
    "怪术": {"异人方术"},
    "艺绝": {"器物技艺"},
    "器奇": {"器物技艺"},
    "乐": {"器物技艺"},
    "酒食": {"饮食医药"},
    "医": {"饮食医药"},
    "雷": {"梦兆占验", "天文地理"},
    "梦": {"梦兆占验"},
    "物异": {"神怪妖魅"},
    "广知": {"知识名物"},
    "语资": {"知识名物"},
    "冥迹": {"丧葬冥界", "神怪妖魅"},
    "尸穸": {"丧葬冥界"},
    "诺皋记上": {"神怪妖魅"},
    "诺皋记下": {"神怪妖魅"},
    "支诺皋上": {"神怪妖魅"},
    "支诺皋中": {"神怪妖魅"},
    "支诺皋下": {"神怪妖魅"},
    "寺塔记上": {"建筑寺塔", "佛道信仰"},
    "寺塔记下": {"建筑寺塔", "佛道信仰"},
    "金刚经鸠异": {"佛道信仰"},
    "支动": {"动物"},
    "支植上": {"植物"},
    "支植下": {"植物"},
    "羽篇": {"动物"},
    "毛篇": {"动物"},
    "鳞介篇": {"动物"},
    "虫篇": {"动物"},
    "木篇": {"植物"},
    "草篇": {"植物"},
    "肉攫部": {"动物"},
    "广动植之一": {"动物", "植物"},
    "广动植之二": {"动物", "植物"},
    "广动植之三": {"动物", "植物"},
    "广动植之四": {"动物", "植物"},
}


PERSON_RE = re.compile(r"^[\u4e00-\u9fff]{1,6}")
TIME_PREFIX_RE = re.compile(r"^(贞观中|天宝末|长庆中|太和中|永贞年|西汉|近代|秦汉以来|立春日|寒食日|三月三日|腊日|上尝梦曰|旧言|代宗即位日)")


def extract_primary_subject(text: str) -> str:
    norm = normalize(text)
    norm = TIME_PREFIX_RE.sub("", norm)
    first = re.split(r"[。；：，]", norm, maxsplit=1)[0]
    first = re.sub(r"^(钦定四库全书\|酉阳杂俎卷[^|]+\|[^|]+\|)", "", first)
    first = re.sub(r"^(又|有|其|上|乃|因|皆|常)", "", first)
    for verb in ["尝", "初", "少", "见", "为", "曰", "言", "献", "贡", "梦", "生", "出", "有", "在", "即", "将", "主", "善"]:
        if verb in first:
            first = first.split(verb, 1)[0]
            break
    first = first.strip("「」『』（）()[]【】 ")
    if not first:
        m = PERSON_RE.match(norm)
        return m.group(0) if m else "未判定"
    primary = first[:12]
    if primary in GENERIC_SUBJECTS:
        m = PERSON_RE.match(norm)
        return m.group(0) if m else "未判定"
    return primary


def infer_subject_broad_from_primary(primary: str, section: str) -> str:
    if primary.endswith(("草", "木", "树", "花", "芝", "竹", "藤", "李", "桃", "柳", "槐", "桂")):
        return "植物"
    if primary.endswith(("马", "鱼", "鸟", "虫", "龙", "蛇", "虎", "兔", "猿", "鹤", "龟", "凤")):
        return "动物"
    if any(x in primary for x in ["僧", "道士", "真人", "仙", "法师", "天师", "先生"]):
        return "异人方术"
    if any(x in primary for x in ["寺", "塔", "殿", "宫", "楼", "观", "苑", "门"]):
        return "建筑寺塔"
    if any(x in primary for x in ["鬼", "神", "妖", "怪", "魅", "狐"]):
        return "神怪妖魅"
    if section in {"忠志", "事感", "盗侠"}:
        return "人物政事"
    if section in {"礼异", "诡习"}:
        return "礼俗制度"
    if section in {"天咫", "境异"}:
        return "天文地理"
    if section in {"酒食", "医"}:
        return "饮食医药"
    if section in {"艺绝", "器奇", "乐", "黥", "物革"}:
        return "器物技艺"
    if section in {"冥迹", "尸穸"}:
        return "丧葬冥界"
    if section in {"玉格", "壶史", "怪术"}:
        return "异人方术"
    if section in {"贝编", "金刚经鸠异"}:
        return "佛道信仰"
    return "人物政事"


def classify_narrative(paragraph: Paragraph) -> str:
    return NARRATIVE_BY_SECTION.get(paragraph.section_name, "人物轶事")


def classify_subjects(paragraph: Paragraph) -> tuple[list[tuple[str, str]], str]:
    text = normalize(paragraph.text)
    matches: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for subject, broad in SUBJECT_PATTERNS:
        if subject in text:
            item = (broad, subject)
            if item not in seen:
                matches.append(item)
                seen.add(item)

    defaults = SECTION_BROAD_DEFAULTS.get(paragraph.section_name, set())
    primary = extract_primary_subject(paragraph.text)
    if not matches:
        broad = infer_subject_broad_from_primary(primary, paragraph.section_name)
        matches.append((broad, primary))
    else:
        if primary and primary != "未判定":
            inferred = infer_subject_broad_from_primary(primary, paragraph.section_name)
            item = (inferred, primary)
            if item not in seen:
                matches.append(item)
                seen.add(item)

    for broad in defaults:
        if not any(existing_broad == broad for existing_broad, _ in matches):
            matches.append((broad, extract_primary_subject(paragraph.text)))

    return matches, primary


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def percent(count: int, total: int) -> str:
    return f"{(count / total * 100):.2f}%"


def main() -> None:
    paragraphs = parse_paragraphs(TARGET)
    total = len(paragraphs)

    narrative_rows: list[dict] = []
    subject_rows: list[dict] = []
    duplicate_rows: list[dict] = []
    subject_frequency: Counter[str] = Counter()
    narrative_counter: Counter[str] = Counter()
    subject_counter: Counter[str] = Counter()

    for p in paragraphs:
        narrative = classify_narrative(p)
        narrative_counter[narrative] += 1
        source = f"{p.volume_title}-{p.paragraph_index_in_volume}"
        narrative_rows.append(
            {
                "narrative_category": narrative,
                "volume_index": p.volume_index,
                "volume_title": p.volume_title,
                "source": source,
                "paragraph_id": p.paragraph_id,
                "text": p.text,
            }
        )

        subject_matches, primary_subject = classify_subjects(p)
        broad_seen: set[str] = set()
        for broad, subject in subject_matches:
            if subject in GENERIC_SUBJECTS:
                continue
            subject_rows.append(
                {
                    "broad_category": broad,
                    "specific_subject": subject,
                    "volume_index": p.volume_index,
                    "volume_title": p.volume_title,
                    "source": source,
                    "paragraph_id": p.paragraph_id,
                    "primary_subject": primary_subject,
                    "text": p.text,
                }
            )
            broad_seen.add(broad)
            subject_frequency[subject] += 1

        if not broad_seen:
            broad = infer_subject_broad_from_primary(primary_subject, p.section_name)
            subject_rows.append(
                {
                    "broad_category": broad,
                    "specific_subject": primary_subject,
                    "volume_index": p.volume_index,
                    "volume_title": p.volume_title,
                    "source": source,
                    "paragraph_id": p.paragraph_id,
                    "primary_subject": primary_subject,
                    "text": p.text,
                }
            )
            broad_seen.add(broad)
            subject_frequency[primary_subject] += 1

        for broad in broad_seen:
            subject_counter[broad] += 1

        if len(broad_seen) > 1:
            duplicate_rows.append(
                {
                    "volume_index": p.volume_index,
                    "volume_title": p.volume_title,
                    "source": source,
                    "paragraph_id": p.paragraph_id,
                    "duplicate_broad_categories": " | ".join(sorted(broad_seen)),
                    "duplicate_specific_subjects": " | ".join(sorted({subject for _, subject in subject_matches})),
                    "text": p.text,
                }
            )

    narrative_rows.sort(key=lambda x: (x["narrative_category"], x["volume_index"], x["source"]))
    subject_rows.sort(key=lambda x: (x["broad_category"], x["specific_subject"], x["volume_index"], x["source"]))
    duplicate_rows.sort(key=lambda x: (x["volume_index"], x["source"]))

    narrative_stats_rows = [
        {
            "narrative_category": category,
            "paragraph_count": count,
            "absolute_percentage": percent(count, total),
        }
        for category, count in sorted(narrative_counter.items(), key=lambda item: (-item[1], item[0]))
    ]

    subject_stats_rows = [
        {
            "broad_category": category,
            "paragraph_count": count,
            "absolute_percentage": percent(count, total),
        }
        for category, count in sorted(subject_counter.items(), key=lambda item: (-item[1], item[0]))
    ]

    subject_frequency_rows = [
        {
            "specific_subject": subject,
            "appearance_count": count,
        }
        for subject, count in sorted(subject_frequency.items(), key=lambda item: (-item[1], item[0]))
    ]

    write_csv(
        BASE / "酉阳杂俎-初校-叙事分类明细.csv",
        narrative_rows,
        ["narrative_category", "volume_index", "volume_title", "source", "paragraph_id", "text"],
    )
    write_csv(
        BASE / "酉阳杂俎-初校-叙事分类统计.csv",
        narrative_stats_rows,
        ["narrative_category", "paragraph_count", "absolute_percentage"],
    )
    write_csv(
        BASE / "酉阳杂俎-初校-主题分类明细.csv",
        subject_rows,
        ["broad_category", "specific_subject", "volume_index", "volume_title", "source", "paragraph_id", "primary_subject", "text"],
    )
    write_csv(
        BASE / "酉阳杂俎-初校-主题分类统计.csv",
        subject_stats_rows,
        ["broad_category", "paragraph_count", "absolute_percentage"],
    )
    write_csv(
        BASE / "酉阳杂俎-初校-重复主题分类.csv",
        duplicate_rows,
        ["volume_index", "volume_title", "source", "paragraph_id", "duplicate_broad_categories", "duplicate_specific_subjects", "text"],
    )
    write_csv(
        BASE / "酉阳杂俎-初校-主题频次统计.csv",
        subject_frequency_rows,
        ["specific_subject", "appearance_count"],
    )

    print(f"paragraphs={total}")
    print(f"narrative_categories={len(narrative_counter)}")
    print(f"subject_broad_categories={len(subject_counter)}")
    print(f"duplicate_subject_paragraphs={len(duplicate_rows)}")


if __name__ == "__main__":
    main()

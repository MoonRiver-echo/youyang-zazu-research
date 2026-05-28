from __future__ import annotations

import csv
import re
from pathlib import Path


BASE = Path(r"C:\Users\lx\Desktop\前期准备\prepare")
COUNTRY_ROWS = BASE / "酉阳杂俎-初校-国别条目归类-据注三次修订.csv"
ANNOTATIONS = BASE / "酉阳杂俎-许逸民校-2015-annotations.txt"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def cn_int(text: str) -> int | None:
    text = text.strip()
    if not text:
        return None
    if text.isdigit():
        return int(text)
    digits = {"零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
    units = {"十": 10, "百": 100, "千": 1000, "万": 10000}
    total = 0
    section = 0
    number = 0
    for ch in text:
        if ch in digits:
            number = digits[ch]
        elif ch in units:
            unit = units[ch]
            if unit == 10000:
                section = (section + (number or 0)) * unit
                total += section
                section = 0
            else:
                section += (number or 1) * unit
            number = 0
    return total + section + number


COUNTRY_RENAMES = {
    "波斯": "波斯国",
    "拂林": "拂林国",
    "真腊": "真腊国",
    "婆利": "婆利国",
    "骨利干": "骨利干国",
    "古龟兹国": "龟兹国",
    "天竺": "天竺",
    "交趾": "交趾",
    "新罗": "新罗",
    "康国": "康国",
    "安息": "安息国",
    "大食": "大食",
    "昆仑": "昆仑",
    "乌仗那国": "乌仗那国",
    "百济": "百济",
    "高句丽": "高句丽",
    "摩伽陀国": "摩伽陀国",
    "婆弥烂国": "婆弥烂国",
    "焉耆国": "焉耆国",
    "于阗国": "于阗国",
    "阗国": "于阗国",
    "那揭罗曷国": "那揭罗曷国",
    "因墀国": "因墀国",
    "俱德建国": "俱德建国",
    "俱振提国": "俱振提国",
    "俱位国": "俱位国",
    "东迦毕诚国": "东迦毕诚国",
    "仍建国": "仍建国",
    "伽古罗国": "伽古罗国",
    "北天健驮罗国": "北天健驮罗国",
    "北虏之先索国": "先索国",
    "悬渡国": "悬渡国",
    "憔侥国": "憔侥国",
    "扶支国": "扶支国",
    "拘夷国": "拘夷国",
    "拨拔力国": "拨拔力国",
    "昆吾国": "昆吾国",
    "昆明国": "昆明国",
    "梵那衍国": "梵那衍国",
    "犬国": "犬封国",
    "私诃条国": "私诃条国",
    "苏都瑟匿国": "苏都瑟匿国",
    "苏都识匿国": "苏都识匿国",
    "莱子国": "莱子国",
    "诃伽国": "诃伽国",
    "赡披国": "赡披国",
    "长须国": "长须国",
    "吐蕃": "吐蕃",
    "悉怛国": "悉怛国",
    "婆国": "阇婆国",
}

DROP_LABELS = {
    "延陵昔聘上国",
    "斯商人欲入此国",
    "此国",
    "其国",
    "我国",
    "溉一国",
    "经久复归招国",
    "裆巾衣国",
    "西南二千里有国",
    "言婆罗门国",
    "讨袭诸国",
    "谷伯绥之国",
    "象马兵南讨其国",
    "那国",
    "一万二城大国",
}

COUNTRY_META = {
    "波斯国": {
        "modern_reference": "今伊朗及其周边",
        "tang_note": "唐人所称波斯国，地在京师西万五千三百里，东接吐火罗、康国，西北拒拂林。",
        "map_region": "西域极西",
    },
    "拂林国": {
        "modern_reference": "东地中海及拜占庭区域",
        "tang_note": "唐代西海之上大秦故地，东南与波斯接。",
        "map_region": "西海以西",
    },
    "交趾": {
        "modern_reference": "今越南河内附近",
        "tang_note": "唐安南都护府交趾旧地。",
        "map_region": "岭南以南",
    },
    "骨利干国": {
        "modern_reference": "今贝加尔湖一带",
        "tang_note": "铁勒诸部之一，在翰海之北。",
        "map_region": "极北",
    },
    "高句丽": {
        "modern_reference": "今朝鲜半岛北部及辽东部分地区",
        "tang_note": "东夷强国，在辽东以东。",
        "map_region": "东北",
    },
    "百济": {
        "modern_reference": "今朝鲜半岛西南部",
        "tang_note": "朝鲜半岛古国，与高句丽、新罗鼎立。",
        "map_region": "东北",
    },
    "新罗": {
        "modern_reference": "今朝鲜半岛东南部",
        "tang_note": "唐代朝鲜半岛古国。",
        "map_region": "东北海东",
    },
    "龟兹国": {
        "modern_reference": "今新疆库车",
        "tang_note": "西域旧国，东去长安七千五百里。",
        "map_region": "西域",
    },
    "焉耆国": {
        "modern_reference": "今新疆焉耆",
        "tang_note": "西域旧国，近龟兹。",
        "map_region": "西域",
    },
    "于阗国": {
        "modern_reference": "今新疆和田",
        "tang_note": "西域南道重国。",
        "map_region": "西域南道",
    },
    "昆仑": {
        "modern_reference": "唐宋文献中多指南海诸国或香料群岛，亦有泛称黑身南海人之义",
        "tang_note": "所指多义，此表取海外南方诸国之通称。",
        "map_region": "南海诸国",
    },
    "康国": {
        "modern_reference": "今撒马尔罕附近",
        "tang_note": "即颯秣建，唐西域重国。",
        "map_region": "西域中亚",
    },
    "安息国": {
        "modern_reference": "古伊朗高原西部地区",
        "tang_note": "西域大国名，唐人常作远西强国称。",
        "map_region": "西域极西",
    },
    "天竺": {
        "modern_reference": "今印度次大陆诸国总称",
        "tang_note": "唐人常以五天竺为印度总称。",
        "map_region": "西南天竺",
    },
    "摩伽陀国": {
        "modern_reference": "今印度比哈尔一带",
        "tang_note": "佛教圣地之一，摩诃菩提寺所在。",
        "map_region": "中天竺",
    },
    "大食": {
        "modern_reference": "阿拉伯帝国及其势力范围",
        "tang_note": "唐代西海强国。",
        "map_region": "西海之南",
    },
    "真腊国": {
        "modern_reference": "今柬埔寨地区",
        "tang_note": "南海大国，近交州以西南。",
        "map_region": "南海西南",
    },
    "婆利国": {
        "modern_reference": "今印尼巴厘岛附近或广义南海岛屿",
        "tang_note": "南海国名，龙脑香产地之一。",
        "map_region": "南海群岛",
    },
    "吐蕃": {
        "modern_reference": "今青藏高原及其周边",
        "tang_note": "唐西南强邻。",
        "map_region": "西南高原",
    },
}


MANUAL_RELATIONS = [
    {
        "canonical_country": "波斯国",
        "related_place": "京师",
        "relation_type": "距京师",
        "direction": "西",
        "distance_li": "15300",
        "evidence_source": "注释",
        "note": "旧唐书西戎波斯国传",
    },
    {
        "canonical_country": "波斯国",
        "related_place": "吐火罗、康国",
        "relation_type": "相接",
        "direction": "东",
        "distance_li": "",
        "evidence_source": "注释",
        "note": "东与吐火罗、康国接",
    },
    {
        "canonical_country": "波斯国",
        "related_place": "拂林国",
        "relation_type": "相拒",
        "direction": "西北",
        "distance_li": "",
        "evidence_source": "注释",
        "note": "西北拒拂林",
    },
    {
        "canonical_country": "骨利干国",
        "related_place": "翰海",
        "relation_type": "方位",
        "direction": "北",
        "distance_li": "",
        "evidence_source": "注释",
        "note": "处翰海北，近贝加尔湖",
    },
    {
        "canonical_country": "龟兹国",
        "related_place": "京师",
        "relation_type": "距京师",
        "direction": "西",
        "distance_li": "7500",
        "evidence_source": "注释",
        "note": "旧唐书西戎龟兹国传",
    },
    {
        "canonical_country": "婆弥烂国",
        "related_place": "京师",
        "relation_type": "距京师",
        "direction": "",
        "distance_li": "25550",
        "evidence_source": "正文",
        "note": "原文直述去京师二万五千五百五十里",
    },
    {
        "canonical_country": "拨拔力国",
        "related_place": "海",
        "relation_type": "海中位置",
        "direction": "西南",
        "distance_li": "",
        "evidence_source": "正文",
        "note": "在西南海中",
    },
    {
        "canonical_country": "交趾",
        "related_place": "交州、安南都护府",
        "relation_type": "行政归属",
        "direction": "",
        "distance_li": "",
        "evidence_source": "注释",
        "note": "唐为安南都护府辖地",
    },
    {
        "canonical_country": "高句丽",
        "related_place": "朝鲜半岛北部",
        "relation_type": "现代参照",
        "direction": "东北",
        "distance_li": "",
        "evidence_source": "注释",
        "note": "在今朝鲜半岛",
    },
    {
        "canonical_country": "百济",
        "related_place": "朝鲜半岛西南部",
        "relation_type": "现代参照",
        "direction": "东北",
        "distance_li": "",
        "evidence_source": "注释",
        "note": "在今朝鲜半岛",
    },
    {
        "canonical_country": "新罗",
        "related_place": "朝鲜半岛东南部",
        "relation_type": "现代参照",
        "direction": "东北",
        "distance_li": "",
        "evidence_source": "注释",
        "note": "在今朝鲜半岛",
    },
    {
        "canonical_country": "悬渡国",
        "related_place": "乌耗西",
        "relation_type": "方位",
        "direction": "",
        "distance_li": "",
        "evidence_source": "正文",
        "note": "乌耗西有悬渡国",
    },
    {
        "canonical_country": "因墀国",
        "related_place": "南方",
        "relation_type": "使者去向",
        "direction": "南",
        "distance_li": "",
        "evidence_source": "正文",
        "note": "汉武时使南方",
    },
    {
        "canonical_country": "大食",
        "related_place": "某国",
        "relation_type": "方位",
        "direction": "西南",
        "distance_li": "2000",
        "evidence_source": "正文",
        "note": "大食西南二千里有国",
    },
]


RELATION_PATTERNS = [
    (
        re.compile(r"(?P<country>[\u4e00-\u9fff]{1,8}国)，去京师(?P<distance>[一二三四五六七八九十百千万两\d]+)里"),
        lambda m: {
            "canonical_country": canonicalize_label(m.group("country")) or m.group("country"),
            "related_place": "京师",
            "relation_type": "距京师",
            "direction": "",
            "distance_li": str(cn_int(m.group("distance")) or ""),
            "evidence_source": "正文",
            "note": "原文距离",
        },
    ),
    (
        re.compile(r"(?P<country>[\u4e00-\u9fff]{1,8}国)，在(?P<direction>东南海中|西南海中|东北海中|西北海中|海中)"),
        lambda m: {
            "canonical_country": canonicalize_label(m.group("country")) or m.group("country"),
            "related_place": "海",
            "relation_type": "海中位置",
            "direction": m.group("direction").replace("海中", ""),
            "distance_li": "",
            "evidence_source": "正文",
            "note": "原文海中方位",
        },
    ),
    (
        re.compile(r"(?P<country>[\u4e00-\u9fff]{1,8}国)西北有(?P<place>[\u4e00-\u9fff]{1,8})"),
        lambda m: {
            "canonical_country": canonicalize_label(m.group("country")) or m.group("country"),
            "related_place": m.group("place"),
            "relation_type": "方位",
            "direction": "西北",
            "distance_li": "",
            "evidence_source": "正文",
            "note": "原文方位",
        },
    ),
    (
        re.compile(r"(?P<country>[\u4e00-\u9fff]{1,8}国)西有(?P<place>[\u4e00-\u9fff]{1,8})"),
        lambda m: {
            "canonical_country": canonicalize_label(m.group("country")) or m.group("country"),
            "related_place": m.group("place"),
            "relation_type": "方位",
            "direction": "西",
            "distance_li": "",
            "evidence_source": "正文",
            "note": "原文方位",
        },
    ),
]


def canonicalize_label(label: str) -> str | None:
    label = label.strip()
    if label in DROP_LABELS or label.endswith("此国"):
        return None
    return COUNTRY_RENAMES.get(label, label)


def summary_annotation_snippets() -> dict[str, str]:
    text = ANNOTATIONS.read_text(encoding="utf-8")
    out: dict[str, str] = {}
    for key in ["骨利幹國", "交趾", "波斯", "康國", "崑崙", "高句麗", "百濟", "龜兹國", "新羅", "吐蕃"]:
        m = re.search(re.escape(key) + r"[:：](.{0,180})", text)
        if m:
            out[key] = m.group(1).replace("\n", " ").strip()
    return out


def build_corrected_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    snippets = summary_annotation_snippets()
    for row in rows:
        canonical = canonicalize_label(row["country"])
        if not canonical:
            continue
        key = (canonical, row["paragraph_id"], row["source"])
        if key in seen:
            continue
        seen.add(key)
        meta = COUNTRY_META.get(canonical, {})
        annotation_key = canonical.replace("国", "國")
        out.append(
            {
                "original_country_label": row["country"],
                "canonical_country": canonical,
                "modern_reference": meta.get("modern_reference", ""),
                "tang_identification_note": meta.get("tang_note", ""),
                "annotation_reference_note": snippets.get(annotation_key, ""),
                "map_region": meta.get("map_region", ""),
                "volume_index": row["volume_index"],
                "volume_title": row["volume_title"],
                "source": row["source"],
                "paragraph_id": row["paragraph_id"],
                "related_subjects": row["related_subjects"],
                "text": row["text"],
            }
        )
    out.sort(key=lambda item: (item["canonical_country"], int(item["volume_index"]), item["source"]))
    return out


def build_relation_rows(corrected_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str, str]] = set()

    for relation in MANUAL_RELATIONS:
        key = (
            relation["canonical_country"],
            relation["related_place"],
            relation["relation_type"],
            relation["direction"],
            relation["distance_li"],
        )
        if key not in seen:
            out.append(relation)
            seen.add(key)

    for row in corrected_rows:
        text = row["text"]
        for pattern, builder in RELATION_PATTERNS:
            for match in pattern.finditer(text):
                relation = builder(match)
                if not canonicalize_label(relation["canonical_country"]):
                    continue
                key = (
                    relation["canonical_country"],
                    relation["related_place"],
                    relation["relation_type"],
                    relation["direction"],
                    relation["distance_li"],
                )
                if key in seen:
                    continue
                out.append(relation)
                seen.add(key)

    out.sort(key=lambda item: (item["canonical_country"], item["relation_type"], item["related_place"]))
    return out


def build_summary_rows(corrected_rows: list[dict[str, str]], relation_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    by_country: dict[str, dict[str, object]] = {}
    for row in corrected_rows:
        data = by_country.setdefault(
            row["canonical_country"],
            {
                "canonical_country": row["canonical_country"],
                "modern_reference": row["modern_reference"],
                "tang_identification_note": row["tang_identification_note"],
                "map_region": row["map_region"],
                "story_count": 0,
                "sources": [],
            },
        )
        data["story_count"] = int(data["story_count"]) + 1
        sources = data["sources"]
        if isinstance(sources, list) and row["source"] not in sources:
            sources.append(row["source"])

    rel_map: dict[str, list[str]] = {}
    for row in relation_rows:
        rel = row["related_place"]
        summary = f"{row['relation_type']}:{row['direction'] or '-'}:{rel}:{row['distance_li'] or '-'}"
        rel_map.setdefault(row["canonical_country"], [])
        if summary not in rel_map[row["canonical_country"]]:
            rel_map[row["canonical_country"]].append(summary)

    out: list[dict[str, str]] = []
    for country, data in sorted(by_country.items()):
        out.append(
            {
                "canonical_country": country,
                "modern_reference": str(data["modern_reference"]),
                "tang_identification_note": str(data["tang_identification_note"]),
                "map_region": str(data["map_region"]),
                "story_count": str(data["story_count"]),
                "sources": " | ".join(data["sources"]) if isinstance(data["sources"], list) else "",
                "distance_location_relations": " || ".join(rel_map.get(country, [])),
            }
        )
    return out


def build_map_nodes(summary_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    zone_positions = {
        "中原": ("50", "50"),
        "东北": ("78", "32"),
        "东北海东": ("86", "34"),
        "西域": ("28", "38"),
        "西域南道": ("25", "46"),
        "西域中亚": ("20", "34"),
        "西域极西": ("12", "30"),
        "西海以西": ("6", "26"),
        "西海之南": ("10", "42"),
        "西南天竺": ("22", "58"),
        "中天竺": ("26", "56"),
        "西南高原": ("34", "56"),
        "岭南以南": ("58", "72"),
        "南海西南": ("52", "78"),
        "南海群岛": ("66", "82"),
        "南海诸国": ("70", "76"),
        "极北": ("44", "12"),
    }
    rows: list[dict[str, str]] = []
    for row in summary_rows:
        if not row["map_region"]:
            continue
        x, y = zone_positions.get(row["map_region"], ("50", "50"))
        rows.append(
            {
                "canonical_country": row["canonical_country"],
                "map_region": row["map_region"],
                "suggested_x_percent": x,
                "suggested_y_percent": y,
                "modern_reference": row["modern_reference"],
            }
        )
    rows.sort(key=lambda item: (item["map_region"], item["canonical_country"]))
    return rows


def main() -> None:
    rows = read_csv(COUNTRY_ROWS)
    corrected_rows = build_corrected_rows(rows)
    relation_rows = build_relation_rows(corrected_rows)
    summary_rows = build_summary_rows(corrected_rows, relation_rows)
    map_node_rows = build_map_nodes(summary_rows)

    write_csv(
        BASE / "酉阳杂俎-初校-国别条目归类-据唐代考订.csv",
        corrected_rows,
        [
            "original_country_label",
            "canonical_country",
            "modern_reference",
            "tang_identification_note",
            "annotation_reference_note",
            "map_region",
            "volume_index",
            "volume_title",
            "source",
            "paragraph_id",
            "related_subjects",
            "text",
        ],
    )
    write_csv(
        BASE / "酉阳杂俎-初校-国别地望关系-据唐代考订.csv",
        relation_rows,
        [
            "canonical_country",
            "related_place",
            "relation_type",
            "direction",
            "distance_li",
            "evidence_source",
            "note",
        ],
    )
    write_csv(
        BASE / "酉阳杂俎-初校-国别地望汇总-据唐代考订.csv",
        summary_rows,
        [
            "canonical_country",
            "modern_reference",
            "tang_identification_note",
            "map_region",
            "story_count",
            "sources",
            "distance_location_relations",
        ],
    )
    write_csv(
        BASE / "酉阳杂俎-初校-国别地图节点-据唐代考订.csv",
        map_node_rows,
        ["canonical_country", "map_region", "suggested_x_percent", "suggested_y_percent", "modern_reference"],
    )

    print(f"corrected_country_rows={len(corrected_rows)}")
    print(f"relation_rows={len(relation_rows)}")
    print(f"summary_countries={len(summary_rows)}")


if __name__ == "__main__":
    main()

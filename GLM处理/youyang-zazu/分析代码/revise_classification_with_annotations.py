from __future__ import annotations

from collections import Counter
from pathlib import Path
import csv
import re
import sys

sys.path.append(r"C:\Users\lx\Desktop\前期准备")

import classify_yuyang as base  # noqa: E402


BASE = Path(r"C:\Users\lx\Desktop\前期准备\prepare")
REFERENCE_ANNOTATIONS = BASE / "酉阳杂俎-许逸民校-2015-annotations.txt"
SUFFIX = "-据注三次修订"

TERM_LINE_RE = re.compile(r"^([\u4e00-\u9fff]{2,8})[：:](.+)$")

GENERIC_TERMS = {
    "本条",
    "一",
    "二",
    "三",
    "四",
    "五",
    "六",
    "七",
    "八",
    "九",
    "十",
    "注",
}
INVALID_TERM_PARTS = {
    "为",
    "作",
    "曰",
    "言",
    "之",
    "初",
    "后",
    "後",
    "前",
    "来",
    "來",
    "去",
    "至",
    "见",
    "見",
    "死后",
    "死後",
    "来往",
    "來往",
    "不可",
}
DEFINITION_MARKERS = [
    "即",
    "谓",
    "亦称",
    "亦作",
    "在今",
    "之略称",
    "别称",
    "之一",
    "年号",
    "古长度单位",
    "神禽",
    "风筝",
    "马奶酒",
    "可入药",
]
BAD_SUBJECT_CHARS_RE = re.compile(r"[《》〈〉{}（）()\[\]○]")
COMPACT_CJK_RE = re.compile(r"^[\u4e00-\u9fff]{1,8}$")
PERSON_TITLE_RE = re.compile(
    r"^(僧|道士|道人|道土|真人|法师|和尚|天师|先生|处士|尼|梵僧)([\u4e00-\u9fff]{1,4})(?=(博|穷|善|本|尝|嘗|初|既|为|為|曰|言|令|命|诏|詔|因|后|後|字|居|事|开|天|乃|从|從|见|見|每|常|有|入|至|来|來|还|還|灭|滅|请|請|赴|观|觀|奏|受|死|卧|隱|隐|召|游|遊|出|归|歸))"
)
PERSON_NAME_RE = re.compile(
    r"^([\u4e00-\u9fff]{2,4})(公|王)?(?=(博|穷|善|本|尝|嘗|初|既|为|為|曰|言|令|命|诏|詔|因|后|後|字|居|事|开|天|乃|从|從|见|見|每|常|有|入|至|来|來|还|還|灭|滅|请|請|赴|观|觀|奏|受|死|卧|隱|隐|召|游|遊|出|归|歸))"
)
PLACE_ENTITY_RE = re.compile(r"^([\u4e00-\u9fff]{2,8}(?:国|州|郡|县|府|山|江|河|海|池))")
BUILDING_ENTITY_RE = re.compile(r"^([\u4e00-\u9fff]{2,8}(?:寺|塔|殿|宫|楼|观|苑|门))")
TIME_PREFIX_RE = re.compile(
    r"^(贞观中|贞观初|开元中|开元末|开元初|天宝末|天宝中|长庆中|太和中|永贞年|大历中|大历末|大历八年|元和中|元和末|宝历中|宝历|开成末|开成中|贞元中|建中|西汉|近代|秦汉以来|立春日|寒食日|三月三日|腊日|一日|昔|旧言)"
)
LEAD_PREFIX_RE = re.compile(r"^(又|有|其|上|乃|因|皆|常|时|時|后|後|忽|会|會|尝有|嘗有)+")
PERSON_BAD_NAME_CHARS = set("于之其者所与及乎焉乃则亦")
PLACE_SUFFIXES = ("国", "州", "郡", "县", "府", "山", "江", "河", "海", "池")
BUILDING_SUFFIXES = ("寺", "塔", "殿", "宫", "樓", "楼", "观", "苑", "门")
ENTITY_NOUN_SUFFIXES = (
    "草", "木", "花", "树", "竹", "藤", "芝", "香",
    "鸟", "鱼", "马", "虫", "兽", "龟", "鹊", "鹤", "猿", "狐", "兔", "鸡", "龙", "蛇", "虎", "凤",
    "鬼", "神", "妖", "怪", "魅", "精",
    "酒", "药", "汤", "镜", "剑", "钟", "鼓", "琴", "盘", "瓶", "鞭", "箭", "弓",
    "佛", "经", "僧", "仙", "礼",
)
BAD_PHRASE_CHARS = set("未无有言为為见見来來去至在用将將令命召称稱说說死食饮飲")
HUMAN_ROLE_GROUPS = {
    "僧": "僧",
    "和尚": "僧",
    "法师": "僧",
    "尼": "僧",
    "梵僧": "僧",
    "沙门": "僧",
    "道士": "道士",
    "道人": "道士",
    "道土": "道士",
    "天师": "道士",
    "真人": "真人",
    "先生": "先生",
    "处士": "处士",
}
HUMAN_ROLE_MENTION_RE = re.compile(
    r"(僧|和尚|法师|尼|梵僧|沙门|道士|道人|道土|天师|真人|先生|处士)"
    r"([\u4e00-\u9fff]{1,4}?)"
    r"(?=(博|穷|善|本|尝|嘗|初|既|为|為|曰|言|令|命|诏|詔|因|后|後|字|居|事|开|天|乃|从|從|见|見|每|常|有|入|至|来|來|还|還|灭|滅|请|請|赴|观|觀|奏|受|死|卧|隱|隐|召|游|遊|出|归|歸|也|矣|。|，|；|：))"
)
GENERIC_HUMAN_ROLES = set(HUMAN_ROLE_GROUPS.values()) | set(HUMAN_ROLE_GROUPS.keys()) | {"一行"}
COUNTRY_SPECIALS = {
    "波斯", "交趾", "昆仑", "拂林", "新罗", "真腊", "高句丽", "百济", "大食",
    "吐蕃", "安息", "扶南", "林邑", "回鹘", "骨利干", "乌仗那", "婆利",
    "罽宾", "天竺", "康国", "俱德建国", "乌仗那国", "婆利国", "摩伽陀国",
    "伽古罗国", "俱位国", "俱振提国", "北天健驮罗国", "北天竺国", "因墀国",
    "古龟兹国", "婆弥烂国", "昆吾国", "昆明国", "焉耆国", "苏都识匿国",
    "私诃条国", "莱子国", "长须国", "悬渡国", "憔侥国", "五天竺国",
    "仍建国", "拨拔力国", "悉怛国", "波斯属国", "扶支国", "真腊国",
}
COUNTRY_BAD_TERMS = {"国初", "国人", "国中", "国王", "国使", "国者"}
COUNTRY_CAPTURE_PATTERNS = [
    re.compile(r"(?:出|于|於|至|有|在|使至|来自|來自)?([\u4e00-\u9fff]{1,6}国)(?=(有|呼|王|人|城|寺|刹|尚|来|來|贡|貢|使|，|。|、|之|中|者))"),
    re.compile(r"([\u4e00-\u9fff]{1,6}属国)(?=(有|，|。|、|之))"),
]
COUNTRY_CANONICAL_MAP = {
    "波斯国": "波斯",
    "出波斯国": "波斯",
    "亦出波斯国": "波斯",
    "拂林国": "拂林",
    "出拂林国": "拂林",
    "亦出拂林国": "拂林",
    "真腊国": "真腊",
    "出真腊国": "真腊",
    "乌仗那": "乌仗那国",
}
COUNTRY_DROP_PREFIXES = (
    "一云本出", "本出", "乃诏上监", "京西持", "二使送客归中", "化被三千",
    "历八十一", "劫化他", "一万二城大", "境内并无此", "稍异中国", "如中国",
    "自古不属外", "吾国", "其国", "彼国", "此国", "时国", "令勉受",
)
COUNTRY_DROP_LABELS = {
    "外国", "中国", "其国", "我国", "此国", "彼国", "时国", "大国",
}


def normalize(text: str) -> str:
    return base.normalize(text)


def clean_term(term: str) -> str:
    term = normalize(term)
    term = re.sub(r"^[（(〔︹\[][^）)〕︺\]]+[）)〕︺\]]", "", term)
    term = re.sub(r"^[一二三四五六七八九十0-9]+", "", term)
    term = term.strip("「」『』（）()[]【】 ")
    return term[:8]


def clean_lead_text(text: str) -> str:
    norm = normalize(text)
    norm = re.sub(r"\{\{.*?\}\}", "", norm)
    norm = norm.strip()
    changed = True
    while changed:
        changed = False
        new_norm = TIME_PREFIX_RE.sub("", norm)
        if new_norm != norm:
            norm = new_norm.lstrip("，。；： ")
            changed = True
        new_norm = LEAD_PREFIX_RE.sub("", norm)
        if new_norm != norm:
            norm = new_norm.lstrip("，。；： ")
            changed = True
    return norm


def is_valid_term(term: str) -> bool:
    if not re.fullmatch(r"[\u4e00-\u9fff]{2,8}", term):
        return False
    if term in GENERIC_TERMS:
        return False
    if any(part in term for part in INVALID_TERM_PARTS):
        return False
    return True


def is_glossary_like(term: str, gloss: str) -> bool:
    prefix = gloss[:40]
    if any(marker in prefix for marker in DEFINITION_MARKERS):
        return True
    if term.endswith(("国", "州", "郡", "县", "府", "寺", "塔", "殿", "宫", "苑", "门", "楼", "池", "山", "江", "河", "海")):
        return any(marker in gloss for marker in ["在今", "之一", "国人", "地", "院", "寺", "殿", "宫", "楼", "山", "池"])
    if term.endswith(("草", "木", "花", "树", "香", "芝", "藤", "竹")):
        return any(marker in gloss for marker in ["即", "亦称", "亦作", "可入药", "香树", "树脂", "草", "木", "花"])
    if term.endswith(("鸟", "鱼", "马", "虫", "兽", "龟", "鹊", "鹤", "猿", "狐", "兔", "鸡")):
        return any(marker in gloss for marker in ["即", "亦作", "鸟", "鱼", "兽", "虫", "马"])
    return False


def is_named_person_label(label: str) -> bool:
    if not COMPACT_CJK_RE.fullmatch(label):
        return False
    if label.endswith(PLACE_SUFFIXES + BUILDING_SUFFIXES):
        return False
    if any(ch in label for ch in PERSON_BAD_NAME_CHARS):
        return False
    if re.fullmatch(r"(僧|道士|道人|道土|真人|法师|和尚|天师|先生|处士|尼|梵僧)[\u4e00-\u9fff]{1,4}", label):
        return True
    if 2 <= len(label) <= 4 and label not in {"波斯", "昆仑", "荆州", "南中", "泉", "石人"}:
        return True
    return False


def is_time_label(label: str) -> bool:
    if re.fullmatch(r"[开貞贞太大元宝永长景天][\u4e00-\u9fff]{1,3}(中|末|初|年)?", label):
        return True
    return label in {"贞观", "开元", "天宝", "元和", "太和", "大历", "宝历", "建中", "贞元"}


def is_compact_entity_label(label: str) -> bool:
    if not COMPACT_CJK_RE.fullmatch(label):
        return False
    if label in GENERIC_TERMS or label == "未判定":
        return False
    if is_time_label(label):
        return False
    if len(label) >= 3 and any(ch in BAD_PHRASE_CHARS for ch in label):
        return False
    if len(label) > 4 and not (
        is_named_person_label(label)
        or label.endswith(PLACE_SUFFIXES)
        or label.endswith(BUILDING_SUFFIXES)
        or label.endswith(ENTITY_NOUN_SUFFIXES)
    ):
        return False
    return True


def is_frequency_label(label: str) -> bool:
    if not is_compact_entity_label(label):
        return False
    if label.endswith(("者", "家", "近", "时", "時", "同", "等", "处", "條", "条", "下", "白")):
        return False
    if label.startswith(("凡", "今", "仍", "其", "某")):
        return False
    if len(label) >= 3 and any(ch in label for ch in "者家近时時同等等处"):
        return False
    if re.fullmatch(r"[一二三四五六七八九十][\u4e00-\u9fff]{1,7}", label) and not (
        is_named_person_label(label)
        or label.endswith(PLACE_SUFFIXES)
        or label.endswith(BUILDING_SUFFIXES)
        or label.endswith(ENTITY_NOUN_SUFFIXES)
    ):
        return False
    return True


def normalize_role_group(role: str) -> str:
    return HUMAN_ROLE_GROUPS.get(role, role)


def extract_named_humans(text: str) -> list[dict[str, str]]:
    norm = normalize(text)
    humans: list[dict[str, str]] = []
    seen: set[str] = set()
    for match in HUMAN_ROLE_MENTION_RE.finditer(norm):
        role = normalize_role_group(match.group(1))
        name = match.group(2)
        if not name or any(ch in PERSON_BAD_NAME_CHARS for ch in name):
            continue
        full = f"{role}{name}" if role in {"僧", "道士", "真人", "先生", "处士"} else f"{match.group(1)}{name}"
        key = f"{role}|{name}|{full}"
        if key in seen:
            continue
        seen.add(key)
        humans.append({"role_group": role, "short_name": name, "full_name": full})
    return humans


def build_subject_hierarchy(subject: str, broad: str, text: str) -> tuple[str, str, str]:
    label = normalize(subject)
    humans = extract_named_humans(text)
    if humans:
        for human in humans:
            aliases = {human["role_group"], human["short_name"], human["full_name"]}
            if label in aliases:
                return "人物政事", human["role_group"], human["full_name"]
        if label in GENERIC_HUMAN_ROLES and len(humans) == 1:
            human = humans[0]
            return "人物政事", human["role_group"], human["full_name"]
    return broad, label, label


def extract_countries(text: str, term_map: dict[str, str]) -> list[str]:
    norm = normalize(text)
    found: list[tuple[int, str]] = []
    seen: set[str] = set()

    candidates: set[str] = set(COUNTRY_SPECIALS)
    for term, broad in term_map.items():
        if broad != "异域物产":
            continue
        if term.endswith("国") or term.endswith("属国") or term in COUNTRY_SPECIALS:
            candidates.add(term)

    def normalize_country(label: str) -> str | None:
        if label in COUNTRY_CANONICAL_MAP:
            return COUNTRY_CANONICAL_MAP[label]
        if label in COUNTRY_DROP_LABELS:
            return None
        if any(label.startswith(prefix) for prefix in COUNTRY_DROP_PREFIXES):
            return None
        contained = sorted((candidate for candidate in candidates if candidate != label and candidate in label), key=len, reverse=True)
        if contained:
            normalized = contained[0]
            return COUNTRY_CANONICAL_MAP.get(normalized, normalized)
        if label.endswith("国") and label[:-1] in COUNTRY_SPECIALS:
            return label[:-1]
        if label.endswith("属国") and label[:-2] in COUNTRY_SPECIALS:
            return f"{label[:-2]}属国"
        return label

    for pattern in COUNTRY_CAPTURE_PATTERNS:
        for match in pattern.finditer(norm):
            country = normalize_country(match.group(1))
            if not country or country in COUNTRY_BAD_TERMS:
                continue
            if country not in seen:
                found.append((match.start(1), country))
                seen.add(country)

    for country in sorted(candidates, key=len, reverse=True):
        if country in seen:
            continue
        pos = norm.find(country)
        if pos != -1:
            normalized = normalize_country(country)
            if normalized and normalized not in seen:
                found.append((pos, normalized))
                seen.add(normalized)

    found.sort(key=lambda item: (item[0], -len(item[1]), item[1]))
    return [country for _, country in found]


def normalize_person_label(label: str) -> str:
    if label.endswith("公") and len(label) >= 3:
        return label[:-1]
    return label


def extract_lead_entity(text: str, term_map: dict[str, str]) -> tuple[str | None, str | None]:
    lead = clean_lead_text(text)
    lead = re.split(r"[。；：，]", lead, maxsplit=1)[0]

    m = PERSON_TITLE_RE.match(lead)
    if m:
        name = m.group(2)
        if not any(ch in PERSON_BAD_NAME_CHARS for ch in name):
            return normalize_person_label(f"{m.group(1)}{name}"), "person"

    m = PERSON_NAME_RE.match(lead)
    if m:
        candidate = normalize_person_label((m.group(1) or "") + (m.group(2) or ""))
        if is_named_person_label(candidate):
            return candidate, "person"

    for term, broad in sorted(term_map.items(), key=lambda item: (-len(item[0]), item[0])):
        if lead.startswith(term):
            if broad == "人物政事":
                return term, "person"
            if broad == "异域物产":
                return term, "place"
            if broad == "建筑寺塔":
                return term, "building"
            return term, "thing"

    m = BUILDING_ENTITY_RE.match(lead)
    if m:
        return m.group(1), "building"

    m = PLACE_ENTITY_RE.match(lead)
    if m:
        return m.group(1), "place"

    fallback = base.extract_primary_subject(text)
    if COMPACT_CJK_RE.fullmatch(fallback):
        if fallback.endswith(PLACE_SUFFIXES):
            return fallback, "place"
        if fallback.endswith(BUILDING_SUFFIXES):
            return fallback, "building"
        return fallback, "thing"
    return None, None


def infer_broad_from_entity(subject: str, broad: str, kind: str | None, term_map: dict[str, str]) -> str:
    mapped = term_map.get(subject)
    if mapped:
        return mapped
    if kind == "person":
        return "人物政事"
    if kind == "place":
        return "异域物产"
    if kind == "building":
        return "建筑寺塔"
    if subject.endswith(PLACE_SUFFIXES):
        return "异域物产"
    if subject.endswith(BUILDING_SUFFIXES):
        return "建筑寺塔"
    return broad


def compact_subject_label(subject: str, broad: str, text: str, term_map: dict[str, str]) -> tuple[str | None, str]:
    label = normalize(subject).strip()
    if label.endswith("公") and broad == "人物政事" and len(label) >= 3:
        label = label[:-1]

    lead_entity, lead_kind = extract_lead_entity(text, term_map)

    if broad in {"异人方术", "佛道信仰", "人物政事"} and lead_kind == "person" and lead_entity:
        return lead_entity, "人物政事"

    if label in {"僧", "道人", "道士", "道土", "真人", "法师", "和尚", "天师", "先生", "处士", "尼", "梵僧"} and lead_kind == "person" and lead_entity:
        return lead_entity, "人物政事"

    if BAD_SUBJECT_CHARS_RE.search(label) or not is_compact_entity_label(label):
        if lead_entity:
            if is_compact_entity_label(lead_entity):
                return lead_entity, infer_broad_from_entity(lead_entity, broad, lead_kind, term_map)
        return None, broad

    if broad == "人物政事" and (label.endswith(PLACE_SUFFIXES) or label.endswith(BUILDING_SUFFIXES)):
        return label, infer_broad_from_entity(label, broad, None, term_map)

    if is_named_person_label(label) and not label.endswith(PLACE_SUFFIXES + BUILDING_SUFFIXES):
        return label, "人物政事"

    if broad in {"异域物产", "建筑寺塔"} and lead_kind == "person" and lead_entity:
        return lead_entity, "人物政事"

    if not is_compact_entity_label(label):
        if lead_entity and is_compact_entity_label(lead_entity):
            return lead_entity, infer_broad_from_entity(lead_entity, broad, lead_kind, term_map)
        return None, broad

    return label, infer_broad_from_entity(label, broad, None, term_map)


def infer_broad_from_gloss(term: str, gloss: str) -> str | None:
    text = normalize(gloss)
    term_n = normalize(term)

    if text.startswith(("原校", "按，原", "疑", "原作", "据")):
        return None

    if any(k in text for k in ["冥司", "阴曹", "地府", "地狱", "墓", "坟", "葬", "尸"]):
        return "丧葬冥界"
    if any(k in text for k in ["佛经", "释氏", "佛寺", "菩萨", "佛", "僧", "法门"]) or term_n in {"上清", "兰若", "释氏书"}:
        return "佛道信仰"
    if any(k in text for k in ["神仙", "真人", "道士", "仙", "方术", "术士", "高僧", "修道"]):
        return "异人方术"
    if any(k in text for k in ["在今", "诸部之一", "西域", "部之一", "国人", "半岛", "海", "岛", "郡", "县", "州"]) or term_n.endswith("国"):
        return "异域物产"
    if any(k in text for k in ["鸟", "鱼", "兽", "虫", "马", "蛇", "龟", "鹊", "鹤", "猿", "兔", "鸡", "鸢", "神禽"]) or any(
        k in term_n for k in ["马", "鱼", "鸟", "虫", "蛇", "龟", "猿", "鹤", "兔", "鸡", "鸢", "雕", "虾蟆", "麒麟", "凤", "虎", "蟾蜍", "日乌"]
    ):
        return "动物"
    if any(k in text for k in ["树", "草", "花", "木", "竹", "藤", "芝", "香树", "树脂", "叶", "根"]) or any(
        k in term_n for k in ["树", "草", "花", "木", "竹", "藤", "芝", "李", "桃", "槐", "柳", "桂", "龙脑", "木香", "长生花"]
    ):
        return "植物"
    if any(k in text for k in ["药", "可入药", "可饮", "酒", "膏", "脂", "散", "汤", "口脂", "马奶酒"]):
        return "饮食医药"
    if any(k in text for k in ["巾", "风筝", "围裙", "仪仗", "剑", "弓", "箭", "琵琶", "琴", "幞头", "器", "乐器"]) or any(
        k in term_n for k in ["幞头", "蔽膝", "班剑", "翕"]
    ):
        return "器物技艺"
    if any(k in text for k in ["宫", "殿", "楼", "观", "苑", "寺", "塔", "门", "池", "寝殿", "宫殿"]) or any(
        k in term_n for k in ["宫", "殿", "楼", "观", "苑", "寺", "塔", "门", "池"]
    ):
        return "建筑寺塔"
    if any(k in text for k in ["梦", "祥瑞", "兆", "星", "月", "云", "占"]):
        return "梦兆占验"
    if any(k in text for k in ["即唐", "皇帝", "公主", "刺史", "有传", "字", "年号", "人。", "人也"]) and "国" not in text[:20]:
        return "人物政事"
    if any(k in text for k in ["寒食", "上巳", "腊日", "立春", "节", "祭", "礼", "祓", "风俗", "岁时"]):
        return "礼俗制度"
    if any(k in term_n for k in ["鬼", "神", "妖", "怪", "魅", "狐", "女娲", "河伯", "西王母", "天人"]):
        return "神怪妖魅"
    return None


def parse_annotation_term_map() -> dict[str, str]:
    term_map: dict[str, str] = {}
    lines = REFERENCE_ANNOTATIONS.read_text(encoding="utf-8").splitlines()
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        m = TERM_LINE_RE.match(stripped)
        if not m:
            continue
        term = clean_term(m.group(1))
        gloss = normalize(m.group(2))
        if not is_valid_term(term):
            continue
        if not is_glossary_like(term, gloss):
            continue
        broad = infer_broad_from_gloss(term, gloss)
        if broad:
            term_map[term] = broad
    return term_map


def note_terms_for_paragraph(text: str, term_map: dict[str, str]) -> list[tuple[str, str]]:
    norm = normalize(text)
    matches: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    lead = norm[:24]
    for term, broad in sorted(term_map.items(), key=lambda item: (-len(item[0]), item[0])):
        if term in lead:
            item = (broad, term)
            if item not in seen:
                matches.append(item)
                seen.add(item)
    return matches


def merge_subjects(
    baseline_matches: list[tuple[str, str]],
    primary_subject: str,
    note_matches: list[tuple[str, str]],
    section_name: str,
) -> tuple[list[tuple[str, str]], set[tuple[str, str]]]:
    note_by_subject = {subject: broad for broad, subject in note_matches}
    merged: list[tuple[str, str]] = []
    seen_subjects: set[str] = set()
    annotation_supported: set[tuple[str, str]] = set()

    for broad, subject in baseline_matches:
        if subject in base.GENERIC_SUBJECTS:
            continue
        final_broad = note_by_subject.get(subject, broad)
        item = (final_broad, subject)
        if subject not in seen_subjects:
            merged.append(item)
            seen_subjects.add(subject)
        if subject in note_by_subject:
            annotation_supported.add(item)

    for broad, subject in note_matches:
        if subject in seen_subjects or subject in base.GENERIC_SUBJECTS:
            continue
        if subject == primary_subject or normalize(primary_subject).startswith(subject):
            item = (broad, subject)
            merged.append(item)
            seen_subjects.add(subject)
            annotation_supported.add(item)

    if not merged:
        merged.append((base.infer_subject_broad_from_primary(primary_subject, section_name), primary_subject))

    return merged, annotation_supported


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def percent(count: int, total: int) -> str:
    return f"{(count / total * 100):.2f}%"


def output_name(original_name: str) -> str:
    stem, ext = original_name.rsplit(".", 1)
    return f"{stem}{SUFFIX}.{ext}"


def main() -> None:
    paragraphs = base.parse_paragraphs(base.TARGET)
    total = len(paragraphs)
    term_map = parse_annotation_term_map()

    narrative_rows: list[dict] = []
    subject_rows: list[dict] = []
    duplicate_rows: list[dict] = []
    country_rows: list[dict] = []
    subject_frequency: Counter[tuple[str, str]] = Counter()
    narrative_counter: Counter[str] = Counter()
    subject_counter: Counter[str] = Counter()
    country_counter: Counter[str] = Counter()

    for p in paragraphs:
        narrative = base.classify_narrative(p)
        source = f"{p.volume_title}-{p.paragraph_index_in_volume}"
        narrative_counter[narrative] += 1
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

        baseline_matches, primary_subject = base.classify_subjects(p)
        note_matches = note_terms_for_paragraph(p.text, term_map)

        merged, annotation_supported = merge_subjects(
            baseline_matches,
            primary_subject,
            note_matches,
            p.section_name,
        )

        broad_seen: set[str] = set()
        compact_rows: list[tuple[str, str, str, str, str]] = []
        compact_seen: set[tuple[str, str, str]] = set()
        for broad, subject in merged:
            compact_subject, compact_broad = compact_subject_label(subject, broad, p.text, term_map)
            if not compact_subject or compact_subject in base.GENERIC_SUBJECTS or compact_subject == "未判定":
                continue
            final_broad, level1_subject, level2_subject = build_subject_hierarchy(compact_subject, compact_broad, p.text)
            item = (final_broad, level1_subject, level2_subject)
            if item in compact_seen:
                continue
            compact_seen.add(item)
            compact_rows.append((final_broad, level1_subject, level2_subject, compact_subject, subject))

        if not compact_rows:
            fallback_subject, fallback_broad = compact_subject_label(primary_subject, base.infer_subject_broad_from_primary(primary_subject, p.section_name), p.text, term_map)
            if fallback_subject and fallback_subject not in base.GENERIC_SUBJECTS and fallback_subject != "未判定":
                final_broad, level1_subject, level2_subject = build_subject_hierarchy(fallback_subject, fallback_broad, p.text)
                compact_rows.append((final_broad, level1_subject, level2_subject, fallback_subject, primary_subject))

        for broad, level1_subject, level2_subject, subject, original_subject in compact_rows:
            subject_rows.append(
                {
                    "broad_category": broad,
                    "level1_subject": level1_subject,
                    "level2_subject": level2_subject,
                    "specific_subject": level2_subject,
                    "volume_index": p.volume_index,
                    "volume_title": p.volume_title,
                    "source": source,
                    "paragraph_id": p.paragraph_id,
                    "primary_subject": primary_subject,
                    "annotation_supported": "yes" if any(orig == original_subject for _, orig in annotation_supported) else "no",
                    "original_subject": original_subject,
                    "text": p.text,
                }
            )
            broad_seen.add(broad)
            if is_frequency_label(level2_subject):
                subject_frequency[(level1_subject, level2_subject)] += 1

        countries = extract_countries(p.text, term_map)
        for country in countries:
            country_rows.append(
                {
                    "country": country,
                    "volume_index": p.volume_index,
                    "volume_title": p.volume_title,
                    "source": source,
                    "paragraph_id": p.paragraph_id,
                    "related_subjects": " | ".join(sorted({level2 for _, _, level2, _, _ in compact_rows})),
                    "text": p.text,
                }
            )
            country_counter[country] += 1

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
                    "duplicate_specific_subjects": " | ".join(
                        sorted({f"{level1}-{level2}" if level1 != level2 else level2 for _, level1, level2, _, _ in compact_rows})
                    ),
                    "text": p.text,
                }
            )

    narrative_rows.sort(key=lambda x: (x["narrative_category"], x["volume_index"], x["source"]))
    subject_rows.sort(key=lambda x: (x["broad_category"], x["specific_subject"], x["volume_index"], x["source"]))
    duplicate_rows.sort(key=lambda x: (x["volume_index"], x["source"]))
    country_rows.sort(key=lambda x: (x["country"], x["volume_index"], x["source"]))

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
            "level1_subject": level1_subject,
            "level2_subject": level2_subject,
            "appearance_count": count,
        }
        for (level1_subject, level2_subject), count in sorted(subject_frequency.items(), key=lambda item: (-item[1], item[0][0], item[0][1]))
    ]

    country_stats_rows = [
        {
            "country": country,
            "paragraph_count": count,
            "absolute_percentage": percent(count, total),
        }
        for country, count in sorted(country_counter.items(), key=lambda item: (-item[1], item[0]))
    ]

    note_map_rows = [
        {"annotated_term": term, "broad_category": broad}
        for term, broad in sorted(term_map.items())
    ]

    write_csv(
        BASE / output_name("酉阳杂俎-初校-叙事分类明细.csv"),
        narrative_rows,
        ["narrative_category", "volume_index", "volume_title", "source", "paragraph_id", "text"],
    )
    write_csv(
        BASE / output_name("酉阳杂俎-初校-叙事分类统计.csv"),
        narrative_stats_rows,
        ["narrative_category", "paragraph_count", "absolute_percentage"],
    )
    write_csv(
        BASE / output_name("酉阳杂俎-初校-主题分类明细.csv"),
        subject_rows,
        ["broad_category", "level1_subject", "level2_subject", "specific_subject", "volume_index", "volume_title", "source", "paragraph_id", "primary_subject", "annotation_supported", "original_subject", "text"],
    )
    write_csv(
        BASE / output_name("酉阳杂俎-初校-主题分类统计.csv"),
        subject_stats_rows,
        ["broad_category", "paragraph_count", "absolute_percentage"],
    )
    write_csv(
        BASE / output_name("酉阳杂俎-初校-重复主题分类.csv"),
        duplicate_rows,
        ["volume_index", "volume_title", "source", "paragraph_id", "duplicate_broad_categories", "duplicate_specific_subjects", "text"],
    )
    write_csv(
        BASE / output_name("酉阳杂俎-初校-主题频次统计.csv"),
        subject_frequency_rows,
        ["level1_subject", "level2_subject", "appearance_count"],
    )
    write_csv(
        BASE / output_name("酉阳杂俎-初校-注释术语映射.csv"),
        note_map_rows,
        ["annotated_term", "broad_category"],
    )
    write_csv(
        BASE / output_name("酉阳杂俎-初校-国别条目归类.csv"),
        country_rows,
        ["country", "volume_index", "volume_title", "source", "paragraph_id", "related_subjects", "text"],
    )
    write_csv(
        BASE / output_name("酉阳杂俎-初校-国别统计.csv"),
        country_stats_rows,
        ["country", "paragraph_count", "absolute_percentage"],
    )

    print(f"paragraphs={total}")
    print(f"annotation_terms={len(term_map)}")
    print(f"subject_broad_categories={len(subject_counter)}")
    print(f"duplicate_subject_paragraphs={len(duplicate_rows)}")
    print(f"country_groups={len(country_counter)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
酉阳杂俎 三校版 分类文档生成脚本
生成7+1个markdown文档，格式参考GLM处理文件夹
"""

import re
import os
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\lx\Desktop\前期准备"
INPUT_FILE = os.path.join(BASE_DIR, "清洗数据", "酉阳杂俎-三校.md")
OUTPUT_DIR = os.path.join(BASE_DIR, "清洗数据")

# ============================================================
# 分类体系（同 classify_sanjiao.py）
# ============================================================
VOLUME_CATEGORIES = {
    "序": "史料序跋", "忠志": "帝王纪事", "礼异": "礼俗制度",
    "天咫": "天文地理", "玉格": "佛道异闻", "壶史": "神仙方术",
    "贝编": "佛道异闻", "境异": "异境异域", "喜兆": "征兆占验",
    "祸兆": "征兆占验", "物革": "事物怪变", "诡习": "器艺技法",
    "怪术": "术法幻术", "艺绝": "器艺技法", "器奇": "器物名物",
    "乐": "器艺技法", "酒食": "饮食医药", "医": "饮食医药",
    "黥": "礼俗制度", "雷": "天文地理", "梦": "梦兆占验",
    "事感": "精诚感应", "盗侠": "侠盗刺客", "物异": "异物异象",
    "广知": "广知博物", "语资": "语资谈助", "冥迹": "幽冥冥迹",
    "尸穸": "丧葬礼俗", "诺皋记上": "异闻志怪", "诺皋记下": "异闻志怪",
    "广动植之一": "动植物谱录", "广动植之二": "动植物谱录",
    "广动植之三": "动植物谱录", "广动植类之四": "动植物谱录",
    "肉攫部": "器艺技法", "支诺皋上": "异闻志怪", "支诺皋中": "异闻志怪",
    "支诺皋下": "异闻志怪", "贬误": "知识考辨", "寺塔记上": "佛寺塔庙",
    "寺塔记下": "佛寺塔庙", "金刚经鸠异": "佛道异闻",
    "支动": "动植物谱录", "支植上": "动植物谱录", "支植下": "动植物谱录",
}

THEME_KEYWORDS = {
    "人物政事": {
        "帝王": ['帝', '上', '天子', '诏', '敕', '玄宗', '太宗', '高宗', '肃宗', '代宗', '中宗', '睿宗', '则天', '明皇'],
        "人物": ['成式', '公', '卿', '大夫', '刺史', '令', '尉', '将军', '尚书', '侍郎', '学士'],
        "僧": ['僧', '沙弥', '比丘', '禅师', '上人', '法师', '梵僧', '胡僧'],
        "道士": ['道', '道士', '天师', '真人', '先生', '山人'],
        "侠盗": ['侠', '盗', '刺客', '贼', '劫', '夜叉'],
    },
    "动物": {
        "鸟类": ['鸟', '鹊', '鹰', '鹤', '雁', '燕', '雀', '凤', '鸱', '鸢', '雉', '鸦', '乌', '鹅', '鹭', '鸽', '鹦', '雕'],
        "兽类": ['虎', '鹿', '马', '牛', '羊', '犬', '狗', '豕', '猪', '象', '狮', '豹', '熊', '猴', '猿', '狐', '兔', '鼠', '猫', '狼', '驼', '骡', '驴'],
        "鱼类": ['鱼', '鲤', '鲫', '鲈', '鳖', '龟', '鳗', '鳝', '鲙', '鲸'],
        "爬行": ['蛇', '蜥', '龟', '鳄', '蜃', '蟒'],
        "昆虫": ['虫', '蚁', '蜂', '蝶', '蛾', '蝉', '蜻', '萤', '蝗', '螳', '蛛', '蝇'],
        "神物": ['龙', '蛟', '螭', '虬', '凤', '麟', '麒麟', '驺虞', '白泽'],
    },
    "鬼怪妖魅": {
        "鬼": ['鬼', '亡魂', '魂魄', '游魂', '幽魂', '鬼官', '鬼魅'],
        "仙": ['仙', '仙人', '飞仙', '神仙', '真仙', '地仙'],
        "精": ['精', '妖精', '狐精', '蛇精', '树精', '古精'],
        "魅": ['魅', '魑魅', '魍魉', '魅惑'],
        "妖": ['妖', '妖怪', '妖精', '妖魅', '妖术'],
        "魔": ['魔', '妖魔', '天魔', '夜叉', '修罗'],
    },
    "建筑寺塔": {
        "宫殿": ['宫', '宫殿', '皇宫', '殿', '堂', '阁', '台', '观'],
        "寺观": ['寺', '寺庙', '兰若', '伽蓝', '观', '道观', '宫观', '院', '庵'],
        "城楼": ['城', '楼', '门', '墙', '坊', '郭'],
    },
    "器物技艺": {
        "武器": ['剑', '刀', '戟', '戈', '矛', '弓', '箭', '鞭', '盾'],
        "镜": ['镜', '铜镜', '明镜'],
        "用具": ['盘', '碗', '杯', '鼎', '壶', '瓶', '匣', '箱', '炉'],
        "衣饰": ['衣', '冠', '带', '履', '衾', '裘', '袍', '裙', '帛'],
        "乐器": ['鼓', '钟', '磬', '琴', '瑟', '箫', '笛', '竽', '琵琶'],
    },
    "佛道信仰": {
        "佛": ['佛', '释', '菩萨', '罗汉', '涅槃', '佛光', '舍利'],
        "道": ['道', '老君', '太上', '太极', '真人', '丹', '炼'],
        "经法": ['经', '法', '戒', '禅', '论', '咒', '符', '梵'],
    },
    "丧葬冥界": {
        "葬": ['葬', '墓', '棺', '坟', '椁', '冢', '殉'],
        "冥": ['冥', '阴间', '地府', '黄泉', '幽冥', '阎罗'],
        "尸": ['尸', '尸解', '不朽', '僵尸', '骸骨', '骨'],
    },
    "饮食医药": {
        "食": ['食', '煮', '饮', '饼', '羹', '粥', '脍', '鲙', '馎饦', '馄饨'],
        "药": ['药', '丹', '丸', '散', '汤', '医', '治', '病', '疾'],
        "酒": ['酒', '酿', '醪', '醑', '醅', '醴', '醪糟'],
        "茶": ['茶', '茗', '煎茶'],
    },
    "梦兆占验": {
        "梦": ['梦', '入梦', '托梦', '梦中', '梦兆', '凶梦', '吉梦'],
        "兆": ['兆', '占', '卜', '谶', '瑞', '凶', '吉', '祈', '应验'],
    },
    "异域物产": {
        "异国": ['波斯', '西域', '天竺', '大食', '突厥', '龟兹', '于阗', '拂林', '昆仑', '胡', '蛮'],
    },
    "天文地理": {
        "天象": ['日', '月', '星', '辰', '风', '雨', '雷', '电', '云', '雾', '霜', '雪', '虹', '蚀'],
        "地理": ['山', '水', '泉', '井', '河', '江', '海', '湖', '洞', '谷'],
    },
    "植物": {
        "木": ['松', '柏', '柳', '槐', '桑', '榆', '桐', '桂', '竹', '檀', '梅'],
        "果": ['桃', '李', '杏', '柿', '枣', '梨', '橘', '柚', '橙'],
        "花": ['花', '莲', '菊', '兰', '牡丹', '芍药', '芙蓉'],
        "草": ['草', '芝', '茅', '苇', '芦', '艾', '蒿', '苔', '萍'],
    },
}

CORE_SHENGUI_KEYWORDS = [
    '神', '鬼', '仙', '妖', '魔', '魅', '怪', '精', '佛', '僧', '道',
    '龙', '蛟', '凤', '麒麟', '狐', '变', '尸解', '冥', '魂', '魄',
    '地狱', '天帝', '菩萨', '袈裟', '符', '咒', '术士', '法师', '天师',
    '巫', '真人', '飞行', '变化', '异人', '天翁', '灶神', '帝江',
    '不空', '万回', '一行', '罗公远', '邢和璞', '翟天师',
]
SECONDARY_SHENGUI_KEYWORDS = [
    '灵', '瑞', '谶', '兆', '梦', '卜', '占', '祈', '咒', '丹',
    '修炼', '飞升', '得道', '破戒', '超度', '转世', '轮回',
    '阴间', '阳间', '天宫', '地府', '阎罗', '判官',
    '夜叉', '修罗', '阿修罗', '毗沙门', '观音',
    '舍利', '佛光', '神光', '灵光', '圣迹',
    '巫术', '法术', '妖术', '幻术', '仙术',
    '黄白', '丹砂', '长生', '不死',
    '托梦', '入梦', '梦中', '显灵', '降神',
    '怪异', '奇异', '不可思议',
]
MONSTER_TYPE_KEYWORDS = {
    "神话异兽": ['帝江', '刑天', '浑水敦', '异兽', '怪兽', '大蛇', '毒龙', '飞头', '夜叉', '蛟', '螭', '虬'],
    "神仙志怪": ['仙', '真人', '天翁', '天帝', '灶神', '得道', '飞升', '修炼', '羽化', '尸解', '道士'],
    "妖怪变形": ['变', '妖', '魅', '化', '变形', '化为人', '化为', '幻', '精', '狐', '蛇精'],
    "降妖伏魔": ['降', '伏', '斩', '收', '制服', '破', '驱除', '禳', '除妖', '镇'],
    "民俗神灵": ['灶神', '门神', '土地', '城隍', '河伯', '山神', '风伯', '雨师', '雷公', '龙王'],
    "佛道灵异": ['佛', '僧', '道', '寺', '观', '菩萨', '罗汉', '经', '咒', '法', '舍利', '灵光', '袈裟'],
    "冥界报应": ['冥', '地狱', '阎罗', '判官', '鬼', '阴间', '报应', '还魂', '转世', '罚'],
    "梦兆占验": ['梦', '兆', '谶', '占', '卜', '祈', '瑞', '入梦', '托梦'],
    "术法幻术": ['术', '法', '幻', '隐形', '变化', '咒', '符', '法术', '奇术', '幻术'],
    "异域怪物": ['异域', '波斯', '西域', '天竺', '外国', '蛮', '胡', '大食', '拂林'],
    "尸解变化": ['尸解', '尸', '不朽', '不腐', '僵尸', '骸骨'],
    "事物怪变": ['忽变', '怪变', '异变', '化为', '变形', '变异'],
}
NARRATIVE_THEME_KEYWORDS = {
    "死者复活": ['复生', '还魂', '再生', '复苏', '起死', '更生', '魂归', '且生'],
    "鬼魂还阳": ['还阳', '魂归', '鬼魂', '亡魂', '游魂', '魂魄', '附身', '托生', '冥归'],
    "生死边界": ['冥', '阴间', '地府', '黄泉', '幽冥', '阳间', '还魂', '入冥', '赴冥'],
    "丧葬再生": ['葬', '墓', '冢', '棺', '椁', '殉', '陪葬', '祭', '迁葬', '发冢'],
    "迷路返回时间流逝": ['迷', '迷路', '失路', '歧路', '不知所之', '寻路', '归路', '归', '还家', '不得归'],
    "时间错位": ['经年', '数日', '忽觉', '须臾', '瞬息', '岁月', '经宿', '遽', '倏忽', '恍然'],
    "空间异变": ['忽见', '异境', '异地', '仙境', '洞天', '福地', '幻境', '迷途'],
    "天上人间": ['天宫', '上天', '天帝', '仙界', '降世', '天上', '人间', '下凡'],
    "人兽互变": ['化为人', '变为', '变形', '变', '化', '幻化', '人形', '兽形', '狐变', '蛇变'],
    "物怪变形": ['化为', '忽变', '变形', '物怪', '成精', '作怪', '妖怪'],
    "妖魅惑人": ['魅', '惑', '迷', '妖', '淫', '色', '幻', '惑人', '迷乱'],
    "修道成仙": ['修炼', '得道', '飞升', '仙', '真人', '羽化', '辟谷', '炼丹', '黄白'],
    "僧尼异事": ['僧', '尼', '寺', '佛', '禅', '经', '咒', '戒', '钵', '袈裟', '斋'],
    "法术幻术": ['术', '法', '幻', '隐形', '变化', '咒', '符', '奇术', '遁', '遁术'],
    "因果报应": ['报应', '因果', '善报', '恶报', '罚', '赎', '劫', '还报', '业'],
    "佛法灵验": ['佛', '观音', '菩萨', '经', '念', '诵', '灵验', '显灵', '护法'],
    "梦兆应验": ['梦', '入梦', '托梦', '梦中', '兆', '应', '征', '谶', '吉梦', '凶梦'],
    "占卜预言": ['占', '卜', '谶', '预言', '相', '算', '推', '卜筮'],
    "祥瑞灾异": ['瑞', '祥', '灾', '异', '天象', '蚀', '蝗', '旱', '水', '祥瑞'],
    "异物奇珍": ['异', '奇', '宝', '珍', '怪', '异物', '奇珍', '珍宝', '珠', '玉'],
    "动植怪变": ['变异', '怪', '异', '畸形', '双头', '无目', '变化'],
    "自然怪象": ['风', '雨', '雷', '电', '虹', '雾', '霜', '异', '怪', '天变'],
    "侠客义行": ['侠', '义', '刺客', '飞天夜叉', '盗', '劫', '杀', '报恩', '报仇'],
    "奇人异能": ['异人', '奇术', '绝技', '高手', '异能', '神力', '奇才'],
    "隐逸高人": ['隐', '逸', '山人', '处士', '高人', '道士', '先生'],
    "忠孝节义": ['忠', '孝', '节', '义', '烈', '贞', '廉', '仁', '礼'],
    "冤屈报应": ['冤', '屈', '报', '雪', '伸', '冤魂', '复仇'],
    "情爱奇闻": ['婚', '嫁', '妻', '妾', '情', '恋', '美', '色', '缘'],
}

DESCRIPTION_SUBJECT_KEYWORDS = {
    "人物志": ['人', '士', '官', '将', '臣', '帝', '王', '公', '卿', '僧', '道', '尼', '医', '匠', '侠', '盗'],
    "动植矿物": ['鸟', '兽', '鱼', '虫', '草', '木', '花', '石', '金', '玉', '药', '龙', '蛇', '虎', '鹿', '马', '犬', '狐'],
    "地理建筑": ['山', '水', '城', '寺', '塔', '观', '宫', '殿', '门', '桥', '路', '河', '海', '湖'],
    "器物技艺": ['剑', '刀', '弓', '镜', '钟', '鼓', '琴', '书', '画', '药', '丹', '符', '印'],
    "礼俗制度": ['礼', '祭', '葬', '婚', '冠', '服', '官', '律', '刑', '赋', '贡'],
    "天文气象": ['日', '月', '星', '风', '雨', '雷', '电', '云', '雾', '霜', '雪', '虹'],
    "佛道宗教": ['佛', '僧', '道', '寺', '观', '经', '咒', '符', '仙', '禅', '菩萨', '罗汉', '地狱', '天宫'],
    "鬼神怪异": ['鬼', '神', '妖', '魅', '精', '魔', '怪', '魂', '魄', '冥', '阴', '阳', '尸'],
    "梦兆占卜": ['梦', '兆', '占', '卜', '谶', '瑞', '凶', '吉', '祈'],
    "食药物产": ['食', '饮', '酒', '茶', '药', '丹', '果', '蔬', '肉', '鱼', '米', '麦'],
}

SHENGUI_VOLUMES = {"诺皋记上", "诺皋记下", "支诺皋上", "支诺皋中", "支诺皋下"}
MOSTLY_SHENGUI_VOLUMES = {"玉格", "壶史", "贝编", "境异", "怪术", "冥迹", "尸穸"}

def get_volume_short(vol_title):
    if '·' in vol_title:
        return vol_title.split('·', 1)[1]
    return vol_title.replace('续·', '')

def get_narrative_category(vol_title):
    name = get_volume_short(vol_title)
    for key, cat in VOLUME_CATEGORIES.items():
        if key in name or name in key:
            return cat
    if '广动植' in name: return '动植物谱录'
    if '诺皋' in name: return '异闻志怪'
    if '支诺皋' in name: return '异闻志怪'
    if '寺塔' in name: return '佛寺塔庙'
    if '支植' in name or '支动' in name: return '动植物谱录'
    return '未分类'

def is_supernatural(text, vol_short, cat):
    if vol_short in SHENGUI_VOLUMES: return True
    core = sum(1 for kw in CORE_SHENGUI_KEYWORDS if kw in text)
    if core >= 2: return True
    sec = sum(1 for kw in SECONDARY_SHENGUI_KEYWORDS if kw in text)
    if sec >= 3: return True
    if core >= 1 and sec >= 1: return True
    if cat in ["佛道异闻","神仙方术","异闻志怪","幽冥冥迹","丧葬礼俗","梦兆占验","征兆占验","事物怪变","术法幻术","异物异象","异境异域"]:
        if core >= 1 or sec >= 2: return True
    return False

def determine_monster_type(text):
    scores = {}
    for mt, kws in MONSTER_TYPE_KEYWORDS.items():
        s = sum(1 for kw in kws if kw in text)
        if s > 0: scores[mt] = s
    if not scores:
        if '佛' in text or '僧' in text or '道' in text: return "佛道灵异"
        if '鬼' in text or '冥' in text: return "冥界报应"
        if '梦' in text: return "梦兆占验"
        if '变' in text or '化' in text: return "妖怪变形"
        return "神仙志怪"
    return max(scores, key=scores.get)

def determine_narrative_themes(text):
    themes = []
    for name, kws in NARRATIVE_THEME_KEYWORDS.items():
        c = sum(1 for kw in kws if kw in text)
        if c >= 2: themes.append(name)
        elif c == 1 and len(kws) <= 3: themes.append(name)
    if not themes:
        for name, kws in NARRATIVE_THEME_KEYWORDS.items():
            if any(kw in text for kw in kws):
                themes.append(name)
                if len(themes) >= 2: break
    return themes

def determine_desc_subjects(text):
    subjects = {}
    for subj, kws in DESCRIPTION_SUBJECT_KEYWORDS.items():
        found = [kw for kw in kws if kw in text]
        if len(found) >= 3: subjects[subj] = found[:5]
    if not subjects:
        for subj, kws in DESCRIPTION_SUBJECT_KEYWORDS.items():
            found = [kw for kw in kws if kw in text]
            if len(found) >= 2:
                subjects[subj] = found[:3]
                if len(subjects) >= 2: break
    return subjects

def determine_theme_details(text):
    """返回 {大类: {子类: [匹配关键词]}} 格式的描写主题"""
    result = {}
    for broad, subcats in THEME_KEYWORDS.items():
        sub_matches = {}
        for sub, kws in subcats.items():
            found = [kw for kw in kws if kw in text]
            if found:
                sub_matches[sub] = found[:3]
        if sub_matches:
            result[broad] = sub_matches
    return result

def generate_pid(vol_idx, para_idx, is_xu=False):
    prefix = "S" if vol_idx == 0 else ("X" if is_xu else "V")
    vol_num = f"{vol_idx:02d}"
    return f"{prefix}{vol_num}-P{para_idx:03d}"

def brief(text, max_len=60):
    if len(text) <= max_len: return text
    return text[:max_len] + '……'

# ============================================================
# Parse
# ============================================================
def parse_sanjiao(content):
    lines = content.split('\n')
    volumes = []
    current_vol = None
    current_paras = []
    for line in lines:
        stripped = line.strip()
        if not stripped: continue
        if stripped.startswith('## '):
            if current_vol and current_paras:
                volumes.append((current_vol, current_paras))
            current_vol = stripped[3:].strip()
            current_paras = []
        elif len(stripped) > 5:
            current_paras.append(stripped)
    if current_vol and current_paras:
        volumes.append((current_vol, current_paras))
    return volumes

# ============================================================
# Main
# ============================================================
def main():
    print("读取三校文件...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    volumes = parse_sanjiao(content)
    print(f"解析到 {len(volumes)} 卷")
    
    # Classify all paragraphs
    all_entries = []
    shengui_entries = []
    vol_idx = 0
    for vol_title, paras in volumes:
        vol_short = get_volume_short(vol_title)
        cat = get_narrative_category(vol_title)
        is_xu = vol_title.startswith('续·')
        for pi, para in enumerate(paras, 1):
            pid = generate_pid(vol_idx, pi, is_xu or vol_idx == 0)
            has_sgui = is_supernatural(para, vol_short, cat)
            desc_subjects = determine_desc_subjects(para)
            theme_details = determine_theme_details(para)
            
            entry = {
                "pid": pid, "vol_title": vol_title, "vol_short": vol_short,
                "narrative_category": cat, "has_supernatural": has_sgui,
                "description_subjects": desc_subjects,
                "theme_details": theme_details,
                "text": para, "text_brief": brief(para),
            }
            if has_sgui:
                entry["monster_type"] = determine_monster_type(para)
                entry["narrative_themes"] = determine_narrative_themes(para)
                shengui_entries.append(entry)
            all_entries.append(entry)
        vol_idx += 1
    
    total = len(all_entries)
    total_sgui = len(shengui_entries)
    print(f"总段落: {total}, 神怪: {total_sgui}")
    
    # ============================================================
    # 01-卷目分段.md
    # ============================================================
    print("生成 01-卷目分段.md...")
    lines = ["# 《酉阳杂俎》卷目分段（三校版）\n"]
    lines.append("| 段落ID | 卷·篇 | 内容概要 |")
    lines.append("|--------|--------|----------|")
    for e in all_entries:
        lines.append(f"| {e['pid']} | {e['vol_title']} | {e['text_brief']} |")
    with open(os.path.join(OUTPUT_DIR, "01-卷目分段.md"), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    # ============================================================
    # 02-叙事结构分类表.md
    # ============================================================
    print("生成 02-叙事结构分类表.md...")
    cat_stats = defaultdict(int)
    vol_cat = defaultdict(lambda: defaultdict(int))
    for e in all_entries:
        cat_stats[e['narrative_category']] += 1
        vol_cat[e['vol_title']][e['narrative_category']] += 1
    
    all_cats = sorted(cat_stats.keys(), key=lambda x: -cat_stats[x])
    
    lines = ["# 《酉阳杂俎》叙事结构分类表（三校版）\n"]
    lines.append("## 分类标准说明\n")
    lines.append("基于段落叙事特征，将全文段落分为以下类别：\n")
    lines.append("| 分类名称 | 定义 |")
    lines.append("|----------|------|")
    cat_defs = {
        "动植物谱录": "描述动植物、矿物等自然物的分类谱录",
        "异闻志怪": "含鬼神妖怪、异变怪异、因果报应的叙事故事",
        "人物轶事": "记载帝王将相、名人的轶事趣闻",
        "知识考辨": "杂录典籍引述、文字考证、实用知识",
        "神仙方术": "描述方术、道法、幻术等术数技艺",
        "佛道异闻": "引述佛道经典、宗教义理、修行体系的异闻",
        "器艺技法": "记载手工技艺、奇术表演、纹身等",
        "异境异域": "描述外国异邦风土人情",
        "征兆占验": "涉及梦境、占卜、预言、祥瑞灾异",
        "饮食医药": "涉及食物、烹饪、饮馔、药理医术",
        "礼俗制度": "记载礼仪、官制、婚俗、丧制等制度",
        "器物名物": "涉及珍奇器物、宝物名称考辨",
        "冥界报应": "涉及冥界、阴司、因果报应",
        "天文地理": "涉及天象、地理、自然奇观",
        "帝王纪事": "记载帝王事迹、宫中轶事",
        "侠盗刺客": "涉及侠客、盗贼、刺客的故事",
        "精诚感应": "精诚感动天地的故事",
        "梦兆占验": "涉及梦境、预兆的故事",
        "丧葬礼俗": "涉及丧葬制度、冥间传说的故事",
        "语资谈助": "语言文字、典故轶事",
        "广知博物": "广博知识、博物考辨",
        "异物异象": "异物、异象、怪异事物",
        "事物怪变": "事物突然变异的故事",
        "术法幻术": "法术、幻术、奇异技艺",
        "佛寺塔庙": "记载佛寺、塔、庙的故事",
        "史料序跋": "序言、史料",
    }
    for cat in all_cats:
        defn = cat_defs.get(cat, "其他分类")
        lines.append(f"| {cat} | {defn} |")
    
    lines.append("\n---\n\n## 叙事结构分类统计\n")
    lines.append(f"**全文段落总数：{total}段**\n")
    lines.append("| 分类 | 段落数 | 百分比(%) |")
    lines.append("|------|--------|-----------|")
    for cat in all_cats:
        c = cat_stats[cat]
        lines.append(f"| {cat} | {c} | {c/total*100:.1f}% |")
    
    lines.append("\n---\n\n## 逐卷叙事结构分布\n")
    header = "| 卷·篇 | " + " | ".join(all_cats) + " | 合计 |"
    sep = "|--------|" + "|".join(["------"] * len(all_cats)) + "|------|"
    lines.append(header)
    lines.append(sep)
    for vol_title, paras in volumes:
        row = f"| {vol_title} |"
        for cat in all_cats:
            row += f" {vol_cat[vol_title].get(cat, 0)} |"
        row += f" {len(paras)} |"
        lines.append(row)
    
    with open(os.path.join(OUTPUT_DIR, "02-叙事结构分类表.md"), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    # ============================================================
    # 03-描写对象分类表.md
    # ============================================================
    print("生成 03-描写对象分类表.md...")
    desc_stats = defaultdict(int)
    desc_detail = {}  # {broad: {sub: count}}
    for e in all_entries:
        for subj, kws in e['description_subjects'].items():
            desc_stats[subj] += 1
            if subj not in desc_detail: desc_detail[subj] = defaultdict(int)
            for kw in kws:
                desc_detail[subj][kw] += 1
    
    lines = ["# 《酉阳杂俎》描写对象分类表（三校版）\n"]
    lines.append("## 分类标准说明\n")
    lines.append("按段落所描述的主要对象分类，共设10大类。一段可归属多类。\n")
    lines.append("| 一级分类 | 二级子类 | 段落数 |")
    lines.append("|----------|----------|--------|")
    for broad in DESCRIPTION_SUBJECT_KEYWORDS:
        count = desc_stats.get(broad, 0)
        subs = "、".join(list(desc_detail.get(broad, {}).keys())[:5])
        lines.append(f"| {broad} | {subs}… | {count} |")
    
    lines.append("\n---\n\n## 主题分类统计\n")
    lines.append(f"**全文段落总数：{total}段（一段可归属多类）**\n")
    lines.append("| 分类 | 段落数 | 占全文比(%) |")
    lines.append("|------|--------|-------------|")
    for subj in sorted(desc_stats.keys(), key=lambda x: -desc_stats[x]):
        c = desc_stats[subj]
        lines.append(f"| {subj} | {c} | {c/total*100:.1f}% |")
    
    with open(os.path.join(OUTPUT_DIR, "03-描写对象分类表.md"), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    # ============================================================
    # 04-交叉分类表.md
    # ============================================================
    print("生成 04-交叉分类表.md...")
    multi_entries = [e for e in all_entries if len(e['theme_details']) >= 2]
    
    lines = ["# 《酉阳杂俎》交叉分类表（三校版）\n"]
    lines.append("## 说明\n\n本表记录同时属于多个主题类别的段落。\n")
    lines.append(f"## 多主题段落（共{len(multi_entries)}段）\n")
    lines.append("| 段落ID | 卷·篇 | 叙事分类 | 主题类别 | 一级 | 二级 | 内容概要 |")
    lines.append("|--------|--------|----------|----------|------|------|----------|")
    for e in multi_entries[:500]:  # Limit output
        themes_str = "、".join([f"{broad}" for broad in e['theme_details'].keys()])
        sub_strs = []
        kw_strs = []
        for broad, subs in e['theme_details'].items():
            for sub, kws in subs.items():
                sub_strs.append(sub)
                kw_strs.append("、".join(kws[:2]))
        first_sub = sub_strs[0] if sub_strs else ""
        first_kw = kw_strs[0] if kw_strs else ""
        lines.append(f"| {e['pid']} | {e['vol_title']} | {e['narrative_category']} | {themes_str} | {first_sub} | {first_kw} | {e['text_brief']} |")
    if len(multi_entries) > 500:
        lines.append(f"| … | … | … | … | … | … | （共{len(multi_entries)}段） |")
    
    with open(os.path.join(OUTPUT_DIR, "04-交叉分类表.md"), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    # ============================================================
    # 05-描写对象频次表.md
    # ============================================================
    print("生成 05-描写对象频次表.md...")
    keyword_freq = defaultdict(lambda: {"count": 0, "broad": "", "sub": "", "pids": []})
    for e in all_entries:
        for broad, subs in e['theme_details'].items():
            for sub, kws in subs.items():
                for kw in kws:
                    key = f"{broad}|{sub}|{kw}"
                    keyword_freq[key]["count"] += 1
                    keyword_freq[key]["broad"] = broad
                    keyword_freq[key]["sub"] = sub
                    keyword_freq[key]["pids"].append(e['pid'])
    
    sorted_kw = sorted(keyword_freq.items(), key=lambda x: -x[1]["count"])
    
    lines = ["# 《酉阳杂俎》描写对象频次表（三校版）\n"]
    lines.append("## 说明\n\n统计全文各描写对象出现的次数，按频次从高到低排列。\n")
    lines.append("| 排名 | 一级子类 | 二级主题 | 出现次数 | 所在段落编号（前5个） |")
    lines.append("|------|----------|----------|----------|----------------------|")
    for rank, (key, info) in enumerate(sorted_kw[:80], 1):
        pids_str = "、".join(info["pids"][:5])
        lines.append(f"| {rank} | {info['broad']} | {info['sub']} | {info['count']} | {pids_str} |")
    
    with open(os.path.join(OUTPUT_DIR, "05-描写对象频次表.md"), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    # ============================================================
    # 06-同类描写对象汇总.md (simplified - top keywords only)
    # ============================================================
    print("生成 06-同类描写对象汇总.md...")
    # Group by (broad, sub)
    sub_groups = defaultdict(list)
    for e in all_entries:
        for broad, subs in e['theme_details'].items():
            for sub, kws in subs.items():
                sub_groups[(broad, sub)].append(e)
    
    lines = ["# 《酉阳杂俎》同类描写对象汇总（三校版）\n"]
    lines.append("## 说明\n\n将描写同一类对象的段落集中排列，方便比较分析。\n")
    
    # Sort by count desc
    sorted_groups = sorted(sub_groups.items(), key=lambda x: -len(x[1]))
    for (broad, sub), entries in sorted_groups[:30]:  # Top 30 groups
        lines.append(f"\n## {broad} - {sub}（{len(entries)}段）\n")
        lines.append("| 序号 | 卷·篇 | 段落ID | 内容概要 |")
        lines.append("|------|--------|---------|----------|")
        for i, e in enumerate(entries[:10], 1):
            lines.append(f"| {i} | {e['vol_title']} | {e['pid']} | {e['text_brief']} |")
        if len(entries) > 10:
            lines.append(f"| … | … | … | （共{len(entries)}段） |")
    
    with open(os.path.join(OUTPUT_DIR, "06-同类描写对象汇总.md"), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    # ============================================================
    # 07-段落描写对象分类总表.md (simplified)
    # ============================================================
    print("生成 07-段落描写对象分类总表.md...")
    lines = ["# 《酉阳杂俎》段落描写对象分类总表（三校版）\n"]
    lines.append(f"> 基于{total}段全文，按描写对象一级类目→二级类目组织\n\n---\n")
    lines.append(f"**全文段落总数**：{total}段\n")
    lines.append(f"**主题分类记录**：{sum(len(e['theme_details']) for e in all_entries)}条（一段可归属多类）\n\n")
    
    for broad in THEME_KEYWORDS:
        lines.append(f"\n## {broad}（{sum(1 for e in all_entries if broad in e['theme_details'])}段）\n")
        for sub in THEME_KEYWORDS[broad]:
            sub_entries = [e for e in all_entries if broad in e['theme_details'] and sub in e['theme_details'][broad]]
            if not sub_entries: continue
            lines.append(f"\n### {sub}（{len(sub_entries)}段）\n")
            lines.append("| 段落ID | 卷·篇 | 叙事分类 | 内容概要 |")
            lines.append("|--------|--------|----------|----------|")
            for e in sub_entries[:20]:
                lines.append(f"| {e['pid']} | {e['vol_title']} | {e['narrative_category']} | {e['text_brief']} |")
            if len(sub_entries) > 20:
                lines.append(f"| … | … | … | （共{len(sub_entries)}段） |")
    
    with open(os.path.join(OUTPUT_DIR, "07-段落描写对象分类总表.md"), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    # ============================================================
    # 神鬼妖魔怪描写对象提取报告.md
    # ============================================================
    print("生成 神鬼妖魔怪描写对象提取报告.md...")
    # Keyword frequency for supernatural
    all_sgui_kw = CORE_SHENGUI_KEYWORDS + SECONDARY_SHENGUI_KEYWORDS
    kw_freq = defaultdict(int)
    for e in shengui_entries:
        for kw in all_sgui_kw:
            if kw in e['text']:
                kw_freq[kw] += 1
    sorted_kw_freq = sorted(kw_freq.items(), key=lambda x: -x[1])
    
    # Group by monster type
    mtype_groups = defaultdict(list)
    for e in shengui_entries:
        mtype_groups[e.get('monster_type', '未归类')].append(e)
    
    lines = ["# 《酉阳杂俎》神鬼妖魔怪描写对象提取报告（三校版）\n"]
    lines.append(f"> 基于{total}段全文分析，使用关键词规则从文本中自动提取\n\n---\n")
    lines.append(f"\n## 一、已分类为「神怪内容」的段落（{total_sgui}段）\n")
    lines.append(f"\n当前分类体系中，共覆盖 **{total_sgui}段**，分为{len(mtype_groups)}个怪物类型：\n")
    lines.append("| 怪物类型 | 段落数 |")
    lines.append("|----------|--------|")
    for mt in sorted(mtype_groups.keys(), key=lambda x: -len(mtype_groups[x])):
        lines.append(f"| {mt} | {len(mtype_groups[mt])} |")
    
    lines.append("\n---\n\n## 二、神怪关键词频次排行（Top 60）\n")
    lines.append("| 排名 | 关键词 | 次数 | | 排名 | 关键词 | 次数 |")
    lines.append("|------|--------|------|-|------|--------|------|")
    half = 30
    for i in range(half):
        left = f"| {i+1} | {sorted_kw_freq[i][0]} | {sorted_kw_freq[i][1]} |" if i < len(sorted_kw_freq) else "| | | |"
        j = i + half
        right = f"| {j+1} | {sorted_kw_freq[j][0]} | {sorted_kw_freq[j][1]} |" if j < len(sorted_kw_freq) else "| | | |"
        lines.append(f"{left} {right}")
    
    # Narrative theme distribution for shengui
    theme_dist = defaultdict(int)
    for e in shengui_entries:
        for t in e.get('narrative_themes', []):
            theme_dist[t] += 1
    
    lines.append("\n---\n\n## 三、神怪段落叙事主题分布\n")
    lines.append("| 叙事主题 | 段落数 |")
    lines.append("|----------|--------|")
    for t in sorted(theme_dist.keys(), key=lambda x: -theme_dist[x]):
        lines.append(f"| {t} | {theme_dist[t]} |")
    
    # Detailed listing by monster type
    lines.append("\n---\n\n## 四、按怪物类型分组\n")
    for mt in sorted(mtype_groups.keys(), key=lambda x: -len(mtype_groups[x])):
        entries = mtype_groups[mt]
        lines.append(f"\n### {mt}（{len(entries)}段）\n")
        for e in entries[:15]:
            themes = '、'.join(e.get('narrative_themes', []))
            lines.append(f"- **{e['vol_title']}** | {themes} | {e['text_brief']}")
        if len(entries) > 15:
            lines.append(f"- ……（共{len(entries)}段）")
    
    with open(os.path.join(OUTPUT_DIR, "神鬼妖魔怪描写对象提取报告.md"), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"\n全部文档生成完毕！")
    print(f"输出目录: {OUTPUT_DIR}")

if __name__ == '__main__':
    main()
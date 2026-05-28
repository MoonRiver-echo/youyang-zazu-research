# -*- coding: utf-8 -*-
"""
酉阳杂俎 自动分类脚本
基于关键词规则对全量段落进行：
1. 神怪内容识别 (has_supernatural)
2. 神怪深度分类 (title, brief, monster_type, themes, shengui_keywords)
3. 统计信息
"""

import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

INPUT_FILE = r'C:\Users\lx\Desktop\前期准备\parsed_paragraphs.json'
OUTPUT_FILE = r'C:\Users\lx\Desktop\前期准备\classified_youyang.json'

# ---- 神怪关键词体系 ----

# 核心神怪关键词（出现任一即判断为神怪内容）
CORE_SHENGUI_KEYWORDS = [
    '神', '鬼', '仙', '妖', '魔', '魅', '怪', '精', '佛', '僧', '道',
    '龙', '蛟', '凤', '麒麟', '狐', '变', '尸解', '冥', '魂', '魄',
    '地狱', '天帝', '菩萨', '袈裟', '符', '咒', '术士', '法师', '天师',
    '巫', '真人', '飞行', '变化', '异人', '天翁', '灶神', '帝江',
    '不空', '万回', '一行', '罗公远', '邢和璞', '翟天师',
]

# 次级神怪关键词（需要结合上下文判断，权重较低）
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

# 叙事类别自动分配（基于卷名）
VOLUME_CATEGORIES = {
    "序": "史料序跋",
    "忠志": "帝王纪事",
    "礼异": "礼俗制度",
    "天咫": "天文地理",
    "玉格": "佛道异闻",
    "壶史": "神仙方术",
    "贝编": "佛道异闻",
    "境异": "异境异域",
    "喜兆": "征兆占验",
    "祸兆": "征兆占验",
    "物革": "事物怪变",
    "诡习": "器艺技法",
    "怪术": "术法幻术",
    "艺绝": "器艺技法",
    "器奇": "器物名物",
    "乐": "器艺技法",
    "酒食": "饮食医药",
    "医": "饮食医药",
    "黥": "礼俗制度",
    "雷": "天文地理",
    "梦": "梦兆占验",
    "事感": "精诚感应",
    "盗侠": "侠盗刺客",
    "物异": "异物异象",
    "广知": "广知博物",
    "语资": "语资谈助",
    "冥迹": "幽冥冥迹",
    "尸穸": "丧葬礼俗",
    "诺皋记上": "异闻志怪",
    "诺皋记下": "异闻志怪",
    "广动植之一（并序）": "动植物谱录",
    "广动植之二": "动植物谱录",
    "广动植之三": "动植物谱录",
    "广动植之四": "动植物谱录",
    "肉攫部": "器艺技法",
    "支诺皋上": "异闻志怪",
    "支诺皋中": "异闻志怪",
    "支诺皋下": "异闻志怪",
    "贬误": "知识考辨",
    "寺塔记上": "佛寺塔庙",
    "寺塔记下": "佛寺塔庙",
    "金刚经鸠异": "佛道异闻",
    "支动": "动植物谱录",
    "支植上": "动植物谱录",
    "支植下": "动植物谱录",
}

# 神怪卷（这些卷的内容几乎全是神怪）
SHENGUI_VOLUMES = {
    "诺皋记上", "诺皋记下", "支诺皋上", "支诺皋中", "支诺皋下"
}

# 神怪卷的段落几乎都是神怪
MOSTLY_SHENGUI_VOLUMES = {
    "玉格", "壶史", "贝编", "境异", "怪术", "冥迹", "尸穸"
}

# monster_type 关键词映射
MONSTER_TYPE_KEYWORDS = {
    "神话异兽": ['帝江', '刑天', '浑水敦', '异兽', '怪兽', '大蛇', '毒龙', '飞头', '夜叉'],
    "神仙志怪": ['仙', '真人', '天翁', '天帝', '灶神', '得道', '飞升', '修炼', '羽化', '尸解'],
    "妖怪变形": ['变', '妖', '魅', '化', '变形', '化为人', '化为', '幻', '精'],
    "降妖伏魔": ['降', '伏', '斩', '收', '制服', '破', '驱除', '禳'],
    "民俗神灵": ['灶神', '门神', '土地', '城隍', '河伯', '山神', '风伯', '雨师', '雷公'],
    "佛道灵异": ['佛', '僧', '道', '寺', '观', '菩萨', '罗汉', '经', '咒', '法', '舍利', '灵光'],
    "冥界报应": ['冥', '地狱', '阎罗', '判官', '鬼', '阴间', '报应', '还魂', '转世'],
    "梦兆占验": ['梦', '兆', '谶', '占', '卜', '祈', '瑞'],
    "术法幻术": ['术', '法', '幻', '隐形', '变化', '咒', '符', '法术', '奇术'],
    "异域怪物": ['异域', '波斯', '西域', '天竺', '外国', '蛮', '胡'],
    "尸解变化": ['尸解', '尸', '不朽', '不腐', '僵尸'],
    "事物怪变": ['变', '化为', '化', '忽变', '怪变', '异变'],
}

# theme 映射
THEME_KEYWORDS = {
    "动物": {
        "鸟类": ['鸟', '鹊', '鹰', '鹤', '雁', '燕', '雀', '凤', '鸱', '鸢', '雉', '鸦', '乌', '鹅', '鹭', '鸽', '鹦'],
        "兽类": ['虎', '鹿', '马', '牛', '羊', '犬', '狗', '豕', '猪', '象', '狮', '豹', '熊', '猴', '猿', '狐', '兔', '鼠', '猫', '猫', '狼'],
        "鱼类": ['鱼', '鲤', '鲫', '鲈', '鳖', '龟', '鳗', '鳝', '鲙'],
        "爬行": ['蛇', '蜥', '龟', '鳄', '蜃'],
        "昆虫": ['虫', '蚁', '蜂', '蝶', '蛾', '蝉', '蜻', '萤', '蝗', '螳', '蛛'],
        "神物": ['龙', '蛟', '螭', '虬', '凤', '麟', '麒麟'],
    },
    "佛道信仰": {
        "佛": ['佛', '释', '菩萨', '罗汉', '涅槃'],
        "道": ['道', '老君', '太上', '太极', '真人'],
        "僧": ['僧', '沙弥', '比丘', '禅师', '上人'],
        "仙": ['仙', '仙人', '飞仙', '神仙'],
        "经法": ['经', '法', '戒', '禅', '论'],
        "梵": ['梵', '天竺', '西域'],
    },
    "丧葬冥界": {
        "葬": ['葬', '墓', '棺', '坟', '椁'],
        "冥": ['冥', '阴间', '地府', '黄泉'],
        "鬼": ['鬼', '亡魂', '魂魄', '游魂'],
        "尸": ['尸', '尸解', '不朽', '僵尸'],
    },
    "建筑寺塔": {
        "宫": ['宫', '宫殿', '皇宫'],
        "殿": ['殿', '堂', '阁'],
        "寺": ['寺', '寺庙', '兰若', '伽蓝'],
        "观": ['观', '道观', '宫观'],
        "城楼": ['城', '楼', '门', '墙'],
    },
    "器物技艺": {
        "武器": ['剑', '刀', '戟', '戈', '矛', '弓', '箭'],
        "镜": ['镜'],
        "用具": ['盘', '碗', '杯', '鼎', '壶', '瓶', '匣'],
        "衣饰": ['衣', '冠', '带', '履', '衾', '裘'],
        "乐器": ['鼓', '钟', '磬', '琴', '瑟', '箫', '笛', '竽'],
    },
    "神怪妖魅": {
        "精": ['精', '妖精', '狐精', '蛇精'],
        "魅": ['魅', '魑魅', '魍魉'],
        "妖": ['妖', '妖怪', '妖精'],
        "魔": ['魔', '妖魔', '天魔'],
    },
    "饮食医药": {
        "食": ['食', '煮', '饮', '饼', '羹', '粥', '脍', '鲙'],
        "药": ['药', '丹', '丸', '散', '汤', '医', '治'],
        "酒": ['酒', '酿', '醪', '醑', '醅'],
        "茶": ['茶', '茗'],
    },
    "梦兆占验": {
        "梦": ['梦', '入梦', '托梦', '梦中'],
    },
    "异域物产": {
        "异国": ['波斯', '西域', '天竺', '大食', '突厥', '龟兹', '于阗', '拂林'],
    },
    "人物政事": {
        "帝王": ['帝', '上', '天子', '诏', '敕', '玄宗', '太宗', '高宗', '肃宗', '代宗'],
        "人物": ['成式', '公', '卿', '大夫', '刺史', '令', '尉'],
    },
    "天文地理": {
        "日": ['日', '月', '星', '辰', '天象', '蚀'],
        "泉": ['泉', '井', '河', '江', '海', '湖'],
    },
}


def is_supernatural(text, volume_title, narrative_category):
    """判断段落是否包含神怪内容"""
    # 神怪核心卷的段落默认为神怪
    vol_name = volume_title.split('·')[-1] if '·' in volume_title else volume_title
    if vol_name in SHENGUI_VOLUMES:
        return True
    
    # 检查核心神怪关键词
    core_count = 0
    for kw in CORE_SHENGUI_KEYWORDS:
        if kw in text:
            core_count += 1
            if core_count >= 2:
                return True
    
    # 检查次级神怪关键词
    secondary_count = 0
    for kw in SECONDARY_SHENGUI_KEYWORDS:
        if kw in text:
            secondary_count += 1
            if secondary_count >= 3:
                return True
    
    # 核心关键词1个 + 次级1个也可以
    if core_count >= 1 and secondary_count >= 1:
        return True
    
    # 特定卷的分类优先
    if narrative_category in ["佛道异闻", "神仙方术", "异闻志怪", "幽冥冥迹", "丧葬礼俗", "梦兆占验", "征兆占验", "事物怪变", "术法幻术", "异物异象", "异境异域"]:
        # 这些卷的内容本身就偏神怪，降低阈值
        if core_count >= 1:
            return True
        if secondary_count >= 2:
            return True
    
    return False


def determine_monster_type(text):
    """确定怪物类型"""
    scores = {}
    for mtype, keywords in MONSTER_TYPE_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw in text:
                score += 1
        if score > 0:
            scores[mtype] = score
    
    if not scores:
        # 默认类型
        if '佛' in text or '僧' in text or '道' in text:
            return "佛道灵异"
        elif '鬼' in text or '冥' in text:
            return "冥界报应"
        elif '梦' in text:
            return "梦兆占验"
        elif '变' in text or '化' in text:
            return "妖怪变形"
        else:
            return "神仙志怪"
    
    return max(scores, key=scores.get)


def determine_themes(text):
    """确定主题分类"""
    themes = []
    for broad, subcats in THEME_KEYWORDS.items():
        for sub, keywords in subcats.items():
            for kw in keywords:
                if kw in text:
                    themes.append({
                        "broad_category": broad,
                        "level1_subject": sub,
                        "level2_subject": sub,
                        "specific_subject": sub
                    })
                    break  # Only add once per subcategory
            if len(themes) >= 3:
                break
        if len(themes) >= 3:
            break
    
    # Ensure at least one theme
    if not themes:
        themes.append({
            "broad_category": "人物政事",
            "level1_subject": "人物",
            "level2_subject": "人物",
            "specific_subject": "人物"
        })
    
    return themes


def extract_shengui_keywords(text):
    """提取神怪关键词"""
    found = []
    all_keywords = CORE_SHENGUI_KEYWORDS + SECONDARY_SHENGUI_KEYWORDS
    for kw in all_keywords:
        if kw in text and kw not in found:
            found.append(kw)
    return found


def generate_title(text, max_len=8):
    """从文本内容生成简短标题"""
    # Try to find a name or key phrase
    # Look for proper names
    name_patterns = [
        r'([^\x00-\x7F]{2,4})(?=[，。曰为]',
        r'曰["""]([^"""]+)["""]',
    ]
    
    # Simplify: use first meaningful clause
    # Remove parenthetical notes
    clean = re.sub(r'[（\(][^）\)]+[）\)]', '', text)
    clean = re.sub(r'[（\(一][^）\)]*[）\)]', '', clean)
    
    # Take first sentence fragment
    for sep in ['。', '，', '：']:
        if sep in clean:
            fragment = clean[:clean.index(sep)]
            if len(fragment) >= 4:
                # Try to extract key person or thing
                title = fragment[:max_len]
                return title
    
    return clean[:max_len]


def generate_brief(text, max_len=80):
    """从文本内容生成摘要"""
    clean = re.sub(r'[（\(][^）\)]+[）\)]', '', text)
    clean = clean.replace('\n', ' ').strip()
    if len(clean) <= max_len:
        return clean
    return clean[:max_len] + '……'


def generate_translation_note():
    """生成翻译标记"""
    return "（AI生成，仅供参考）待补充"


def classify():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    paragraphs = data['paragraphs']
    classified = []
    shengui_count = 0
    
    # Stats
    category_stats = {}
    monster_type_stats = {}
    theme_stats = {}
    keyword_freq = {}
    
    for p in paragraphs:
        text = p['original_text']
        vol_title = p['volume_title']
        # Determine narrative_category from volume_title
        vol_name = vol_title.split('·')[-1] if '·' in vol_title else vol_title
        cat = VOLUME_CATEGORIES.get(vol_name, "未分类")
        
        # Determine if supernatural
        has_sgui = is_supernatural(text, vol_title, cat)
        
        entry = {
            "pid": p['pid'],
            "volume_num": p['volume_num'],
            "volume_title": p['volume_title'],
            "section_title": p.get('section_title'),
            "narrative_category": cat,
            "has_supernatural": has_sgui,
            "original_text": text,
            "text_length": p['text_length'],
        }
        
        if has_sgui:
            shengui_count += 1
            mtype = determine_monster_type(text)
            themes = determine_themes(text)
            kw_list = extract_shengui_keywords(text)
            
            entry["title"] = generate_title(text)
            entry["brief"] = generate_brief(text)
            entry["monster_type"] = mtype
            entry["themes"] = themes
            entry["shengui_keywords"] = kw_list
            entry["keyword_count"] = len(kw_list)
            entry["translation"] = generate_translation_note()
            
            # Stats
            monster_type_stats[mtype] = monster_type_stats.get(mtype, 0) + 1
            for t in themes:
                tkey = f"{t['broad_category']}/{t['specific_subject']}"
                theme_stats[tkey] = theme_stats.get(tkey, 0) + 1
            for kw in kw_list:
                keyword_freq[kw] = keyword_freq.get(kw, 0) + 1
        
        # Category stats
        category_stats[cat] = category_stats.get(cat, 0) + 1
        
        classified.append(entry)
    
    # Build output
    total = len(classified)
    
    # Sort keyword stats
    keyword_sorted = sorted(keyword_freq.items(), key=lambda x: -x[1])[:40]
    theme_sorted = sorted(theme_stats.items(), key=lambda x: -x[1])[:20]
    
    output = {
        "metadata": {
            "title": "酉阳杂俎",
            "version": "二校版（自动分类）",
            "total_paragraphs": total,
            "total_shengui_paragraphs": shengui_count,
            "classification_method": "基于关键词规则的自动分类",
            "narrative_stats": category_stats,
            "monster_type_stats": monster_type_stats,
            "theme_frequency": [{"theme": k, "count": v} for k, v in theme_sorted],
            "keyword_frequency": [{"keyword": k, "count": v} for k, v in keyword_sorted],
            "translation_note": "以上白话译文由AI生成，仅供参考"
        },
        "stories": [e for e in classified if e['has_supernatural']],
        "paragraphs": classified
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"Total paragraphs: {total}")
    print(f"Supernatural paragraphs: {shengui_count}")
    print(f"Non-supernatural: {total - shengui_count}")
    print(f"\nNarrative categories:")
    for cat, count in sorted(category_stats.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        print(f"  {cat}: {count} ({pct:.1f}%)")
    
    print(f"\nMonster types:")
    for mt, count in sorted(monster_type_stats.items(), key=lambda x: -x[1]):
        print(f"  {mt}: {count}")
    
    print(f"\nTop 20 themes:")
    for t, count in theme_sorted[:20]:
        print(f"  {t}: {count}")
    
    print(f"\nTop 20 keywords:")
    for kw, count in keyword_sorted[:20]:
        print(f"  {kw}: {count}")
    
    print(f"\nSaved to {OUTPUT_FILE}")


if __name__ == '__main__':
    classify()
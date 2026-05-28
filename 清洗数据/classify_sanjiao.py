#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
酉阳杂俎 三校版 自动分类脚本

输入: 酉阳杂俎-三校.md
输出: 
  1. 酉阳杂俎-三校-分类总览.md (markdown 分类结果)
  2. 酉阳杂俎-三校-神怪分类.md (神怪段落深度分类)

分类维度:
  A. 叙事类别 (narrative_category) - 基于卷名自动分配
  B. 描写对象 (description_subject) - 关键词识别
  C. 神怪识别 (has_supernatural) - 关键词规则
  D. 神怪深度分类:
    - monster_type: 怪物类型
    - narrative_theme: 叙事主题 (死者复活、迷路返回时间流逝 等)
    - themes: 描写主题
"""

import re
import os
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\lx\Desktop\前期准备"
INPUT_FILE = os.path.join(BASE_DIR, "清洗数据", "酉阳杂俎-三校.md")
OUTPUT_DIR = os.path.join(BASE_DIR, "清洗数据")
OUTPUT_OVERVIEW = os.path.join(OUTPUT_DIR, "酉阳杂俎-三校-分类总览.md")
OUTPUT_SHENGUI = os.path.join(OUTPUT_DIR, "酉阳杂俎-三校-神怪分类.md")

# ============================================================
# A. 叙事类别映射（基于卷名）
# ============================================================
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
    "广动植之一": "动植物谱录",
    "广动植之二": "动植物谱录",
    "广动植之三": "动植物谱录",
    "广动植类之四": "动植物谱录",
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

# B. 描写对象分类关键词
DESCRIPTION_SUBJECT_KEYWORDS = {
    "人物志": ['人', '士', '官', '将', '臣', '帝', '王', '公', '卿', '僧', '道', '尼', '医', '匠', '妓', '侠', '盗'],
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

# ============================================================
# C. 神怪识别关键词
# ============================================================
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

SHENGUI_VOLUMES = {"诺皋记上", "诺皋记下", "支诺皋上", "支诺皋中", "支诺皋下"}
MOSTLY_SHENGUI_VOLUMES = {"玉格", "壶史", "贝编", "境异", "怪术", "冥迹", "尸穸"}

# D1. 怪物类型关键词
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

# D2. 叙事主题深度分类关键词
NARRATIVE_THEME_KEYWORDS = {
    # 生死类
    "死者复活": ['复生', '还魂', '再生', '复苏', '起死', '再生', '更生', '苏', '魂归', '且生', '命虽绝', '复苏'],
    "鬼魂还阳": ['还阳', '魂归', '鬼魂', '亡魂', '游魂', '魂魄', '附身', '托生', '冥归'],
    "生死边界": ['冥', '阴间', '地府', '黄泉', '幽冥', '阳间', '还魂', '入冥', '赴冥'],
    "丧葬再生": ['葬', '墓', '冢', '棺', '椁', '殉', '陪葬', '祭', '迁葬', '发冢'],
    
    # 时间空间类
    "迷路返回时间流逝": ['迷', '迷路', '失路', '歧路', '不知所之', '寻路', '归路', '归', '还家', '不得归'],
    "时间错位": ['经年', '数日', '忽觉', '须臾', '瞬息', '岁月', '经宿', '遽', '倏忽', '恍然'],
    "空间异变": ['忽见', '异境', '异地', '仙境', '洞天', '福地', '幻境', '迷途'],
    "天上人间": ['天宫', '上天', '天帝', '仙界', '降世', '天上', '人间', '下凡'],
    
    # 变形类
    "人兽互变": ['化为人', '变为', '变形', '变', '化', '幻化', '人形', '兽形', '狐变', '蛇变'],
    "物怪变形": ['化为', '忽变', '变形', '物怪', '成精', '作怪', '妖怪'],
    "妖魅惑人": ['魅', '惑', '迷', '妖', '淫', '色', '幻', '惑人', '迷乱'],
    
    # 修仙佛道类
    "修道成仙": ['修炼', '得道', '飞升', '仙', '真人', '羽化', '辟谷', '炼丹', '黄白'],
    "僧尼异事": ['僧', '尼', '寺', '佛', '禅', '经', '咒', '戒', '钵', '袈裟', '斋'],
    "法术幻术": ['术', '法', '幻', '隐形', '变化', '咒', '符', '奇术', '遁', '遁术'],
    "因果报应": ['报应', '因果', '善报', '恶报', '罚', '赎', '劫', '还报', '业'],
    "佛法灵验": ['佛', '观音', '菩萨', '经', '念', '诵', '灵验', '显灵', '护法'],
    
    # 占卜梦兆类
    "梦兆应验": ['梦', '入梦', '托梦', '梦中', '兆', '应', '征', '谶', '吉梦', '凶梦'],
    "占卜预言": ['占', '卜', '谶', '预言', '相', '算', '推', '卜筮'],
    "祥瑞灾异": ['瑞', '祥', '灾', '异', '天象', '蚀', '蝗', '旱', '水', '祥瑞'],
    
    # 异物异象类
    "异物奇珍": ['异', '奇', '宝', '珍', '怪', '异物', '奇珍', '珍宝', '珠', '玉'],
    "动植怪变": ['变异', '怪', '异', '畸形', '双头', '无目', '变化'],
    "自然怪象": ['风', '雨', '雷', '电', '虹', '雾', '霜', '异', '怪', '天变'],
    
    # 侠盗奇人类
    "侠客义行": ['侠', '义', '刺客', '飞天夜叉', '盗', '劫', '杀', '报恩', '报仇'],
    "奇人异能": ['异人', '奇术', '绝技', '高手', '异能', '神力', '奇才'],
    "隐逸高人": ['隐', '逸', '山人', '处士', '高人', '道士', '先生'],
    
    # 情感伦理类
    "忠孝节义": ['忠', '孝', '节', '义', '烈', '贞', '廉', '仁', '礼'],
    "冤屈报应": ['冤', '屈', '报', '雪', '伸', '冤魂', '复仇'],
    "情爱奇闻": ['婚', '嫁', '妻', '妾', '情', '恋', '美', '色', '缘'],
}

# ============================================================
# 分类函数
# ============================================================

def parse_sanjiao(content):
    """解析三校markdown，返回 [(卷名, [段落])] 列表"""
    lines = content.split('\n')
    volumes = []
    current_vol = None
    current_paras = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('## '):
            if current_vol and current_paras:
                volumes.append((current_vol, current_paras))
            current_vol = stripped[3:].strip()
            current_paras = []
        elif len(stripped) > 5:  # 过滤太短的行
            current_paras.append(stripped)
    
    if current_vol and current_paras:
        volumes.append((current_vol, current_paras))
    
    return volumes


def get_narrative_category(vol_title):
    """从卷名获取叙事类别"""
    # 提取篇名（去掉卷号）
    if '·' in vol_title:
        name = vol_title.split('·', 1)[1]
    elif '·' in vol_title:
        name = vol_title.split('·', 1)[1]
    else:
        name = vol_title
    
    # 去掉续集标记
    name = name.replace('续·', '').replace('续', '')
    
    # 模糊匹配
    for key, cat in VOLUME_CATEGORIES.items():
        if key in name or name in key:
            return cat
    
    # 特殊处理
    if '广动植' in name:
        return '动植物谱录'
    if '诺皋' in name:
        return '异闻志怪'
    if '支诺皋' in name:
        return '异闻志怪'
    if '寺塔' in name:
        return '佛寺塔庙'
    if '支植' in name or '支动' in name:
        return '动植物谱录'
    
    return '未分类'


def get_volume_short_name(vol_title):
    """提取卷名短名"""
    if '·' in vol_title:
        return vol_title.split('·', 1)[1]
    elif '·' in vol_title:
        return vol_title.split('·', 1)[1]
    return vol_title.replace('续·', '')


def is_supernatural(text, vol_short_name, narrative_category):
    """判断段落是否包含神怪内容"""
    # 神怪核心卷
    if vol_short_name in SHENGUI_VOLUMES:
        return True
    
    # 核心关键词
    core_count = sum(1 for kw in CORE_SHENGUI_KEYWORDS if kw in text)
    if core_count >= 2:
        return True
    
    # 次级关键词
    secondary_count = sum(1 for kw in SECONDARY_SHENGUI_KEYWORDS if kw in text)
    if secondary_count >= 3:
        return True
    
    # 核心1 + 次级1
    if core_count >= 1 and secondary_count >= 1:
        return True
    
    # 特定卷降低阈值
    if narrative_category in ["佛道异闻", "神仙方术", "异闻志怪", "幽冥冥迹", "丧葬礼俗",
                               "梦兆占验", "征兆占验", "事物怪变", "术法幻术", "异物异象", "异境异域"]:
        if core_count >= 1:
            return True
        if secondary_count >= 2:
            return True
    
    return False


def determine_monster_type(text):
    """确定怪物类型"""
    scores = {}
    for mtype, keywords in MONSTER_TYPE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[mtype] = score
    
    if not scores:
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


def determine_narrative_themes(text):
    """确定叙事主题（深度分类）"""
    themes = []
    for theme_name, keywords in NARRATIVE_THEME_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw in text)
        if count >= 2:  # 至少2个关键词匹配才认定
            themes.append(theme_name)
        elif count == 1 and len(keywords) <= 3:  # 短列表中的关键词权重高
            themes.append(theme_name)
    
    if not themes:
        # 退化：用最少关键词
        for theme_name, keywords in NARRATIVE_THEME_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                themes.append(theme_name)
                if len(themes) >= 2:
                    break
    
    return themes


def determine_description_subjects(text):
    """确定描写对象"""
    subjects = []
    for subj, keywords in DESCRIPTION_SUBJECT_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw in text)
        if count >= 3:
            subjects.append(subj)
    
    if not subjects:
        # 降低阈值
        for subj, keywords in DESCRIPTION_SUBJECT_KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in text)
            if count >= 2:
                subjects.append(subj)
                if len(subjects) >= 2:
                    break
    
    return subjects if subjects else ["事迹叙述"]


def extract_keywords(text):
    """提取神怪关键词"""
    found = []
    all_kw = CORE_SHENGUI_KEYWORDS + SECONDARY_SHENGUI_KEYWORDS
    for kw in all_kw:
        if kw in text and kw not in found:
            found.append(kw)
    return found


def generate_title(text, max_len=10):
    """从文本生成简短标题"""
    clean = re.sub(r'[（\(][^）\)]+[）\)]', '', text)
    for sep in ['。', '，', '：', '曰']:
        if sep in clean:
            idx = clean.index(sep)
            if idx >= 4:
                fragment = clean[:idx]
                return fragment[:max_len]
    return clean[:max_len]


def generate_brief(text, max_len=100):
    """生成摘要"""
    clean = re.sub(r'[（\(][^）\)]+[）\)]', '', text)
    clean = clean.replace('\n', ' ').strip()
    if len(clean) <= max_len:
        return clean
    return clean[:max_len] + '……'


# ============================================================
# 主函数
# ============================================================

def classify():
    print("=" * 60)
    print("酉阳杂俎 三校版 自动分类")
    print("=" * 60)
    
    # 读取三校
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    volumes = parse_sanjiao(content)
    print(f"\n解析到 {len(volumes)} 卷")
    
    total_paras = 0
    total_shengui = 0
    all_entries = []
    shengui_entries = []
    
    # 统计
    category_stats = defaultdict(int)
    monster_type_stats = defaultdict(int)
    narrative_theme_stats = defaultdict(int)
    desc_subject_stats = defaultdict(int)
    
    pid = 0
    for vol_title, paras in volumes:
        vol_short = get_volume_short_name(vol_title)
        category = get_narrative_category(vol_title)
        
        for para in paras:
            pid += 1
            total_paras += 1
            category_stats[category] += 1
            
            has_sgui = is_supernatural(para, vol_short, category)
            
            # 描写对象
            desc_subjects = determine_description_subjects(para)
            for ds in desc_subjects:
                desc_subject_stats[ds] += 1
            
            entry = {
                "pid": pid,
                "volume_title": vol_title,
                "volume_short": vol_short,
                "narrative_category": category,
                "description_subjects": desc_subjects,
                "has_supernatural": has_sgui,
                "text_preview": para[:60] + ('……' if len(para) > 60 else ''),
                "text_length": len(para),
            }
            
            if has_sgui:
                total_shengui += 1
                mtype = determine_monster_type(para)
                n_themes = determine_narrative_themes(para)
                kw_list = extract_keywords(para)
                
                entry["monster_type"] = mtype
                entry["narrative_themes"] = n_themes
                entry["shengui_keywords"] = kw_list
                entry["title"] = generate_title(para)
                entry["brief"] = generate_brief(para)
                
                monster_type_stats[mtype] += 1
                for t in n_themes:
                    narrative_theme_stats[t] += 1
                
                shengui_entries.append(entry)
            
            all_entries.append(entry)
    
    # ============================================================
    # 输出分类总览 (markdown)
    # ============================================================
    lines = []
    lines.append("# 酉阳杂俎 三校版 分类总览\n")
    lines.append(f"- 总段落数: **{total_paras}**")
    lines.append(f"- 神怪段落数: **{total_shengui}**")
    lines.append(f"- 非神怪段落: **{total_paras - total_shengui}**")
    lines.append(f"- 分类方法: 基于关键词规则的Python自动分类\n")
    
    # 叙事类别统计
    lines.append("## 一、叙事类别分布\n")
    lines.append("| 叙事类别 | 段落数 | 占比 |")
    lines.append("|----------|--------|------|")
    for cat, count in sorted(category_stats.items(), key=lambda x: -x[1]):
        pct = count / total_paras * 100
        lines.append(f"| {cat} | {count} | {pct:.1f}% |")
    lines.append("")
    
    # 描写对象统计
    lines.append("## 二、描写对象分布\n")
    lines.append("| 描写对象 | 段落数 | 占比 |")
    lines.append("|----------|--------|------|")
    for subj, count in sorted(desc_subject_stats.items(), key=lambda x: -x[1]):
        pct = count / total_paras * 100
        lines.append(f"| {subj} | {count} | {pct:.1f}% |")
    lines.append("")
    
    # 各卷段落统计
    lines.append("## 三、各卷段落数\n")
    lines.append("| 卷名 | 叙事类别 | 段落数 | 神怪段落数 |")
    lines.append("|------|----------|--------|-----------|")
    for vol_title, paras in volumes:
        vol_short = get_volume_short_name(vol_title)
        cat = get_narrative_category(vol_title)
        sgui_count = sum(1 for p in paras if is_supernatural(p, vol_short, cat))
        lines.append(f"| {vol_title} | {cat} | {len(paras)} | {sgui_count} |")
    lines.append("")
    
    # 神怪段落明细
    lines.append("## 四、神怪段落明细\n")
    lines.append("| # | 卷 | 怪物类型 | 叙事主题 | 标题 | 摘要 |")
    lines.append("|---|-----|----------|----------|------|------|")
    for i, e in enumerate(shengui_entries, 1):
        themes = '、'.join(e.get('narrative_themes', []))
        title = e.get('title', '')
        brief = e.get('brief', '')[:50] + ('……' if len(e.get('brief', '')) > 50 else '')
        lines.append(f"| {i} | {e['volume_title']} | {e.get('monster_type', '')} | {themes} | {title} | {brief} |")
    lines.append("")
    
    # 神怪统计
    lines.append("## 五、神怪统计\n")
    lines.append("### 怪物类型分布\n")
    lines.append("| 怪物类型 | 段落数 |")
    lines.append("|----------|--------|")
    for mt, count in sorted(monster_type_stats.items(), key=lambda x: -x[1]):
        lines.append(f"| {mt} | {count} |")
    lines.append("")
    
    lines.append("### 叙事主题分布\n")
    lines.append("| 叙事主题 | 段落数 |")
    lines.append("|----------|--------|")
    for theme, count in sorted(narrative_theme_stats.items(), key=lambda x: -x[1]):
        lines.append(f"| {theme} | {count} |")
    lines.append("")
    
    overview_md = '\n'.join(lines)
    with open(OUTPUT_OVERVIEW, 'w', encoding='utf-8') as f:
        f.write(overview_md)
    print(f"\n分类总览已保存到: {OUTPUT_OVERVIEW}")
    
    # ============================================================
    # 输出神怪深度分类 (markdown)
    # ============================================================
    sg_lines = []
    sg_lines.append("# 酉阳杂俎 三校版 神怪段落深度分类\n")
    sg_lines.append(f"- 神怪段落总数: **{total_shengui}**")
    sg_lines.append(f"- 占总段落比例: **{total_shengui / total_paras * 100:.1f}%**\n")
    
    # 按叙事主题分组
    sg_lines.append("## 一、按叙事主题分类\n")
    
    theme_groups = defaultdict(list)
    for e in shengui_entries:
        for theme in e.get('narrative_themes', ['未归类']):
            theme_groups[theme].append(e)
    
    for theme_name in sorted(theme_groups.keys(), key=lambda x: -len(theme_groups[x])):
        entries = theme_groups[theme_name]
        sg_lines.append(f"### {theme_name}（{len(entries)}段）\n")
        for e in entries:
            brief = e.get('brief', '')[:80] + ('……' if len(e.get('brief', '')) > 80 else '')
            kw = '、'.join(e.get('shengui_keywords', [])[:5])
            sg_lines.append(f"- **{e['volume_title']}** | {e.get('monster_type', '')} | {brief}")
            if kw:
                sg_lines.append(f"  - 关键词: {kw}")
        sg_lines.append("")
    
    # 按怪物类型分组
    sg_lines.append("## 二、按怪物类型分类\n")
    monster_groups = defaultdict(list)
    for e in shengui_entries:
        monster_groups[e.get('monster_type', '未归类')].append(e)
    
    for mtype in sorted(monster_groups.keys(), key=lambda x: -len(monster_groups[x])):
        entries = monster_groups[mtype]
        sg_lines.append(f"### {mtype}（{len(entries)}段）\n")
        for e in entries:
            brief = e.get('brief', '')[:80] + ('……' if len(e.get('brief', '')) > 80 else '')
            themes = '、'.join(e.get('narrative_themes', []))
            sg_lines.append(f"- **{e['volume_title']}** | {themes} | {brief}")
        sg_lines.append("")
    
    # 按卷分组索引
    sg_lines.append("## 三、按卷索引\n")
    vol_groups = defaultdict(list)
    for e in shengui_entries:
        vol_groups[e['volume_title']].append(e)
    
    for vol_title in sorted(vol_groups.keys()):
        entries = vol_groups[vol_title]
        sg_lines.append(f"### {vol_title}（{len(entries)}段神怪）\n")
        for e in entries:
            brief = e.get('brief', '')[:70] + ('……' if len(e.get('brief', '')) > 70 else '')
            sg_lines.append(f"- [{e.get('monster_type', '')}] {e.get('narrative_themes', [])} — {brief}")
        sg_lines.append("")
    
    shengui_md = '\n'.join(sg_lines)
    with open(OUTPUT_SHENGUI, 'w', encoding='utf-8') as f:
        f.write(shengui_md)
    print(f"神怪分类已保存到: {OUTPUT_SHENGUI}")
    
    # ============================================================
    # 打印统计
    # ============================================================
    print(f"\n{'='*60}")
    print(f"分类统计")
    print(f"{'='*60}")
    print(f"总段落: {total_paras}")
    print(f"神怪段落: {total_shengui} ({total_shengui/total_paras*100:.1f}%)")
    print(f"非神怪: {total_paras - total_shengui}")
    print(f"\n叙事类别:")
    for cat, count in sorted(category_stats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count} ({count/total_paras*100:.1f}%)")
    print(f"\n怪物类型:")
    for mt, count in sorted(monster_type_stats.items(), key=lambda x: -x[1]):
        print(f"  {mt}: {count}")
    print(f"\n叙事主题 Top 20:")
    for theme, count in sorted(narrative_theme_stats.items(), key=lambda x: -x[1])[:20]:
        print(f"  {theme}: {count}")


if __name__ == '__main__':
    classify()
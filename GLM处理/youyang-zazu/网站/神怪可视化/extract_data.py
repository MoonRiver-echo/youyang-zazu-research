#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提取诺皋记相关数据，用于神怪可视化网站"""
import sqlite3, json, re, sys
from pathlib import Path

DB_PATH = Path(r"C:\Users\lx\Desktop\前期准备\GLM处理\youyang_zazu.db")

# 选定的5篇诺皋记故事 paragraph_id
SELECTED_STORIES = [
    "V14-P003",  # 帝江 - 六足重翼无面目的神兽
    "V14-P006",  # 天翁张坚 - 凡人窃天帝之位
    "V14-P010",  # 灶神 - 灶神的真面目与家族
    "V14-P014",  # 古龟兹国王降龙 - 降龙故事
    "V15-P001",  # 骨珠化人 - 食鱼吐骨珠化人的恐怖变形
]

def parse_inline_annotations(text):
    """解析原文中的内联注释，返回 (cleaned_text, annotations_list)
    注释格式: (一曰...) 或 {{...}} 
    """
    annotations = []
    counter = [0]  # mutable counter
    
    def replace_annotation(m):
        counter[0] += 1
        note_id = f"note_{counter[0]}"
        note_text = m.group(1) or m.group(2)
        annotations.append({"id": note_id, "text": note_text.strip()})
        return f'<span class="annotation" data-note="{note_id}"></span>'
    
    # Match (一曰...) patterns and {{...}} patterns
    # First handle {{...}} patterns
    cleaned = re.sub(r'\{\{([^}]+)\}\}', lambda m: _make_annotation(m, annotations, counter), text)
    # Then handle (...一曰...) patterns - be careful not to match normal parentheses
    cleaned = re.sub(r'（([^）]+一曰[^）]+)）', lambda m: _make_annotation(m, annotations, counter), cleaned)
    
    return cleaned, annotations

def _make_annotation(m, annotations, counter):
    counter[0] += 1
    note_id = f"note_{counter[0]}"
    note_text = m.group(1) if m.lastindex else m.group(0)
    annotations.append({"id": note_id, "text": note_text.strip()})
    return f'[{note_id}]'

def extract_story_data():
    """从数据库提取选定的5篇故事数据"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    stories = []
    for pid in SELECTED_STORIES:
        # 获取叙事分类数据
        cur.execute("""
            SELECT narrative_category, volume_title, volume_index, source, paragraph_id, text
            FROM narrative_detail WHERE paragraph_id = ?
        """, (pid,))
        narr_row = cur.fetchone()
        if not narr_row:
            print(f"WARNING: {pid} not found in narrative_detail", file=sys.stderr)
            continue
        
        # 获取主题分类数据
        cur.execute("""
            SELECT broad_category, level1_subject, level2_subject, specific_subject
            FROM theme_detail WHERE paragraph_id = ?
        """, (pid,))
        theme_rows = cur.fetchall()
        themes = [dict(r) for r in theme_rows]
        
        # 获取神怪关键词（从generate_web_data.py的逻辑）
        SHENGUI_KEYWORDS = [
            '鬼','鬼书','鬼官','鬼车鸟','鬼皂荚','鬼矢','鬼魅',
            '精','魅','妖','仙','魔','魂','魄','灵异','作祟',
            '神','神仙','真人','天师','法师','道人','道士','术士','异人',
            '天帝','玉帝','仙官','仙女','仙童','仙药','仙方','仙人',
            '玉女','金童','巫','巫术','巫师',
            '怪','妖怪','妖魅','鬼怪','精怪','妖精','狐精','蛇精','鱼精','树精','花精','石精',
            '狐','九尾','黄鼠狼','蟒','蛟','貔貅',
            '佛','菩萨','罗汉','梵','释','三界','须弥','袈裟','舍利','浮屠',
            '三尸','伏尸','尸解','白日升','飞升','修道','成仙','辟谷',
            '咒','符','法术','幻术','隐形','变形','变幻',
            '冥','酆都','阎罗','判官','阴司','阴间','黄泉','冥府',
            '地狱','鬼使','亡魂','白骨','骷髅',
            '异','变','变化','飞行','隐身','变形','现身','隐去','失所在',
            '龙','麒麟','凤','蟾蜍','月精','玉兔','嫦娥',
            '感应','灵验','显灵','降世','托生','转世','报应',
        ]
        
        text = narr_row['text'] or ''
        found_keywords = [kw for kw in SHENGUI_KEYWORDS if kw in text]
        
        # 定义故事中文名和概括
        story_info = {
            "V14-P003": {
                "title": "帝江·形夭与天帝争神",
                "brief": "天山有神名浑水敦，六足重翼无面目，实为帝江。形夭与帝争神，被断首葬于常羊山，以乳为目、脐为口，操干戚而舞。",
                "monster_type": "神话异兽",
            },
            "V14-P006": {
                "title": "天翁张坚窃车登天",
                "brief": "渔阳人张坚少不羁，蓄白雀得报天翁杀之未遂，后窃天翁车乘白龙登天，易百官，封白雀为上卿，以刘翁为太山太守主生死籍。",
                "monster_type": "神仙志怪",
            },
            "V14-P010": {
                "title": "灶神名隗状如美女",
                "brief": "灶神名隗，状如美女，又姓张名单字子郭，夫人字卿忌，有六女。常以月晦日上天白人罪状，大者夺纪三百日，小者夺算百日。其属神有天帝娇孙、天帝大夫等。",
                "monster_type": "民俗神灵",
            },
            "V14-P014": {
                "title": "古龟兹国王降伏毒龙",
                "brief": "龟兹国王阿主儿有神异，能降伏毒龙。龙化狮子，王即乘之。龙怒腾空至城北二十里，王叱之，龙惧神力降服，后常乘龙而行。",
                "monster_type": "降妖伏魔",
            },
            "V15-P001": {
                "title": "刘录事食鱼骨珠化人",
                "brief": "和州刘录事善食鱠，咯出骨珠子大如黑豆，置于瓯中顷刻长及人遂掴刘。良久各散走俱及后门相触翕成一人，乃刘也。自是恶鱠。",
                "monster_type": "妖怪变形",
            },
        }
        
        info = story_info.get(pid, {"title": pid, "brief": "", "monster_type": ""})
        
        story = {
            "pid": pid,
            "volume_title": narr_row['volume_title'],
            "narrative_category": narr_row['narrative_category'],
            "title": info["title"],
            "brief": info["brief"],
            "monster_type": info["monster_type"],
            "original_text": text,
            "themes": themes,
            "shengui_keywords": found_keywords,
            "keyword_count": len(found_keywords),
        }
        stories.append(story)
    
    conn.close()
    return stories

def extract_shengui_stats():
    """提取神怪分类统计数据"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # 叙事分类统计
    cur.execute("SELECT narrative_category, paragraph_count, absolute_percentage FROM narrative_stats ORDER BY paragraph_count DESC")
    narr_stats = [dict(r) for r in cur.fetchall()]
    
    # 主题分类统计
    cur.execute("SELECT broad_category, paragraph_count, absolute_percentage FROM theme_stats ORDER BY paragraph_count DESC")
    theme_stats = [dict(r) for r in cur.fetchall()]
    
    # 主题频次
    cur.execute("SELECT level1_subject, level2_subject, appearance_count FROM theme_frequency ORDER BY appearance_count DESC")
    theme_freq = [dict(r) for r in cur.fetchall()]
    
    # 诺皋记段落数量
    cur.execute("SELECT COUNT(*) as cnt FROM narrative_detail WHERE volume_title LIKE '%诺皋%'")
    nuogao_count = cur.fetchone()['cnt']
    
    # 诺皋记中含神怪关键词的段落
    SHENGUI_KEYWORDS = [
        '鬼','鬼书','鬼官','鬼车鸟','鬼皂荚','鬼矢','鬼魅',
        '精','魅','妖','仙','魔','魂','魄','灵异','作祟',
        '神','神仙','真人','天师','法师','道人','道士','术士','异人',
        '天帝','玉帝','仙官','仙女','仙童','仙药','仙方','仙人',
        '玉女','金童','巫','巫术','巫师',
        '怪','妖怪','妖魅','鬼怪','精怪','妖精','狐精','蛇精','鱼精','树精','花精','石精',
        '狐','九尾','黄鼠狼','蟒','蛟','貔貅',
        '佛','菩萨','罗汉','梵','释','三界','须弥','袈裟','舍利','浮屠',
        '三尸','伏尸','尸解','白日升','飞升','修道','成仙','辟谷',
        '咒','符','法术','幻术','隐形','变形','变幻',
        '冥','酆都','阎罗','判官','阴司','阴间','黄泉','冥府',
        '地狱','鬼使','亡魂','白骨','骷髅',
        '异','变','变化','飞行','隐身','变形','现身','隐去','失所在',
        '龙','麒麟','凤','蟾蜍','月精','玉兔','嫦娥',
        '感应','灵验','显灵','降世','托生','转世','报应',
    ]
    
    total_shengui = 0
    nuogao_shengui = 0
    
    cur.execute("SELECT paragraph_id, text, volume_title FROM narrative_detail")
    all_rows = cur.fetchall()
    keyword_freq = {}
    for r in all_rows:
        text = r['text'] or ''
        found = [kw for kw in SHENGUI_KEYWORDS if kw in text]
        if found:
            total_shengui += 1
            for kw in found:
                keyword_freq[kw] = keyword_freq.get(kw, 0) + 1
            if '诺皋' in (r['volume_title'] or ''):
                nuogao_shengui += 1
    
    conn.close()
    
    # 排序关键词频次
    sorted_keywords = sorted(keyword_freq.items(), key=lambda x: -x[1])[:40]
    
    return {
        "narrative_stats": narr_stats,
        "theme_stats": theme_stats,
        "theme_frequency": theme_freq[:50],
        "total_paragraphs": len(all_rows),
        "total_shengui_paragraphs": total_shengui,
        "nuogao_total": nuogao_count,
        "nuogao_shengui": nuogao_shengui,
        "keyword_frequency": [{"keyword": k, "count": v} for k, v in sorted_keywords],
    }

if __name__ == "__main__":
    stories = extract_story_data()
    stats = extract_shengui_stats()
    
    output = {
        "stories": stories,
        "stats": stats,
    }
    
    out_path = Path(__file__).parent / "story_data.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"Stories extracted: {len(stories)}")
    for s in stories:
        print(f"  {s['pid']}: {s['title']} ({s['keyword_count']} keywords)")
    print(f"Stats: {stats['total_paragraphs']} paragraphs, {stats['total_shengui_paragraphs']} shengui paragraphs")
    print(f"Nuogao: {stats['nuogao_total']} total, {stats['nuogao_shengui']} shengui")
    print(f"Output: {out_path}")
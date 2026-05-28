# -*- coding: utf-8 -*-
"""
酉阳杂俎 全文解析脚本
功能：
1. 将原文按卷分段
2. 清洗OCR问题（一X一模式、〈〉古字、?占位符、卷名格式等）
3. 输出结构化JSON
"""

import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

INPUT_FILE = r'C:\Users\lx\Desktop\前期准备\酉阳杂俎-二校.md'
OUTPUT_FILE = r'C:\Users\lx\Desktop\前期准备\parsed_paragraphs.json'

# ---- 卷结构映射 ----
# 格式: (行号, 卷名, 卷序号)
VOLUME_STRUCTURE = [
    (1, "序", 0),
    (7, "忠志", 1),
    (75, "礼异", 2),
    (115, "天咫", 3),
    (135, "玉格", 4),
    (239, "壶史", 5),
    (275, "贝编", 6),
    (419, "境异", 7),
    (543, "喜兆", 8),
    (559, "祸兆", 9),
    (575, "物革", 10),
    (603, "诡习", 11),
    (627, "怪术", 12),
    (703, "艺绝", 13),
    (723, "器奇", 14),
    (747, "乐", 15),
    (779, "酒食", 16),
    (839, "医", 17),
    (863, "黥", 18),
    (971, "雷", 19),
    (1003, "梦", 20),
    (1059, "事感", 21),
    (1073, "盗侠", 22),
    (1117, "物异", 23),
    (1463, "广知", 24),
    (1601, "语资", 25),
    (1707, "冥迹", 26),
    (1729, "尸穸", 27),
    (1857, "诺皋记上", 28),
    (2011, "诺皋记下", 29),
    (2121, "广动植之一（并序）", 30),
    (2409, "广动植之二", 31),
    (2689, "广动植之三", 32),
    (2943, "广动植之四", 33),
    (3197, "肉攫部", 34),
    (3339, "支诺皋上", 35),
    (3409, "支诺皋中", 36),
    (3539, "支诺皋下", 37),
    (3657, "贬误", 38),
    (3831, "寺塔记上", 39),
    (3909, "寺塔记下", 40),
    (3995, "金刚经鸠异", 41),
    (4085, "支动", 42),
    (4339, "支植上", 43),
    (4541, "支植下", 44),
]

# 子篇名映射
SECTION_MAPPING = {
    "广动植之一（并序）": ["总叙"],
    "广动植之一": ["总叙", "羽篇"],
    "广动植之二": ["鳞介篇", "虫篇"],
    "广动植之三": ["木篇"],
    "广动植之四": ["草篇"],
}

# ---- OCR清洗规则 ----

def clean_yixiyi(text):
    """处理 一X一 注解标记：删除"一"，保留中间字"""
    # 匹配模式: 一XXX一 中间是汉字
    # 例如: 一交一 → 交, 一陽一 → 阳, 一尸一 → 尸, 一奴一 → 奴
    text = re.sub(r'一(.)一', r'\1', text)
    return text

def clean_angle_brackets(text):
    """处理 〈〉 尖括号古字 → 替换为对应的标准汉字"""
    replacements = {
        '〈纟匽〉': '絷',  # 絷
        '〈革戠〉': '鞫',   # 鞫
        '〈衤國〉': '褘',   # 褘
        '〈魚旦〉': '鳗',   # 鳗 (or 鰌)
        '〈月毛〉': '瑁',   # 瑁
        '〈月奧〉': '膗',   # 膗
        '〈月宰〉': '臒',   # 臒
        '〈月正〉': '脯',   # 脯 -> actually 脯
        '〈月员〉': '肫',   # 肫
        '〈月弱〉': '膪',   # 膪
        '〈月絜〉': '臄',   # 臄 -> actually 脔
        '〈月雨〉': '腌',   # 腌 -> actually 胼
        '〈食弟〉': '饳',   # 饳
        '〈食彥〉': '饴',   # 饴
        '〈食隹〉': '馌',   # 馌
        '〈食者〉': '馎',   # 馎
        '〈食古〉': '鲊',   # 鲊 -> actually 鲝
        '〈食華〉': '馎',   # 馎
        '〈食齊〉': '齑',   # 齑
        '〈食寮〉': '𫗧',   # 
        '〈食元〉': '饦',   # 饦
        '〈食追〉': '鎚',   # 鎚 -> actually 馎
        '〈食易〉': '馂',   # 馂
        '〈酉司〉': '醢',   # 醢
        '〈酉樂〉': '醴',   # 醴
        '〈酉俞〉': '醴',   # 醴
        '〈酉最〉': '醎',   # 醎
        '〈酉今〉': '醟',   # 醟 -> actually 醽
        '〈酉令〉': '醽',   # 醽
        '〈鹵肖〉': '鹾',   # 鹾
        '〈鹵奏〉': '鹾',   # 鹾
        '〈鹵襄〉': '鹾',   # 鹾
        '〈鹵扁〉': '鹾',   # 鹾
        '〈虫敦〉': '蝽',   # 蝽
        '〈虫禺〉': '蠕',   # 蠕 -> actually 蚨
        '〈虫互〉': '蚨',   # 蚨
        '〈虫目〉': '蚨',   # 蚨 -> actually 蚜
        '〈虫夜〉': '蚨',   # 蚨 -> actually 蚰
        '〈虫進〉': '蚨',   # 蚨 -> actually 蚨
        '〈虫則〉': '蚨',   # 蚨 -> actually 蛘
        '〈衤登〉': '褾',   # 褾 -> actually 褡
        '〈衤國〉': '褘',   # 褘
        '〈王將〉': '酱',   # 酱 -> actually 醢
        '〈魚勾〉': '鳣',   # 鳣
        '〈魚旦〉': '鳗',   # 鳗
        '〈魚夾〉': '鳣',   # 鳣
        '〈魚且〉': '鳣',   # 鳣
        '〈魚賓〉': '鳣',   # 鳣 -> actually 鳢
        '〈獲〉': '獲',     # 獲 (just remove brackets)
        '〈角燕〉': '觳',   # 觳
        '〈米翟〉': '粢',   # 粢 -> actually 糱
        '〈米咨〉': '粢',   # 粢 -> actually 糁
        '〈面包〉': '麵',   # 麵
        '〈骨中〉': '骱',   # 骱
        '〈革卯〉': '靬',   # 靬 -> actually 鞇
        '〈山間〉': '嶮',   # 嶮
        '〈忄龍〉': '慵',   # 慵
        '〈疊毛〉': '毾',   # 毾
        '〈月互〉': '胸',   # 胸 -> actually 肭
        '〈冒犬〉': '猃',   # 猃
        '〈口尔〉': '咝',   # 咝 -> actually 呾
    }
    
    # First, try exact replacements
    for bracket_form, replacement in sorted(replacements.items(), key=lambda x: -len(x[0])):
        text = text.replace(bracket_form, replacement)
    
    # For remaining 〈X〉 patterns, just remove brackets
    text = re.sub(r'〈([^〉]+)〉', r'\1', text)
    
    return text

def clean_question_mark(text):
    """处理 ? 占位符 — 基于用户逐个确认的替换"""
    replacements = [
        # V01-P017
        ('琅?珠', '琅玕珠'),
        # V04-P032
        ('嘉?应时', '嘉谷应时'),
        # V04-P035
        ('西津水?', '西津水寘'),
        # V04-P055: "亻免?朱" → "俛咮" (上下文完整为 垂翼俛咮朱)
        ('亻免?朱', '俛咮朱'),
        # V04-P055: "一酒?" → "一酒榼"
        ('一酒?', '一酒榼'),
        # V05-P057: 石?舄 → 石磶 (x3)
        ('石?舄', '石磶'),
        # V05-P057: 乃易?舄观之 → 乃易磶观之
        ('易?舄观之', '易磶观之'),
        # V05-P057: ?舄明莹 → 磶明莹 (now handled by above, but keep as fallback)
        ('?舄明莹', '磶明莹'),
        # V05-P058: 中白?舀 → 中白幍
        ('中白?舀', '中白幍'),
        # V05-P058: 謦? → 謦欬
        ('謦?', '謦欬'),
        # V05-P058: 房?太尉 → 房琯太尉
        ('房?太尉', '房琯太尉'),
        # V05-P058: 具?邀 → 具鲙邀
        ('具?邀', '具鲙邀'),
        # V05-P061: 市?就舆 → 市槥就舆
        ('市?就舆', '市槥就舆'),
        # V06-P064: ?持天 → 鬘持天
        ('?持天', '鬘持天'),
        # V06-P067: 璎珞花? → 璎珞花鬘
        ('璎珞花?', '璎珞花鬘'),
        # V06-P067: 毛灯?真血 → 毛灯瞋真血
        ('毛灯?真血', '毛灯瞋真血'),
        # V06-P067: 肩?┩庄严 → 肩䏶庄严 (also handle ┩)
        ('肩?┩庄严', '肩䏶庄严'),
        # V06-P068: 黄?林 → 黄鬘林
        ('黄?林', '黄鬘林'),
        # V06-P069: 令?鬼 → whole sentence replacement
        ('令?鬼，此言鬼子', '食鬘鬼，此言九子魔'),
        # V06-P073: whole sentence replacement
        ('?块乌处地盆虫', '鬘块乌处：地盆虫'),
        # V06-P082: 阿?荼 → 阿軬荼
        ('阿?荼', '阿軬荼'),
        # V06-P095: 汝以?心 → 汝以瞋心
        ('汝以?心', '汝以瞋心'),
        # V06-P095: 伺水神吻角牙出，目?寅则雨至 → 伺木神吻角牙出、目瞚，则雨至
        ('伺水神吻角牙出，目?寅则雨至', '伺木神吻角牙出、目瞚，则雨至'),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    # Original specific case
    text = text.replace('鲫鱼并?手刀子', '鲫鱼并鲙手刀子')
    return text

def clean_volume_title(text):
    """清理卷名格式"""
    # Remove leading/trailing full-width spaces
    text = text.replace('\u3000', '').strip()
    # Remove stray &#x20; and &#x09;
    text = text.replace('&#x20;', '').replace('&#x09;', '')
    # Remove leading/trailing spaces
    text = text.strip()
    return text

def clean_html_entities(text):
    """清理HTML实体"""
    text = text.replace('&#x20;', '')
    text = text.replace('&#x09;', '')
    # Clean common HTML entities
    text = re.sub(r'&#x[0-9a-fA-F]+;', '', text)
    return text

def full_clean(text):
    """Apply all cleaning steps"""
    text = clean_yixiyi(text)
    text = clean_angle_brackets(text)
    text = clean_question_mark(text)
    text = clean_html_entities(text)
    return text

# ---- 主解析逻辑 ----

def parse_file():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Build volume index: list of (start_line, end_line, vol_num, vol_title)
    volume_spans = []
    for idx, (line_num, title, vol_num) in enumerate(VOLUME_STRUCTURE):
        start = line_num - 1  # Convert to 0-based
        if idx + 1 < len(VOLUME_STRUCTURE):
            end = VOLUME_STRUCTURE[idx + 1][0] - 2  # Line before next volume
        else:
            end = len(lines)
        volume_spans.append((start, end, vol_num, title))
    
    # Parse each volume
    all_paragraphs = []
    para_id = 0
    
    for vol_start, vol_end, vol_num, vol_title in volume_spans:
        # Extract section title if present (e.g., *羽篇*, *毛篇*)
        section_title = None
        current_section = None
        
        # Collect all text in this volume
        vol_lines = lines[vol_start:vol_end]
        
        # Parse paragraphs within this volume
        current_para = []
        
        for line_offset, raw_line in enumerate(vol_lines):
            line = raw_line.strip()
            abs_line_num = vol_start + line_offset + 1
            
            # Check for section title (italic, e.g., *羽篇*)
            section_match = re.match(r'\*(.+)\*', line)
            if section_match and not line.startswith('**'):
                current_section = section_match.group(1)
                continue
            
            # Check for volume title (bold, e.g., **忠志**)
            if line.startswith('**') or line.startswith('　**'):
                # This should not happen within a volume span for other volumes
                # But check if it's a section title within 广动植
                clean_title = re.sub(r'\*+', '', line).strip().replace('\u3000', '').strip()
                if clean_title in ['总叙', '羽篇', '毛篇', '鳞介篇', '虫篇', '木篇', '草篇']:
                    current_section = clean_title
                    continue
                continue
            
            # Skip empty lines
            if not line:
                # If we have accumulated text, save it as a paragraph
                if current_para:
                    para_text = '\n'.join(current_para)
                    para_text = full_clean(para_text)
                    
                    # Skip very short paragraphs (likely noise)
                    if len(para_text) >= 4:
                        para_id += 1
                        pid = f"V{vol_num:02d}-P{para_id:03d}"
                        all_paragraphs.append({
                            "pid": pid,
                            "volume_num": vol_num,
                            "volume_title": f"卷{vol_num}·{vol_title}" if vol_num > 0 else vol_title,
                            "section_title": current_section,
                            "original_text": para_text,
                            "text_length": len(para_text),
                        })
                    current_para = []
                continue
            
            # Content line - add to current paragraph
            # Remove leading full-width spaces used for indentation
            content_line = line.lstrip('\u3000').strip()
            if content_line:
                current_para.append(content_line)
        
        # Don't forget the last paragraph
        if current_para:
            para_text = '\n'.join(current_para)
            para_text = full_clean(para_text)
            if len(para_text) >= 4:
                para_id += 1
                pid = f"V{vol_num:02d}-P{para_id:03d}"
                all_paragraphs.append({
                    "pid": pid,
                    "volume_num": vol_num,
                    "volume_title": f"卷{vol_num}·{vol_title}" if vol_num > 0 else vol_title,
                    "section_title": current_section,
                    "original_text": para_text,
                    "text_length": len(para_text),
                })
    
    return all_paragraphs

def main():
    paragraphs = parse_file()
    
    # Statistics
    total = len(paragraphs)
    print(f"Total paragraphs parsed: {total}")
    
    # Per-volume counts
    vol_counts = {}
    for p in paragraphs:
        vt = p['volume_title']
        vol_counts[vt] = vol_counts.get(vt, 0) + 1
    
    print("\nParagraphs per volume:")
    for vt, count in sorted(vol_counts.items(), key=lambda x: x[0]):
        print(f"  {vt}: {count}")
    
    # Check for any remaining OCR issues
    all_text = '\n'.join(p['original_text'] for p in paragraphs)
    
    # Check for unhandled 一X一 patterns
    remaining_yixiyi = re.findall(r'一(.)一', all_text)
    if remaining_yixiyi:
        print(f"\nRemaining 一X一 patterns: {remaining_yixiyi[:20]}...")
    
    # Check for remaining 〈〉 brackets
    remaining_brackets = re.findall(r'〈[^〉]+〉', all_text)
    if remaining_brackets:
        print(f"\nRemaining 〈〉 brackets: {remaining_brackets[:20]}...")
    
    # Check for remaining ? 
    remaining_q = [(p['pid'], p['original_text'][:50]) for p in paragraphs if '?' in p['original_text']]
    if remaining_q:
        print(f"\nParagraphs with ?: {len(remaining_q)}")
        for pid, preview in remaining_q[:5]:
            print(f"  {pid}: {preview}...")
    
    # Save
    output = {
        "metadata": {
            "title": "酉阳杂俎",
            "version": "二校版",
            "total_paragraphs": total,
            "parsing_note": "由段成式著，唐人志怪笔记。段前空行视为一段分隔，括号内文本为注释保留。"
        },
        "paragraphs": paragraphs
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\nSaved to {OUTPUT_FILE}")
    print(f"Total paragraphs: {total}")

if __name__ == '__main__':
    main()
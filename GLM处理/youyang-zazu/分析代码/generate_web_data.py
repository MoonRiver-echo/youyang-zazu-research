#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成段落分类总表和神鬼妖魔怪数据，供网页嵌入使用。

输出:
  - 分类总表.md: 按描写对象分类的段落总表
  - web_extra_data.json: 网页所需的额外数据（分类总表 + 神鬼数据）
"""
import csv, json, collections
from pathlib import Path

DATA_DIR = Path(r"C:\Users\lx\Desktop\前期准备\GLM处理")
OUTPUT_MD = DATA_DIR / "07-段落描写对象分类总表.md"
OUTPUT_JSON = DATA_DIR / "web_extra_data.json"

# ═══════════════════════════════════════════════════════════
# 1. 读取数据
# ═══════════════════════════════════════════════════════════
print("正在读取数据...")
narrative_detail = []
with open(DATA_DIR / "叙事分类明细.csv", encoding='utf-8-sig', newline='') as f:
    for r in csv.DictReader(f):
        narrative_detail.append(r)

theme_detail = []
with open(DATA_DIR / "主题分类明细.csv", encoding='utf-8-sig', newline='') as f:
    for r in csv.DictReader(f):
        theme_detail.append(r)

theme_frequency = []
with open(DATA_DIR / "主题频次统计.csv", encoding='utf-8-sig', newline='') as f:
    for r in csv.DictReader(f):
        theme_frequency.append(r)

narrative_stats = []
with open(DATA_DIR / "叙事分类统计.csv", encoding='utf-8-sig', newline='') as f:
    for r in csv.DictReader(f):
        narrative_stats.append(r)

theme_stats = []
with open(DATA_DIR / "主题分类统计.csv", encoding='utf-8-sig', newline='') as f:
    for r in csv.DictReader(f):
        theme_stats.append(r)

print(f"  叙事明细: {len(narrative_detail)} 条")
print(f"  主题明细: {len(theme_detail)} 条")

# ═══════════════════════════════════════════════════════════
# 2. 构建段落索引
# ═══════════════════════════════════════════════════════════
para_map = {}  # paragraph_id → {narrative_category, volume_title, content}
for r in narrative_detail:
    pid = r['paragraph_id']
    text = r.get('text', '')
    para_map[pid] = {
        'narrative_category': r['narrative_category'],
        'volume_title': r['volume_title'],
        'content': text,
    }

# 构建主题索引: paragraph_id → list of (broad, level1, level2, specific)
para_themes = collections.defaultdict(list)
for r in theme_detail:
    pid = r['paragraph_id']
    para_themes[pid].append((
        r['broad_category'],
        r['level1_subject'],
        r['level2_subject'],
        r['specific_subject'],
    ))

# ═══════════════════════════════════════════════════════════
# 3. 构建分类树
# ═══════════════════════════════════════════════════════════
# broad → level1 → level2 → specific → [paragraph_ids]
theme_tree = collections.defaultdict(
    lambda: collections.defaultdict(
        lambda: collections.defaultdict(
            lambda: collections.defaultdict(list)
        )
    )
)

for r in theme_detail:
    broad = r['broad_category']
    l1 = r['level1_subject']
    l2 = r['level2_subject']
    spec = r['specific_subject']
    pid = r['paragraph_id']
    theme_tree[broad][l1][l2][spec].append(pid)

# 排序用的主题大类列表
THEME_ORDER = [
    '人物政事','动物','神怪妖魅','植物','器物技艺','建筑寺塔',
    '异域物产','饮食医药','异人方术','梦兆占验','丧葬冥界',
    '佛道信仰','天文地理','礼俗制度',
]

# ═══════════════════════════════════════════════════════════
# 4. 生成 Markdown 文档
# ═══════════════════════════════════════════════════════════
print("正在生成分类总表 Markdown...")

def summarize(text, max_len=50):
    """生成文段含义概括：取前 max_len 字符，截断加省略号"""
    s = text.replace('\n', ' ').strip()
    if len(s) <= max_len:
        return s
    return s[:max_len] + '…'

lines = []
lines.append("# 《酉阳杂俎》段落描写对象分类总表\n")
lines.append("> 基于794段全文，按描写对象一级类目→二级类目组织，" +
             "列出每段所属主题、原文及含义概括。\n\n---\n")

total_paras = len(para_map)
total_theme_rows = len(theme_detail)
lines.append(f"**全文段落总数**：{total_paras}段\n\n")
lines.append(f"**主题分类记录**：{total_theme_rows}条（一段可归属多类）\n\n")

for broad in THEME_ORDER:
    if broad not in theme_tree:
        continue
    l1_map = theme_tree[broad]
    # 统计该大类涉及的段落数
    broad_pids = set()
    for l1 in l1_map.values():
        for l2 in l1.values():
            for spec_pids in l2.values():
                broad_pids.update(spec_pids)
    lines.append(f"\n## {broad}（{len(broad_pids)}段）\n")

    for l1_name, l2_map in sorted(l1_map.items()):
        l1_pids = set()
        for l2 in l2_map.values():
            for spec_pids in l2.values():
                l1_pids.update(spec_pids)
        lines.append(f"\n### {l1_name}（{len(l1_pids)}段）\n")

        for l2_name, spec_map in sorted(l2_map.items()):
            l2_pids = set()
            for spec_pids in spec_map.values():
                l2_pids.update(spec_pids)
            lines.append(f"\n#### {l2_name}（{len(l2_pids)}段）\n")
            lines.append("| 段落ID | 卷·篇 | 叙事分类 | 具体对象 | 原文 | 含义概括 |")
            lines.append("|--------|--------|----------|----------|------|----------|")

            # 收集所有段落，按 ID 排序
            seen_pids = set()
            all_entries = []
            for spec_name, pids in sorted(spec_map.items()):
                for pid in pids:
                    if pid in seen_pids:
                        continue
                    seen_pids.add(pid)
                    p = para_map.get(pid, {})
                    text = p.get('content', '')
                    all_entries.append((pid, p, spec_name, text))

            for pid, p, spec_name, text in sorted(all_entries, key=lambda x: x[0]):
                nar = p.get('narrative_category', '')
                vt = p.get('volume_title', '')
                summary = summarize(text, 40)
                # 原文截断到100字避免表格过宽
                short_text = text.replace('\n', ' ')[:100] + ('…' if len(text) > 100 else '')
                lines.append(f"| {pid} | {vt} | {nar} | {spec_name} | {short_text} | {summary} |")

md_content = ''.join(lines)
with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
    f.write(md_content)
print(f"已生成: {OUTPUT_MD}")

# ═══════════════════════════════════════════════════════════
# 5. 生成神鬼妖魔怪数据
# ═══════════════════════════════════════════════════════════
print("正在生成神鬼妖魔怪数据...")

SHENGUI_KEYWORDS = [
    # 原有分类关键词
    '鬼','鬼书','鬼官','鬼车鸟','鬼皂荚','鬼矢','鬼魅',
    '精','魅','妖','仙','魔','魂','魄','灵异','作祟',
    # 神灵类
    '神','神仙','真人','天师','法师','道人','道士','术士','异人',
    '天帝','玉帝','仙官','仙女','仙童','仙药','仙方','仙人',
    '玉女','金童','巫','巫术','巫师',
    # 妖怪类
    '怪','妖怪','妖魅','鬼怪','精怪','妖精','狐精','蛇精','鱼精','树精','花精','石精',
    '狐','九尾','黄鼠狼','蟒','蛟','貔貅',
    # 佛道超自然
    '佛','菩萨','罗汉','梵','释','三界','须弥','袈裟','舍利','浮屠',
    '三尸','伏尸','尸解','白日升','飞升','修道','成仙','辟谷',
    '咒','符','法术','幻术','隐形','变形','变幻',
    # 冥界
    '冥','酆都','阎罗','判官','阴司','阴间','黄泉','冥府',
    '地狱','鬼使','亡魂','白骨','骷髅',
    # 异变现象
    '异','变','变化','飞行','隐身','变形','现身','隐去','失所在',
    '龙','麒麟','凤','蟾蜍','月精','玉兔','嫦娥',
    '感应','灵验','显灵','降世','托生','转世','报应',
]

# 扩展关键词去重（短词包含检测时，短词会被长词的子串误匹配）
# 按长度降序排列以优先匹配长词
shengui_sorted = sorted(set(SHENGUI_KEYWORDS), key=len, reverse=True)

# 搜索含超自然关键词的段落
shengui_results = []
keyword_counter = collections.Counter()
for r in narrative_detail:
    text = r.get('text', '')
    pid = r['paragraph_id']
    found = []
    # 用短词匹配（简单 in），但优先长词
    for kw in shengui_sorted:
        if kw in text:
            found.append(kw)
            keyword_counter[kw] += 1
    if found:
        shengui_results.append({
            'pid': pid,
            'volume_title': r['volume_title'],
            'narrative_category': r['narrative_category'],
            'keywords': found,
            'keyword_count': len(found),
            'text': text,
        })

# 按关键词数量降序排列
shengui_results.sort(key=lambda x: x['keyword_count'], reverse=True)

# 神怪妖魅类段落
theme_sg = [r for r in theme_detail if r['broad_category'] == '神怪妖魅']
sg_pids = set(r['paragraph_id'] for r in theme_sg)

# 未被神怪妖魅类覆盖的段落
uncovered = [r for r in shengui_results if r['pid'] not in sg_pids]

# 按叙事分类统计
nar_dist = collections.Counter(r['narrative_category'] for r in shengui_results)

# ═══════════════════════════════════════════════════════════
# 6. 生成 JSON 数据（供网页嵌入）
# ═══════════════════════════════════════════════════════════
print("正在生成JSON数据...")

# 分类总表数据: broad → level1 → level2 → specific → [{pid, vt, nar, text, summary}, ...]
classification_data = {}
for broad in THEME_ORDER:
    if broad not in theme_tree:
        continue
    l1_map = theme_tree[broad]
    broad_data = {}
    for l1_name, l2_map in sorted(l1_map.items()):
        l1_data = {}
        for l2_name, spec_map in sorted(l2_map.items()):
            l2_data = {}
            for spec_name, pids in sorted(spec_map.items()):
                entries = []
                seen = set()
                for pid in sorted(pids):
                    if pid in seen:
                        continue
                    seen.add(pid)
                    p = para_map.get(pid, {})
                    text = p.get('content', '')
                    entries.append({
                        'pid': pid,
                        'vt': p.get('volume_title', ''),
                        'nar': p.get('narrative_category', ''),
                        'text': text,
                        'summary': summarize(text, 50),
                    })
                l2_data[spec_name] = entries
            l1_data[l2_name] = l2_data
        broad_data[l1_name] = l1_data
    classification_data[broad] = broad_data

# 神鬼妖魔怪数据
shengui_data = {
    'total_shengui_paragraphs': len(shengui_results),
    'total_sgm_classified': len(sg_pids),
    'total_uncovered': len(uncovered),
    'keyword_frequency': [
        {'keyword': kw, 'count': cnt}
        for kw, cnt in keyword_counter.most_common(60)
    ],
    'narrative_distribution': [
        {'category': cat, 'count': cnt}
        for cat, cnt in nar_dist.most_common()
    ],
    # 全部341段含超自然关键词的段落（含完整原文）
    'all_paragraphs': [
        {
            'pid': r['pid'],
            'vt': r['volume_title'],
            'nar': r['narrative_category'],
            'keywords': r['keywords'],
            'keyword_count': r['keyword_count'],
            'text': r['text'],
            'summary': summarize(r['text'], 60),
        }
        for r in shengui_results
    ],
    # 标记哪些段落已被「神怪妖魅」大类覆盖
    'classified_pids': sorted(list(sg_pids)),
    'sgm_subcategories': [
        {'subcategory': r['level1_subject'], 'specific': r['specific_subject'], 'count': cnt}
        for (r, cnt) in [
            (r, sum(1 for t in theme_sg if t['level1_subject'] == r['level1_subject'] and t['specific_subject'] == r['specific_subject']))
            for r in theme_sg
        ]
    ],
}

# 神怪妖魅子类统计
sg_l1_counter = collections.Counter()
sg_l2_counter = collections.Counter()
for r in theme_sg:
    sg_l1_counter[r['level1_subject']] += 1
    sg_l2_counter[r['specific_subject']] += 1

shengui_data['sgm_subcategory_stats'] = [
    {'subcategory': k, 'count': v}
    for k, v in sg_l1_counter.most_common()
]
shengui_data['sgm_specific_stats'] = [
    {'specific': k, 'count': v}
    for k, v in sg_l2_counter.most_common()
]

# 保存 JSON
web_data = {
    'classification': classification_data,
    'shengui': shengui_data,
}

with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(web_data, f, ensure_ascii=False, separators=(',', ':'))

print(f"已生成: {OUTPUT_JSON}")
print(f"  分类总表: {len(classification_data)} 大类")
total_entries = sum(
    len(entry)
    for broad_data in classification_data.values()
    for l1_data in broad_data.values()
    for l2_data in l1_data.values()
    for spec_entries in l2_data.values()
    for entry in [spec_entries]
)
print(f"  神鬼数据: {shengui_data['total_shengui_paragraphs']} 段含超自然关键词")
print("\n完成！")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析未分类的超自然段落，找出模式，辅助扩展关键词
"""
import csv
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

BASE = r"C:\Users\lx\Desktop\前期准备\清洗数据"

# 读取超自然明细
sg_detail = []
with open(f'{BASE}\\超自然力量叙事主题明细.csv', 'r', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        sg_detail.append(row)

# 读取叙事明细获取完整文本
narr_detail = {}
with open(f'{BASE}\\叙事分类明细.csv', 'r', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        narr_detail[row['paragraph_id']] = row

# 分类统计
classified = 0
unclassified = []
for row in sg_detail:
    themes = row.get('narrative_themes','').strip()
    if not themes:
        pid = row['paragraph_id']
        full = narr_detail.get(pid, {})
        text = full.get('text','')
        unclassified.append({
            'pid': pid,
            'vol': row['volume_title'],
            'mt': row.get('monster_type',''),
            'text': text
        })
    else:
        classified += 1

print(f"超自然段落总数: {len(sg_detail)}")
print(f"已分类: {classified}")
print(f"未分类: {len(unclassified)}")
print()

# 分析未分类段落的特征关键词
# 按 monster_type 分组统计
mt_counter = Counter()
mt_examples = defaultdict(list)
for u in unclassified:
    mt_counter[u['mt']] += 1
    if len(mt_examples[u['mt']]) < 3:
        mt_examples[u['mt']].append(u['text'][:60])

print("=== 未分类段落的怪物类型分布 ===")
for mt, count in mt_counter.most_common():
    print(f"  {mt}: {count}段")
    for ex in mt_examples[mt]:
        print(f"    → {ex}…")

print()

# 分析高频词汇（单字+双字）
from collections import Counter as C2
char_counter = Counter()
bigram_counter = Counter()
for u in unclassified:
    text = u['text']
    # 单字频率（仅统计关键词相关字符）
    keyword_chars = '神仙鬼妖魔魅怪精佛僧道变化魂魄冥阴梦卜占瑞异奇宝珍灵幻术法咒符幻'
    for ch in text:
        if ch in keyword_chars:
            char_counter[ch] += 1
    # 双字
    for i in range(len(text)-1):
        bg = text[i:i+2]
        if len(bg.strip()) == 2:
            bigram_counter[bg] += 1

print("=== 未分类段落关键字符频率（Top 30）===")
for ch, cnt in char_counter.most_common(30):
    print(f"  '{ch}': {cnt}")

print()
print("=== 未分类段落双字高频词（Top 40）===")
for bg, cnt in bigram_counter.most_common(40):
    print(f"  '{bg}': {cnt}")

print()

# 输出所有未分类段落（PID + 卷名 + 前80字）
print("=== 全部未分类段落 ===")
for i, u in enumerate(unclassified):
    print(f"{i+1:3d}. [{u['pid']}] {u['vol']} | {u['mt']} | {u['text'][:80]}")
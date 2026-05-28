#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从《酉阳杂俎》原文提取所有与神鬼妖魔怪相关的描写对象"""
import csv, sys, re, collections
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
DATA_DIR = Path(r"C:\Users\lx\Desktop\前期准备\GLM处理")

# 读取叙事分类明细
narr = []
with open(DATA_DIR / "叙事分类明细.csv", encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        narr.append(r)

# 读取主题分类明细
theme = []
with open(DATA_DIR / "主题分类明细.csv", encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        theme.append(r)

# 神怪妖魅类段落
shenGuai = [r for r in theme if r['broad_category'] == '神怪妖魅']
para_ids = set(r['paragraph_id'] for r in shenGuai)
print("=" * 60)
print("【1】已分类为「神怪妖魅」的段落统计")
print("=" * 60)
print("涉及段落数:", len(para_ids))
print()

# 子类分布
l1_counter = collections.Counter()
l2_counter = collections.Counter()
for r in shenGuai:
    l1_counter[r['level1_subject']] += 1
    l2_counter[r['level2_subject']] += 1

print("--- 子类分布 ---")
for k, v in l1_counter.most_common():
    print("  {}: {} 次匹配".format(k, v))
print()
print("--- 具体对象频次 ---")
for k, v in l2_counter.most_common():
    print("  {}: {} 次".format(k, v))

# 扩展关键词表——从原文中搜索所有可能的超自然描写对象
shen_keys = [
    # 原有分类关键词
    '鬼','鬼书','鬼官','鬼车鸟','鬼皂荚','鬼矢','鬼魅',
    '精','魅','妖','仙','魔','魂','魄','灵异',
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

print()
print("=" * 60)
print("【2】全文搜索：含超自然关键词的段落")
print("=" * 60)

key_counter = collections.Counter()
results = []
for r in narr:
    t = r.get('text', '')
    pid = r['paragraph_id']
    found = []
    for k in shen_keys:
        if k in t:
            found.append(k)
    if found:
        results.append({'pid': pid, 'vt': r['volume_title'], 'nar': r['narrative_category'], 'keys': found, 'text': t})
        for k in found:
            key_counter[k] += 1

print("含超自然关键词的段落数:", len(results))
print()

print("--- 关键词频次（Top 60）---")
for k, v in key_counter.most_common(60):
    print("  {}: {} 次".format(k, v))

print()
print("--- 关键词最密集的20个段落 ---")
results.sort(key=lambda x: len(x['keys']), reverse=True)
for r in results[:20]:
    keys_str = ', '.join(r['keys'][:12])
    extra = '...' if len(r['keys']) > 12 else ''
    print("  {} ({}) [{}]: {}{} ({}个)".format(
        r['pid'], r['vt'], r['nar'], keys_str, extra, len(r['keys'])))

# 按叙事分类统计
print()
print("=" * 60)
print("【3】按叙事分类分布")
print("=" * 60)
nar_counter = collections.Counter()
for r in results:
    nar_counter[r['nar']] += 1
for k, v in nar_counter.most_common():
    print("  {}: {} 段".format(k, v))

# 按卷分布
print()
print("--- 按卷分布 ---")
vol_counter = collections.Counter()
for r in results:
    vol_counter[r['vt']] += 1
for k, v in vol_counter.most_common(15):
    print("  {}: {} 段".format(k, v))

print()
print("=" * 60)
print("【4】不在「神怪妖魅」类但含超自然关键词的段落")
print("=" * 60)
not_in_theme = [r for r in results if r['pid'] not in para_ids]
print("段落数:", len(not_in_theme))
print()
for r in not_in_theme[:20]:
    keys_str = ', '.join(r['keys'][:8])
    print("  {} ({}) [{}]: {}".format(r['pid'], r['vt'], r['nar'], keys_str))
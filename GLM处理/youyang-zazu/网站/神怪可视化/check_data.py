#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
with open(r'C:\Users\lx\Desktop\前期准备\GLM处理\youyang-zazu\网站\神怪可视化\story_data.json', encoding='utf-8') as f:
    data = json.load(f)
stories = data['stories']
stats = data['stats']
for s in stories:
    for key in ['title','brief','monster_type','original_text','shengui_keywords','themes','volume_title','narrative_category','pid']:
        if key not in s:
            print(f"MISSING {key} in {s.get('pid','???')}")
print("Stories check done, count:", len(stories))
print("Narrative stats:", len(stats.get('narrative_stats',[])))
print("Keyword freq:", len(stats.get('keyword_frequency',[])))
print("Total paragraphs:", stats.get('total_paragraphs'))
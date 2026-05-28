#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\lx\Desktop\前期准备\GLM处理\youyang-zazu\网站\神怪可视化\story_data.json', encoding='utf-8') as f:
    data = json.load(f)
for s in data['stories']:
    print(f"=== {s['pid']} ===")
    print(s['original_text'])
    print()
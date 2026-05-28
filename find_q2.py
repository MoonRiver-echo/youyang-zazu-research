# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\lx\Desktop\前期准备\parsed_paragraphs.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
for p in data['paragraphs']:
    if '?' in p['original_text']:
        t = p['original_text']
        idx = 0
        while True:
            pos = t.find('?', idx)
            if pos == -1:
                break
            start = max(0, pos - 15)
            end = min(len(t), pos + 16)
            print(f"{p['pid']}: ...{t[start:end]}...")
            idx = pos + 1
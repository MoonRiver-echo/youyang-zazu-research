# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\lx\Desktop\前期准备\parsed_paragraphs.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for p in data['paragraphs']:
    t = p['original_text']
    if '?' in t:
        idx = 0
        count = 0
        while True:
            pos = t.find('?', idx)
            if pos == -1:
                break
            start = max(0, pos - 12)
            end = min(len(t), pos + 13)
            context = t[start:end]
            count += 1
            pid = p['pid']
            print(f'{pid}-Q{count}: ...{context}...')
            idx = pos + 1
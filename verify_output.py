# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\lx\Desktop\前期准备\classified_youyang.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Show first few entries of stories
for s in data['stories'][:5]:
    pid = s['pid']
    vt = s['volume_title']
    mt = s['monster_type']
    title = s.get('title', '')[:20]
    print(f'{pid} | {vt} | {mt} | {title}')

print('...')
meta = data['metadata']
print(f'Total stories: {meta["total_shengui_paragraphs"]}')
print(f'Total paragraphs: {meta["total_paragraphs"]}')
print(f'Stories in stories array: {len(data["stories"])}')
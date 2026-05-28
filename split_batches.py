# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\lx\Desktop\前期准备\parsed_paragraphs.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
paras = data['paragraphs']

# Split into 6 batches
batch_size = len(paras) // 6 + 1
for i in range(6):
    start = i * batch_size
    end = min((i + 1) * batch_size, len(paras))
    batch = paras[start:end]
    batch_file = rf'C:\Users\lx\Desktop\前期准备\batch_{i+1}.json'
    with open(batch_file, 'w', encoding='utf-8') as f:
        json.dump({'paragraphs': batch}, f, ensure_ascii=False)
    vn_first = batch[0]['volume_num']
    vn_last = batch[-1]['volume_num']
    print(f'Batch {i+1}: {len(batch)} paragraphs (V{vn_first:02d}-V{vn_last:02d})')
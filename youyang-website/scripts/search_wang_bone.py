import json

with open(r'C:\Users\lx\Desktop\前期准备\酉阳杂俎-ctext.json', 'r', encoding='utf-8') as f:
    text = json.load(f)

# Split by paragraphs more carefully
paras = []
current = ''
for line in text.split('\n'):
    line = line.strip()
    if not line:
        if current.strip():
            paras.append(current.strip())
            current = ''
    else:
        current += line
if current.strip():
    paras.append(current.strip())

# Search for stories with 王 and bone/ skeleton / corpse related
keywords = ['王', '骨', '尸', '骸', '骷髅', '肉', '血']
results = []

for i, p in enumerate(paras):
    if '王' in p and any(k in p for k in ['骨', '尸', '骸', '骷髅', '肉朽骨']):
        results.append(f'=== Para {i} (len={len(p)}) ===')
        results.append(p)
        results.append('')

with open(r'C:\Users\lx\Desktop\前期准备\youyang-website\scripts\wang_bone_search.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))

print(f"Found {len(results)//3} paragraphs")
print("Results saved to wang_bone_search.txt")

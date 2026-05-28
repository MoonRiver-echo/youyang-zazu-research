import json

with open(r'C:\Users\lx\Desktop\前期准备\酉阳杂俎-ctext.json', 'r', encoding='utf-8') as f:
    text = json.load(f)

results = []

# Search for 王生
idx = text.find('王生')
results.append(f'王生 found at: {idx}')
if idx != -1:
    results.append(text[max(0,idx-200):idx+400])
    results.append('---')

# Search for 白骨
idx = text.find('白骨')
results.append(f'白骨 found at: {idx}')
if idx != -1:
    results.append(text[max(0,idx-200):idx+400])
    results.append('---')

# Search for 骷髅
idx = text.find('骷髅')
results.append(f'骷髅 found at: {idx}')
if idx != -1:
    results.append(text[max(0,idx-200):idx+400])
    results.append('---')

# Search for 骨已
idx = text.find('骨已')
results.append(f'骨已 found at: {idx}')
if idx != -1:
    results.append(text[max(0,idx-200):idx+400])
    results.append('---')

# Search for any paragraph with both 王 and 骨
paras = text.split('\n\n')
for i, p in enumerate(paras):
    if '王' in p and ('骨' in p or '尸' in p or '死人' in p):
        results.append(f'=== Para with 王+骨/尸 {i} ===')
        results.append(p[:600])
        results.append('')

with open(r'C:\Users\lx\Desktop\前期准备\youyang-website\scripts\wang_search.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))

print("Done")

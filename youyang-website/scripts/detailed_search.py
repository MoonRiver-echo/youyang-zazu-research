import json

with open(r'C:\Users\lx\Desktop\前期准备\酉阳杂俎-ctext.json', 'r', encoding='utf-8') as f:
    text = json.load(f)

# More targeted searches
searches = {
    '王生': '王生',
    '白骨': '白骨',
    '骷髅': '骷髅',
    '书生': '书生',
    '士人': '士人',
    '学子': '学子',
    '骨人': '骨人',
    '化为骨': '化为骨',
    '骨立': '骨立',
    '骨架': '骨架'
}

results = []
for name, kw in searches.items():
    idx = text.find(kw)
    results.append(f'=== {name} (found at {idx}) ===')
    if idx != -1:
        # Show 2 occurrences
        for i in range(2):
            if idx == -1:
                break
            snippet = text[max(0,idx-150):idx+250]
            results.append(snippet)
            results.append('---')
            idx = text.find(kw, idx+1)
    else:
        results.append('NOT FOUND')
    results.append('')

with open(r'C:\Users\lx\Desktop\前期准备\youyang-website\scripts\detailed_search.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))

print("Done")

import json

with open(r'C:\Users\lx\Desktop\前期准备\酉阳杂俎-ctext.json', 'r', encoding='utf-8') as f:
    text = json.load(f)

# Find the full paragraph containing the bone story
idx = text.find('白骨而已，无泊一蝇肉')
if idx == -1:
    idx = text.find('白骨而已')
if idx == -1:
    idx = text.find('发之，白骨')

results = []
results.append(f'Found at: {idx}')
if idx != -1:
    start = max(0, idx - 1200)
    end = idx + 600
    results.append(text[start:end])

with open(r'C:\Users\lx\Desktop\前期准备\youyang-website\scripts\bone_story.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))

print("Done")

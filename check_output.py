import json, os
f = r'C:\Users\lx\Desktop\前期准备\classified_youyang.json'
size = os.path.getsize(f)
print(f'File size: {size/1024/1024:.1f} MB')
with open(f, 'r', encoding='utf-8') as fp:
    data = json.load(fp)
print(f'Paragraphs: {len(data["paragraphs"])}')
print(f'Stories: {len(data["stories"])}')
print(f'Metadata keys: {list(data["metadata"].keys())}')
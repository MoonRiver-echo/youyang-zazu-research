import json
import re
import os

with open(r'C:\Users\lx\Desktop\前期准备\酉阳杂俎-ctext.json', 'r', encoding='utf-8') as f:
    raw = json.load(f)

vol_re = re.compile(r'(卷[一二三四五六七八九十]+·[^\n]+)')
parts = vol_re.split(raw)

volumes = []
for i in range(1, len(parts), 2):
    vol_title = parts[i].strip()
    vol_text = parts[i+1].strip() if i+1 < len(parts) else ''
    volumes.append((vol_title, vol_text))

def split_paragraphs(text):
    lines = text.split('\n')
    paras = []
    cur = ''
    for line in lines:
        line = line.strip()
        if not line:
            if cur.strip():
                paras.append(cur.strip())
                cur = ''
        else:
            if cur:
                cur += line
            else:
                cur = line
    if cur.strip():
        paras.append(cur.strip())
    return paras

all_entries = []
entry_id = 0

for vol_title, vol_text in volumes:
    paras = split_paragraphs(vol_text)
    for p in paras:
        if len(p) < 15:
            continue
        entry_id += 1
        tags = []
        t = p
        if any(k in t for k in ['鬼','魂','魄','冥','尸','夜叉','魅','魍','魉','魑']):
            tags.append('鬼怪')
        if any(k in t for k in ['神','仙','佛','僧','道','巫','寺','庙','祭','咒','梵','塔']):
            tags.append('神佛')
        if any(k in t for k in ['妖','怪','异','奇','幻','精','灵','祟']):
            tags.append('妖怪')
        if any(k in t for k in ['梦','兆','祥','瑞','谶','占','术','方']):
            tags.append('征兆')
        if any(k in t for k in ['龙','凤','麒麟','蛟','螭','龟','蛇']):
            tags.append('神兽')
        if not tags:
            continue
        title = p[:30].replace('「','').replace('」','').replace('【','').replace('】','')
        if len(title) >= 30:
            title = title[:30] + '...'
        all_entries.append({
            'id': f'V{entry_id:04d}',
            'volume': vol_title,
            'text': p,
            'tags': tags,
            'title': title
        })

# Featured stories
featured_specs = [
    {
        'name': '吴刚伐桂',
        'keywords': ['月桂','吴刚','斫之','树创随合'],
        'desc': '月中有桂树，高五百丈。吴刚学仙有过，被谪令伐树，树创随合，永无止境。',
        'quote': '旧言月中有桂，有蟾蜍，故异书言月桂高五百丈，下有一人常斫之，树创随合。人姓吴名刚，西河人，学仙有过，谪令伐树。'
    },
    {
        'name': '修月人',
        'keywords': ['七宝合成','八万二千户','修之','玉屑饭'],
        'desc': '太和中，郑仁本表弟游嵩山迷路，遇一白衣人，告之月乃七宝合成，有八万二千户修之。',
        'quote': '君知月乃七宝合成乎？月势如丸，其影，日烁其凸处也。常有八万二千户修之，予即一数。'
    },
    {
        'name': '胡桃杀人',
        'keywords': ['胡桃','柳氏','碎首','蜂'],
        'desc': '柳氏夜坐，有物如胡桃坠地，掌中遂长，初如拳，如碗，如盘，忽合于其首，碎首而亡。',
        'quote': '柳氏以扇击堕地，乃胡桃也。柳氏遽取玩之掌中，遂长。初如拳，如碗，惊顾之际，已如盘矣。忽合于柳氏首，柳氏碎首，齿著于树。'
    },
    {
        'name': '刘录事',
        'keywords': ['刘录事','骨珠子','茶瓯','鱠'],
        'desc': '和州刘录事善食鱠，咯出一骨珠，置于茶瓯中，顷刻长及人，遂掴刘，良久翕成一人，乃刘也，神已痴矣。',
        'quote': '向者骨珠已长数寸，如人状。座客竞观之，随视而长。顷刻长及人，遂掴刘，因欧流血。'
    },
    {
        'name': '夜叉娶妻',
        'keywords': ['夜叉'],
        'desc': '苏都识匿国有夜叉城，人近窟住者五百馀家，一年再祭。相传夜叉常出窟掠人，有娶妻之说。',
        'quote': '苏都识匿国有夜叉城，城旧有野叉，其窟见在。人近窟住者五百馀家，窟口作舍，设关籥，一年再祭。'
    }
]

featured = []
for spec in featured_specs:
    found = None
    for e in all_entries:
        if all(k in e['text'] for k in spec['keywords']):
            found = e
            break
    if not found:
        for e in all_entries:
            if sum(1 for k in spec['keywords'] if k in e['text']) >= len(spec['keywords']) - 1:
                found = e
                break
    if found:
        featured.append({
            **found,
            'story_name': spec['name'],
            'story_desc': spec['desc'],
            'story_quote': spec['quote']
        })
        print(f"Found: {spec['name']} -> {found['id']}")
    else:
        print(f"NOT FOUND: {spec['name']}")

out_dir = r'C:\Users\lx\Desktop\前期准备\youyang-website'
os.makedirs(out_dir, exist_ok=True)
os.makedirs(os.path.join(out_dir, 'data'), exist_ok=True)

with open(os.path.join(out_dir, 'data', 'entries.json'), 'w', encoding='utf-8') as f:
    json.dump({'entries': all_entries, 'featured': featured}, f, ensure_ascii=False, indent=2)

print(f"Total entries: {len(all_entries)}, Featured: {len(featured)}")
print("Done.")

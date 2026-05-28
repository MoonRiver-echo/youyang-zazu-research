import json
import re
import os

# Read raw text
with open(r'C:\Users\lx\Desktop\前期准备\酉阳杂俎-ctext.json', 'r', encoding='utf-8') as f:
    raw = json.load(f)

# Volume markers
vol_pattern = re.compile(r'卷[一二三四五六七八九十]+·[^\n]+')

# Split into volumes
parts = vol_pattern.split(raw)
headers = vol_pattern.findall(raw)

volumes = []
for h, p in zip(headers, parts[1:]):
    volumes.append((h.strip(), p.strip()))

# Keywords for supernatural/religion filtering
keywords = [
    '鬼','神','怪','妖','魔','狐','夜叉','龙','仙','佛','僧','道','巫','禳',
    '魅','魍','魉','精','灵','魂','魄','尸','冥','祭','咒','符','庙','寺',
    '异','奇','怪','幻','术','方','占','梦','兆','祥','瑞','谶','纬','忌',
    '禁','辟邪','驱','瘟','疫','祟','蛊','毒','蛇','虎','狼','猿','鱼',
    '虫','鸟','兽','木','草','花','石','玉','金','银','珠','宝','剑','镜',
    '琴','棋','书','画','扇','伞','灯','烛','香','炉','鼎','钟','鼓','磬',
    '铃','佩','带','冠','冕','衣','裳','履','袜','巾','帕','枕','席','床',
    '榻','帷','幕','帐','屏','风','槛','栏','梯','桥','楼','阁','台','亭',
    '馆','轩','榭','廊','庑','厢','房','室','堂','庭','院','园','池','沼',
    '潭','泉','溪','涧','河','江','湖','海','波','浪','涛','潮','冰','雪',
    '霜','露','雾','云','霞','虹','霓','雷','电','雨','风','日','月','星',
    '辰','宿','斗','牛','女','虚','危','室','壁','奎','娄','胃','昴','毕',
    '觜','参','井','鬼','柳','星','张','翼','轸','角','亢','氐','房','心',
    '尾','箕','天','地','山','川','岳','岭','峰','峦','丘','壑','谷','峡',
    '坞','坡','岗','陵','原','野','郊','畿','郡','县','乡','里','村','庄',
    '店','铺','驿','关','塞','城','郭','隍','市','坊','巷','街','道','路',
    '途','径','阡','陌','津','渡','航','舶','舟','船','车','马','骑','步',
    '兵','甲','士','卒','将','帅','军','师','旅','团','营','阵','校','尉',
    '官','吏','僚','属','佐','佑','宰','丞','簿','尉','令','长','牧','守',
    '刺','史','伯','侯','公','卿','相','宰','辅','弼','臣','君','王','帝',
    '后','妃','嫔','娥','媛','姬','妾','婢','奴','仆','役','徒','隶','侣',
    '伴','朋','友','宾','客','主','人','氏','族','姓','名','字','号','谥',
    '爵','封','邑','土','田','宅','庐','舍','屋','宇','宫','殿','阙','门',
    '户','扉','牖','窗','槛','阶','除','墀','址','基','垣','墙','壁','堵',
    '雉','堞','垒','堡','寨','营','屯','栅','篱','落','藩','屏','障','塞',
    '隘','崄','峻','峭','陡','危','险','阻','绝','僻','幽','邃','窈','冥',
    '暗','晦','昏','暮','夜','晓','曙','晨','旦','朝','午','晡','夕','晚',
    '昏','黄','黑','白','赤','青','苍','翠','碧','紫','红','绯','绛','朱',
    '丹','彤','赭','褐','黄','缃','橙','绿','蓝','靛','灰','素','玄','墨',
    '漆','油','粉','脂','膏','泽','液','汁','浆','醴','酪','酥','膏','油',
    '盐','酱','醋','豉','醢','醯','酢','酿','醇','醪','醑','醴','酒','茶',
    '汤','粥','饭','食','馔','肴','膳','羞','珍','味','腥','荤','素','斋',
    '蔬','菜','果','瓜','瓠','芋','薯','蔗','荠','笋','菌','芝','苓','术',
    '芷','兰','蕙','茝','蓠','蘅','杜','若','蘼','芜','菁','莪','蒿','蓬',
    '茅','苇','芦','荻','蒲','荷','莲','菡','萏','芙','蓉','蔷','薇','玫',
    '瑰','芍','药','牡','丹','芙','蓉','海','棠','梨','桃','杏','李','梅',
    '樱','桔','柚','柑','橙','枳','枸','檵','杞','菊','兰','桂','椿','槐',
    '榆','柳','杨','柏','松','杉','梧','桐','梓','樟','楠','檀','柘','桑',
    '柘','栎','柞','楢','椐','樗','栲','柯','条','枚','枝','干','根','株',
    '本','末','杪','梢','叶','花','蕊','萼','瓣','房','实','核','仁','皮',
    '肤','肌','肉','骨','髓','脑','血','脉','筋','膜','脂','膏','油','汗',
    '泪','涕','唾','涎','沫','痰','溺','便','矢','屎','尿','溲','屁','气',
    '息','臭','香','味','声','音','响','韵','调','律','吕','钟','磬','鼓',
    '琴','瑟','筝','笛','箫','笙','竽','簧','埙','篪','笳','茄','管','弦',
    '丝','竹','匏','革','木','石','金','土','革','丝','竹','匏','土','木',
    '八音','五声','六律','七政','八卦','九宫','十干','十二支','二十八宿',
    '三十六禽','七十二候','三百六十日','四千五百鸟','二千四百兽','三万六千神'
]

# We already have structured classification data from grep
# Let's build entries from the raw text by splitting paragraphs

def split_paragraphs(text):
    # Split by blank lines or by sentences that look like paragraph starts
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
            cur += line
    if cur.strip():
        paras.append(cur.strip())
    return paras

# Build all entries
all_entries = []
entry_id = 0

for vol_title, vol_text in volumes:
    paras = split_paragraphs(vol_text)
    for p in paras:
        if len(p) < 10:
            continue
        entry_id += 1
        # Determine tags based on content
        tags = []
        if any(k in p for k in ['鬼','魂','魄','冥','尸','夜叉','魅','魍','魉']):
            tags.append('鬼怪')
        if any(k in p for k in ['神','仙','佛','僧','道','巫','寺','庙','祭','咒']):
            tags.append('神佛')
        if any(k in p for k in ['妖','怪','异','奇','幻','精','灵']):
            tags.append('妖怪')
        if any(k in p for k in ['梦','兆','祥','瑞','谶','占','术']):
            tags.append('征兆')
        if not tags:
            tags.append('杂录')
        
        all_entries.append({
            'id': f'V{entry_id:04d}',
            'volume': vol_title,
            'text': p,
            'tags': tags,
            'title': p[:20] + '...' if len(p) > 20 else p
        })

# Featured stories - find by keyword
featured_keywords = {
    '吴刚伐桂': ['吴刚','伐桂','月桂','桂树'],
    '胡桃杀人': ['胡桃','柳氏','蜂','盘','碎首'],
    '修月人': ['修月','月乃七宝','八万二千户'],
    '刘录事': ['刘录事','骨珠子','茶瓯','鱠'],
    '夜叉娶妻': ['夜叉','娶','妻','嫁','野叉']
}

featured = []
for name, kws in featured_keywords.items():
    found = None
    for e in all_entries:
        if all(k in e['text'] for k in kws):
            found = e
            break
    if not found:
        # fallback: partial match
        for e in all_entries:
            if sum(1 for k in kws if k in e['text']) >= max(1, len(kws)-1):
                found = e
                break
    if found:
        featured.append({**found, 'story_name': name})
    else:
        print(f"Warning: {name} not found")

print(f"Total entries: {len(all_entries)}")
print(f"Featured found: {len(featured)}")
for f in featured:
    print(f"  - {f['story_name']}: {f['id']} ({f['volume']})")

# Save data
output_dir = r'C:\Users\lx\Desktop\前期准备\youyang-website'
os.makedirs(output_dir, exist_ok=True)
os.makedirs(os.path.join(output_dir, 'data'), exist_ok=True)
os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)

with open(os.path.join(output_dir, 'data', 'entries.json'), 'w', encoding='utf-8') as f:
    json.dump({
        'entries': all_entries,
        'featured': featured
    }, f, ensure_ascii=False, indent=2)

print("Data saved.")

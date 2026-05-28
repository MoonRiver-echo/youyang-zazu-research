import sqlite3
import json
import os

db_path = 'C:/Users/lx/Desktop/前期准备/academic-website/data/youyang.db'
if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute('''CREATE TABLE entries (
    id TEXT PRIMARY KEY,
    volume TEXT,
    title TEXT,
    text TEXT,
    tags TEXT
)''')

c.execute('''CREATE TABLE tags (
    tag TEXT,
    entry_id TEXT,
    FOREIGN KEY (entry_id) REFERENCES entries(id)
)''')

c.execute('''CREATE TABLE narrative_categories (
    category TEXT PRIMARY KEY,
    core_plot TEXT,
    count INTEGER,
    description TEXT
)''')

c.execute('''CREATE TABLE stats (
    metric TEXT PRIMARY KEY,
    value TEXT,
    note TEXT
)''')

with open('C:/Users/lx/Desktop/前期准备/academic-website/data/entries.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for e in data['entries']:
    c.execute('INSERT INTO entries VALUES (?,?,?,?,?)',
              (e['id'], e.get('volume',''), e.get('title',''), e.get('text',''), ','.join(e.get('tags',[]))))
    for t in e.get('tags',[]):
        c.execute('INSERT INTO tags VALUES (?,?)', (t, e['id']))

# Narrative categories from thesis
cats = [
    ('变化', '以形变为核心，强调人与异类之间的转换变化', 23, '包括人变为异类、异类现原形、画与人的双向互动'),
    ('遭遇', '以人与异类正面相遇为核心，强调遭遇这一过程本身', 18, '分为敌对关系与共存关系两个子类'),
    ('梦', '以梦中经历为核心，梦在叙述中起到传递信息的作用', 7, '遵循入梦—梦中事件—梦觉验证结构'),
    ('冥界', '以阳间之人接触冥司为核心，表现为两种制度的交互', 6, '体现冥界官僚体系与人间官场的相似性'),
    ('预兆', '以先兆与应验为核心，往往表现为延后应验', 9, '先兆在现实生活中被发现，具有较长故事时间'),
    ('因果', '以行为的后果为核心，情节之间有明显的因果关系连接', 4, '强调善恶报应的教化功能'),
    ('禁忌', '以触犯规则的后果为核心，对象往往是某种奇物', 3, '触碰禁忌物导致灾祸'),
    ('异境', '以进入异空间为核心，异空间与正常空间以水、洞等相连', 5, '仙境的世俗化特征：时间短、距离近、进入方式日常化'),
    ('遇鬼', '以直接遭遇鬼魂为核心，往往描述与鬼的互动', 4, '人鬼之间的直接接触'),
    ('物怪', '围绕奇异物品展开，物怪通常不具有意识', 7, '日常器物或自然物的异变'),
    ('病治', '以超自然的疾病为核心，情节集中在致病和治病上', 4, '疾病由超自然力量引起'),
    ('术法', '以降伏妖魔为核心，主人公多为道士、僧人', 5, '宗教权威对超自然力量的规训')
]
for cat in cats:
    c.execute('INSERT INTO narrative_categories VALUES (?,?,?,?)', cat)

stats = [
    ('total_entries', '419', '标注条目总数'),
    ('total_tag_freq', '728', '标签总频次'),
    ('volumes_covered', '20', '涉及卷目数'),
    ('multi_label_entries', '286', '多标签条目数'),
    ('nuogao_total', '147', '诺皋五篇总条目数'),
    ('nuogao_narrative', '95', '诺皋五篇叙事文本数'),
    ('classification_accuracy', '90%+', '三轮标注后准确率')
]
for s in stats:
    c.execute('INSERT INTO stats VALUES (?,?,?)', s)

conn.commit()
conn.close()
print('SQLite database created successfully')

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
酉阳杂俎 三校版 数据库构建 + 可视化Web应用
1) 解析三校文本 + 分类数据 → SQLite数据库
2) 启动HTTP服务器，提供可视化界面
端口: 8891
"""
import sqlite3
import os
import sys
import re
import json
from collections import defaultdict
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(r"C:\Users\lx\Desktop\前期准备\清洗数据")
INPUT_FILE = BASE_DIR / "酉阳杂俎-三校.md"
DB_PATH = BASE_DIR / "youyang_zazu.db"
PORT = 8891

# ============================================================
# 分类体系
# ============================================================
VOLUME_CATEGORIES = {
    "序": "史料序跋", "忠志": "帝王纪事", "礼异": "礼俗制度",
    "天咫": "天文地理", "玉格": "佛道异闻", "壶史": "神仙方术",
    "贝编": "佛道异闻", "境异": "异境异域", "喜兆": "征兆占验",
    "祸兆": "征兆占验", "物革": "事物怪变", "诡习": "器艺技法",
    "怪术": "术法幻术", "艺绝": "器艺技法", "器奇": "器物名物",
    "乐": "器艺技法", "酒食": "饮食医药", "医": "饮食医药",
    "黥": "礼俗制度", "雷": "天文地理", "梦": "梦兆占验",
    "事感": "精诚感应", "盗侠": "侠盗刺客", "物异": "异物异象",
    "广知": "广知博物", "语资": "语资谈助", "冥迹": "幽冥冥迹",
    "尸穸": "丧葬礼俗", "诺皋记上": "异闻志怪", "诺皋记下": "异闻志怪",
    "广动植之一": "动植物谱录", "广动植之二": "动植物谱录",
    "广动植之三": "动植物谱录", "广动植类之四": "动植物谱录",
    "肉攫部": "器艺技法", "支诺皋上": "异闻志怪", "支诺皋中": "异闻志怪",
    "支诺皋下": "异闻志怪", "贬误": "知识考辨", "寺塔记上": "佛寺塔庙",
    "寺塔记下": "佛寺塔庙", "金刚经鸠异": "佛道异闻",
    "支动": "动植物谱录", "支植上": "动植物谱录", "支植下": "动植物谱录",
}

THEME_KEYWORDS = {
    "人物政事": {"帝王": ['帝','上','天子','诏','敕','玄宗','太宗','高宗','肃宗','代宗','中宗'], "人物": ['成式','公','卿','大夫','刺史','令','尉','将军','尚书','侍郎'], "僧": ['僧','沙弥','比丘','禅师','上人','法师','梵僧'], "道士": ['道','道士','天师','真人','先生','山人'], "侠盗": ['侠','盗','刺客','贼','劫','夜叉']},
    "动物": {"鸟类": ['鸟','鹊','鹰','鹤','雁','燕','雀','凤','鸱','鸢','雉','鸦','乌','鹅','鹭','鸽','鹦','雕'], "兽类": ['虎','鹿','马','牛','羊','犬','狗','豕','猪','象','狮','豹','熊','猴','猿','狐','兔','鼠','猫','狼','驼','骡'], "鱼类": ['鱼','鲤','鲫','鲈','鳖','龟','鳗','鳝','鲙','鲸'], "爬行": ['蛇','蜥','龟','鳄','蜃','蟒'], "昆虫": ['虫','蚁','蜂','蝶','蛾','蝉','蜻','萤','蝗','螳','蛛','蝇'], "神物": ['龙','蛟','螭','虬','凤','麟','麒麟']},
    "鬼怪妖魅": {"鬼": ['鬼','亡魂','魂魄','游魂','幽魂','鬼官','鬼魅'], "仙": ['仙','仙人','飞仙','神仙','真仙','地仙'], "精": ['精','妖精','狐精','蛇精','树精'], "魅": ['魅','魑魅','魍魉'], "妖": ['妖','妖怪','妖精','妖魅'], "魔": ['魔','妖魔','天魔','夜叉','修罗']},
    "建筑寺塔": {"宫殿": ['宫','宫殿','殿','堂','阁','台'], "寺观": ['寺','寺庙','兰若','伽蓝','观','道观','院','庵'], "城楼": ['城','楼','门','墙','坊','郭']},
    "器物技艺": {"武器": ['剑','刀','戟','戈','矛','弓','箭','鞭','盾'], "镜": ['镜'], "用具": ['盘','碗','杯','鼎','壶','瓶','匣','箱','炉'], "衣饰": ['衣','冠','带','履','衾','裘','袍','裙','帛'], "乐器": ['鼓','钟','磬','琴','瑟','箫','笛','琵琶']},
    "佛道信仰": {"佛": ['佛','释','菩萨','罗汉','涅槃','舍利'], "道": ['道','老君','太上','太极','真人'], "经法": ['经','法','戒','禅','论','咒','符','梵']},
    "丧葬冥界": {"葬": ['葬','墓','棺','坟','椁','冢','殉'], "冥": ['冥','阴间','地府','黄泉','幽冥','阎罗'], "尸": ['尸','尸解','不朽','僵尸','骸骨']},
    "饮食医药": {"食": ['食','煮','饮','饼','羹','粥','脍','鲙','馄饨'], "药": ['药','丹','丸','散','汤','医','治','病','疾'], "酒": ['酒','酿','醪','醑','醅'], "茶": ['茶','茗']},
    "梦兆占卜": {"梦": ['梦','入梦','托梦','梦中','凶梦','吉梦'], "兆": ['兆','占','卜','谶','瑞','凶','吉','祈']},
    "异域物产": {"异国": ['波斯','西域','天竺','大食','突厥','龟兹','于阗','拂林','昆仑','胡']},
    "天文地理": {"天象": ['日','月','星','风','雨','雷','电','云','雾','霜','雪','虹'], "地理": ['山','水','泉','井','河','江','海','湖','洞','谷']},
    "植物": {"木": ['松','柏','柳','槐','桑','榆','桐','桂','竹','檀','梅'], "果": ['桃','李','杏','柿','枣','梨','橘','柚'], "花": ['花','莲','菊','兰','牡丹','芙蓉'], "草": ['草','芝','茅','苇','芦','艾','蒿','苔','萍']},
}

CORE_SHENGUI = ['神','鬼','仙','妖','魔','魅','怪','精','佛','僧','道','龙','蛟','凤','麒麟','狐','变','尸解','冥','魂','魄','地狱','天帝','菩萨','袈裟','符','咒','术士','法师','天师','巫','真人','飞行','变化','异人','不空','万回','一行','罗公远','邢和璞','翟天师']
SEC_SHENGUI = ['灵','瑞','谶','兆','梦','卜','占','祈','丹','修炼','飞升','得道','破戒','超度','转世','轮回','阴间','阳间','天宫','地府','阎罗','判官','夜叉','阿修罗','毗沙门','观音','舍利','佛光','神光','灵光','圣迹','巫术','法术','妖术','幻术','仙术','黄白','丹砂','长生','不死','托梦','入梦','显灵','降神','怪异','奇异']
SHENGUI_VOLS = {"诺皋记上","诺皋记下","支诺皋上","支诺皋中","支诺皋下"}

NARRATIVE_THEMES = {
    "死者复活": ['复生','还魂','再生','复苏','起死','更生','魂归'],
    "鬼魂还阳": ['还阳','魂归','鬼魂','亡魂','游魂','附身','托生'],
    "生死边界": ['冥','阴间','地府','黄泉','幽冥','阳间','还魂','入冥'],
    "丧葬再生": ['葬','墓','冢','棺','椁','殉','祭','发冢'],
    "迷路返回时间流逝": ['迷','迷路','失路','不知所之','归路','还家','不得归'],
    "时间错位": ['经年','数日','忽觉','须臾','瞬息','岁月','倏忽','恍然'],
    "空间异变": ['忽见','异境','异地','仙境','洞天','福地','幻境'],
    "天上人间": ['天宫','上天','天帝','仙界','降世','天上','人间','下凡'],
    "人兽互变": ['化为人','变为','变形','幻化','人形','兽形','狐变','蛇变'],
    "物怪变形": ['化为','忽变','变形','物怪','成精','作怪','妖怪'],
    "妖魅惑人": ['魅','惑','迷','妖','淫','色','幻','惑人'],
    "修道成仙": ['修炼','得道','飞升','真人','羽化','辟谷','炼丹','黄白'],
    "僧尼异事": ['僧','尼','寺','佛','禅','经','咒','戒','袈裟','斋'],
    "法术幻术": ['术','法','幻','隐形','变化','奇术','遁','遁术'],
    "因果报应": ['报应','因果','善报','恶报','罚','赎','劫','还报','业'],
    "佛法灵验": ['佛','观音','菩萨','经','念','灵验','显灵','护法'],
    "梦兆应验": ['梦','入梦','托梦','兆','应','征','谶','吉梦','凶梦'],
    "占卜预言": ['占','卜','谶','预言','相','算','推'],
    "祥瑞灾异": ['瑞','祥','灾','异','天象','蚀','蝗','旱','水'],
    "异物奇珍": ['异','奇','宝','珍','异物','奇珍','珠','玉'],
    "动植怪变": ['变异','怪','异','畸形','双头','无目'],
    "自然怪象": ['风','雨','雷','电','虹','雾','霜','天变'],
    "侠客义行": ['侠','义','刺客','盗','劫','杀','报恩','报仇'],
    "奇人异能": ['异人','奇术','绝技','高手','异能','神力'],
    "隐逸高人": ['隐','逸','山人','处士','高人'],
    "忠孝节义": ['忠','孝','节','义','烈','贞','廉','仁'],
    "冤屈报应": ['冤','屈','雪','伸','冤魂','复仇'],
    "情爱奇闻": ['婚','嫁','妻','妾','情','恋','美','缘'],
}

MONSTER_TYPES = {
    "神话异兽": ['帝江','刑天','异兽','怪兽','大蛇','毒龙','飞头','夜叉','蛟','螭','虬'],
    "神仙志怪": ['仙','真人','天帝','灶神','得道','飞升','修炼','羽化','尸解','道士'],
    "妖怪变形": ['变','妖','魅','化','幻','精','狐','蛇精'],
    "降妖伏魔": ['降','伏','斩','收','制服','破','驱除','禳','除妖','镇'],
    "民俗神灵": ['灶神','门神','土地','城隍','河伯','山神','风伯','雨师','雷公','龙王'],
    "佛道灵异": ['佛','僧','道','寺','观','菩萨','罗汉','经','咒','法','舍利','灵光','袈裟'],
    "冥界报应": ['冥','地狱','阎罗','判官','鬼','阴间','报应','还魂','转世','罚'],
    "梦兆占验": ['梦','兆','谶','占','卜','祈','瑞','入梦','托梦'],
    "术法幻术": ['术','法','幻','隐形','变化','咒','符','奇术','幻术'],
    "异域怪物": ['异域','波斯','西域','天竺','外国','蛮','胡','大食'],
    "尸解变化": ['尸解','尸','不朽','不腐','僵尸','骸骨'],
    "事物怪变": ['忽变','怪变','异变','化为','变异'],
}

DESC_SUBJECTS = {
    "人物志": ['人','士','官','将','臣','帝','王','公','卿','僧','道','尼','医','匠','侠','盗'],
    "动植矿物": ['鸟','兽','鱼','虫','草','木','花','石','金','玉','药','龙','蛇','虎','鹿','马','犬','狐'],
    "地理建筑": ['山','水','城','寺','塔','观','宫','殿','门','桥','路','河','海','湖'],
    "器物技艺": ['剑','刀','弓','镜','钟','鼓','琴','书','画','药','丹','符','印'],
    "礼俗制度": ['礼','祭','葬','婚','冠','服','官','律','刑','赋','贡'],
    "天文气象": ['日','月','星','风','雨','雷','电','云','雾','霜','雪','虹'],
    "佛道宗教": ['佛','僧','道','寺','观','经','咒','符','仙','禅','菩萨','罗汉','地狱','天宫'],
    "鬼神怪异": ['鬼','神','妖','魅','精','魔','怪','魂','魄','冥','阴','阳','尸'],
    "梦兆占卜": ['梦','兆','占','卜','谶','瑞','凶','吉','祈'],
    "食药物产": ['食','饮','酒','茶','药','丹','果','蔬','肉','鱼','米','麦'],
}


def get_vol_short(t):
    if '·' in t: return t.split('·',1)[1]
    return t.replace('续·','')

def get_cat(t):
    n = get_vol_short(t)
    for k,v in VOLUME_CATEGORIES.items():
        if k in n or n in k: return v
    if '广动植' in n: return '动植物谱录'
    if '诺皋' in n: return '异闻志怪'
    if '支诺皋' in n: return '异闻志怪'
    if '寺塔' in n: return '佛寺塔庙'
    if '支植' in n or '支动' in n: return '动植物谱录'
    return '未分类'

def is_shengui(text, vs, cat):
    if vs in SHENGUI_VOLS: return True
    c = sum(1 for k in CORE_SHENGUI if k in text)
    if c >= 2: return True
    s = sum(1 for k in SEC_SHENGUI if k in text)
    if s >= 3: return True
    if c >= 1 and s >= 1: return True
    if cat in ["佛道异闻","神仙方术","异闻志怪","幽冥冥迹","丧葬礼俗","梦兆占验","征兆占验","事物怪变","术法幻术","异物异象","异境异域"]:
        if c >= 1 or s >= 2: return True
    return False

def get_monster_type(text):
    scores = {}
    for mt, kws in MONSTER_TYPES.items():
        s = sum(1 for k in kws if k in text)
        if s > 0: scores[mt] = s
    if not scores:
        if '佛' in text or '僧' in text or '道' in text: return "佛道灵异"
        if '鬼' in text or '冥' in text: return "冥界报应"
        if '梦' in text: return "梦兆占验"
        if '变' in text or '化' in text: return "妖怪变形"
        return "神仙志怪"
    return max(scores, key=scores.get)

def get_narr_themes(text):
    themes = []
    for name, kws in NARRATIVE_THEMES.items():
        c = sum(1 for k in kws if k in text)
        if c >= 2: themes.append(name)
        elif c == 1 and len(kws) <= 3: themes.append(name)
    if not themes:
        for name, kws in NARRATIVE_THEMES.items():
            if any(k in text for k in kws):
                themes.append(name)
                if len(themes) >= 2: break
    return themes

def get_desc_subjects(text):
    subjects = []
    for subj, kws in DESC_SUBJECTS.items():
        if sum(1 for k in kws if k in text) >= 3:
            subjects.append(subj)
    if not subjects:
        for subj, kws in DESC_SUBJECTS.items():
            if sum(1 for k in kws if k in text) >= 2:
                subjects.append(subj)
                if len(subjects) >= 2: break
    return subjects if subjects else ["事迹叙述"]

def get_theme_details(text):
    result = {}
    for broad, subcats in THEME_KEYWORDS.items():
        sub_m = {}
        for sub, kws in subcats.items():
            found = [k for k in kws if k in text]
            if found: sub_m[sub] = found[:3]
        if sub_m: result[broad] = sub_m
    return result

def parse_sanjiao(content):
    lines = content.split('\n')
    vols = []
    cv = None; cp = []
    for l in lines:
        s = l.strip()
        if not s: continue
        if s.startswith('## '):
            if cv and cp: vols.append((cv, cp))
            cv = s[3:].strip(); cp = []
        elif len(s) > 5: cp.append(s)
    if cv and cp: vols.append((cv, cp))
    return vols


# ============================================================
# 1. Build Database
# ============================================================
def build_db():
    print("读取三校文件...")
    content = INPUT_FILE.read_text(encoding='utf-8')
    vols = parse_sanjiao(content)
    print(f"解析到 {len(vols)} 卷")

    if DB_PATH.exists(): DB_PATH.unlink()
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()

    c.execute("""CREATE TABLE paragraphs (
        pid TEXT PRIMARY KEY,
        volume_index INTEGER,
        volume_title TEXT,
        volume_short TEXT,
        narrative_category TEXT,
        text TEXT,
        text_length INTEGER,
        has_supernatural INTEGER DEFAULT 0
    )""")
    c.execute("""CREATE TABLE shengui (
        pid TEXT PRIMARY KEY,
        volume_title TEXT,
        monster_type TEXT,
        narrative_themes TEXT,
        title TEXT,
        brief TEXT,
        shengui_keywords TEXT,
        FOREIGN KEY(pid) REFERENCES paragraphs(pid)
    )""")
    c.execute("""CREATE TABLE description_subjects (
        pid TEXT,
        subject TEXT
    )""")
    c.execute("""CREATE TABLE theme_details (
        pid TEXT,
        broad_category TEXT,
        level1_subject TEXT,
        specific_subject TEXT,
        keywords TEXT
    )""")
    c.execute("""CREATE TABLE narrative_stats (
        narrative_category TEXT PRIMARY KEY,
        paragraph_count INTEGER,
        percentage REAL
    )""")
    c.execute("""CREATE TABLE monster_type_stats (
        monster_type TEXT PRIMARY KEY,
        paragraph_count INTEGER
    )""")
    c.execute("""CREATE TABLE theme_frequency (
        theme_name TEXT,
        frequency INTEGER
    )""")

    vol_idx = 0
    cat_stats = defaultdict(int)
    mt_stats = defaultdict(int)
    theme_freq = defaultdict(int)

    for vol_title, paras in vols:
        vs = get_vol_short(vol_title)
        cat = get_cat(vol_title)
        is_xu = vol_title.startswith('续·')
        for pi, para in enumerate(paras, 1):
            prefix = "S" if vol_idx == 0 else ("X" if is_xu else "V")
            pid = f"{prefix}{vol_idx:02d}-P{pi:03d}"
            has_sg = is_shengui(para, vs, cat)
            cat_stats[cat] += 1

            c.execute("INSERT INTO paragraphs VALUES (?,?,?,?,?,?,?,?)",
                (pid, vol_idx, vol_title, vs, cat, para, len(para), 1 if has_sg else 0))

            for subj in get_desc_subjects(para):
                pass  # skip first pass, will insert in second pass below
            # re-do:
            pass

            td = get_theme_details(para)
            for broad, subs in td.items():
                for sub, kws in subs.items():
                    c.execute("INSERT INTO theme_details VALUES (?,?,?,?,?)",
                        (pid, broad, sub, sub, '、'.join(kws)))
                    theme_freq[sub] += 1

            if has_sg:
                mt = get_monster_type(para)
                nt = get_narr_themes(para)
                kws = [k for k in CORE_SHENGUI+SEC_SHENGUI if k in para]
                title = re.sub(r'[（\(][^）\)]*[）\)]','',para)[:20]
                brief = para[:80] + ('……' if len(para)>80 else '')
                c.execute("INSERT INTO shengui VALUES (?,?,?,?,?,?,?)",
                    (pid, vol_title, mt, '、'.join(nt), title, brief, '、'.join(kws)))
                mt_stats[mt] += 1

        vol_idx += 1

    # Fix description_subjects - need separate table column
    # Re-create with proper schema
    c.execute("DELETE FROM description_subjects")
    vol_idx2 = 0
    for vol_title, paras in vols:
        vs = get_vol_short(vol_title)
        is_xu = vol_title.startswith('续·')
        for pi, para in enumerate(paras, 1):
            prefix = "S" if vol_idx2 == 0 else ("X" if is_xu else "V")
            pid = f"{prefix}{vol_idx2:02d}-P{pi:03d}"
            for subj in get_desc_subjects(para):
                c.execute("INSERT INTO description_subjects VALUES (?,?)", (pid, subj))
        vol_idx2 += 1

    total = sum(cat_stats.values())
    for cat, count in cat_stats.items():
        c.execute("INSERT OR REPLACE INTO narrative_stats VALUES (?,?,?)",
            (cat, count, round(count/total*100, 1)))
    for mt, count in mt_stats.items():
        c.execute("INSERT OR REPLACE INTO monster_type_stats VALUES (?,?)", (mt, count))
    for theme, freq in theme_freq.items():
        c.execute("INSERT INTO theme_frequency VALUES (?,?)", (theme, freq))

    conn.commit()

    # Print stats
    for table in ['paragraphs','shengui','description_subjects','theme_details','narrative_stats','monster_type_stats','theme_frequency']:
        c.execute(f"SELECT COUNT(*) FROM {table}")
        print(f"  {table}: {c.fetchone()[0]} 条")

    conn.commit()
    return conn, vols


# ============================================================
# 2. Build JSON data for web
# ============================================================
def build_json_data(conn, vols):
    c = conn.cursor()

    # Paragraphs
    c.execute("SELECT * FROM paragraphs ORDER BY volume_index, pid")
    paragraphs = []
    cols = ['pid','volume_index','volume_title','volume_short','narrative_category','text','text_length','has_supernatural']
    for row in c.fetchall():
        paragraphs.append(dict(zip(cols, row)))

    # Shengui
    c.execute("SELECT * FROM shengui ORDER BY pid")
    shengui = []
    cols2 = ['pid','volume_title','monster_type','narrative_themes','title','brief','shengui_keywords']
    for row in c.fetchall():
        shengui.append(dict(zip(cols2, row)))

    # Stats
    c.execute("SELECT * FROM narrative_stats ORDER BY paragraph_count DESC")
    narr_stats = [dict(zip(['narrative_category','paragraph_count','percentage'], row)) for row in c.fetchall()]

    c.execute("SELECT * FROM monster_type_stats ORDER BY paragraph_count DESC")
    mt_stats = [dict(zip(['monster_type','paragraph_count'], row)) for row in c.fetchall()]

    c.execute("SELECT * FROM theme_frequency ORDER BY frequency DESC")
    tf = [dict(zip(['theme_name','frequency'], row)) for row in c.fetchall()]

    # Volume summary
    vol_summary = []
    for vol_title, paras in vols:
        vs = get_vol_short(vol_title)
        cat = get_cat(vol_title)
        c.execute("SELECT COUNT(*), SUM(has_supernatural) FROM paragraphs WHERE volume_title=?", (vol_title,))
        row = c.fetchone()
        vol_summary.append({
            'volume_title': vol_title, 'volume_short': vs,
            'narrative_category': cat, 'total': row[0], 'shengui_count': row[1] or 0
        })

    data = {
        'paragraphs': paragraphs,
        'shengui': shengui,
        'narrative_stats': narr_stats,
        'monster_type_stats': mt_stats,
        'theme_frequency': tf,
        'volume_summary': vol_summary,
        'total_paragraphs': len(paragraphs),
        'total_shengui': len(shengui),
    }
    return data


# ============================================================
# 3. Web Handler
# ============================================================
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>《酉阳杂俎》三校版 数据库可视化</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Microsoft YaHei','SimHei',sans-serif; background:#1a1a2e; color:#e0e0e0; }
.header { background:#16213e; padding:20px; text-align:center; border-bottom:2px solid #0f3460; }
.header h1 { font-size:28px; color:#e94560; }
.header p { color:#a0a0c0; margin-top:5px; }
.tabs { display:flex; background:#16213e; border-bottom:1px solid #0f3460; overflow-x:auto; }
.tab { padding:12px 20px; cursor:pointer; color:#a0a0c0; border-bottom:3px solid transparent; white-space:nowrap; transition:all .2s; }
.tab:hover { color:#e94560; }
.tab.active { color:#e94560; border-bottom-color:#e94560; background:#1a1a2e; }
.content { padding:20px; max-width:1400px; margin:0 auto; }
.panel { display:none; }
.panel.active { display:block; }
.stats-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:15px; margin:20px 0; }
.stat-card { background:#16213e; border-radius:8px; padding:15px; text-align:center; border:1px solid #0f3460; }
.stat-card h3 { font-size:14px; color:#a0a0c0; }
.stat-card .num { font-size:32px; color:#e94560; font-weight:bold; }
table { width:100%; border-collapse:collapse; margin:15px 0; font-size:13px; }
th { background:#0f3460; color:#e94560; padding:8px 6px; text-align:left; position:sticky; top:0; }
td { padding:6px; border-bottom:1px solid #0f3460; }
tr:hover { background:#1a1a3e; }
.search-box { width:100%; padding:10px; margin:10px 0; background:#16213e; border:1px solid #0f3460; color:#e0e0e0; border-radius:4px; font-size:14px; }
.badge { display:inline-block; padding:2px 8px; border-radius:3px; font-size:11px; margin:1px; }
.badge-sg { background:#e94560; color:#fff; }
.badge-cat { background:#0f3460; color:#e0e0e0; }
.badge-mt { background:#533483; color:#fff; }
.chart-bar { height:24px; background:linear-gradient(90deg,#e94560,#533483); border-radius:3px; transition:width .3s; }
.chart-row { display:flex; align-items:center; margin:4px 0; }
.chart-label { width:100px; text-align:right; padding-right:8px; font-size:12px; color:#a0a0c0; }
.chart-value { font-size:12px; color:#e0e0e0; padding-left:5px; }
.shengui-tag { display:inline-block; padding:1px 6px; margin:1px; border-radius:3px; font-size:11px; background:#533483; color:#fff; }
</style>
</head>
<body>
<div class="header">
<h1>《酉阳杂俎》三校版 数据库可视化</h1>
<p>总段落: <span id="total">0</span> | 神怪段落: <span id="total-sg">0</span> | 叙事类别: <span id="total-cat">0</span> | 怪物类型: <span id="total-mt">0</span></p>
</div>
<div class="tabs">
<div class="tab active" data-tab="overview">总览</div>
<div class="tab" data-tab="volumes">卷目统计</div>
<div class="tab" data-tab="narrative">叙事类别</div>
<div class="tab" data-tab="monster">怪物类型</div>
<div class="tab" data-tab="themes">叙事主题</div>
<div class="tab" data-tab="shengui">神怪明细</div>
<div class="tab" data-tab="search">段落检索</div>
</div>
<div class="content">
<div class="panel active" id="panel-overview"></div>
<div class="panel" id="panel-volumes"></div>
<div class="panel" id="panel-narrative"></div>
<div class="panel" id="panel-monster"></div>
<div class="panel" id="panel-themes"></div>
<div class="panel" id="panel-shengui"></div>
<div class="panel" id="panel-search"></div>
</div>
<script>
const DATA = __JSON_DATA__;
const CAT_COLORS = {
    '动植物谱录':'#4CAF50','异闻志怪':'#FF5722','佛道异闻':'#9C27B0','异物异象':'#FF9800',
    '器艺技法':'#607D8B','知识考辨':'#795548','佛寺塔庙':'#673AB7','礼俗制度':'#00BCD4',
    '广知博物':'#8BC34A','丧葬礼俗':'#F44336','异境异域':'#03A9F4','语资谈助':'#CDDC39',
    '饮食医药':'#FFEB3B','帝王纪事':'#E91E63','术法幻术':'#FFC107','梦兆占验':'#3F51B5',
    '天文地理':'#009688','神仙方术':'#FF4081','侠盗刺客':'#424242','征兆占验':'#8D6E63',
    '事物怪变':'#A1887F','器物名物':'#BDBDBD','幽冥冥迹':'#D32F2F','精诚感应':'#26A69A',
    '史料序跋':'#78909C','未分类':'#9E9E9E'
};

document.getElementById('total').textContent = DATA.total_paragraphs;
document.getElementById('total-sg').textContent = DATA.total_shengui;
document.getElementById('total-cat').textContent = DATA.narrative_stats.length;
document.getElementById('total-mt').textContent = DATA.monster_type_stats.length;

function renderOverview(){
    const p = document.getElementById('panel-overview');
    let html = '<h2 style="color:#e94560;margin-bottom:15px">数据总览</h2>';
    html += '<div class="stats-grid">';
    const cards = [
        ['总段落',DATA.total_paragraphs],['神怪段落',DATA.total_shengui],
        ['非神怪',DATA.total_paragraphs-DATA.total_shengui],
        ['叙事类别',DATA.narrative_stats.length],
        ['怪物类型',DATA.monster_type_stats.length],
        ['卷数',DATA.volume_summary.length]
    ];
    cards.forEach(([label,val])=>{
        html += `<div class="stat-card"><h3>${label}</h3><div class="num">${val}</div></div>`;
    });
    html += '</div>';
    html += '<h3 style="color:#e94560;margin:20px 0 10px">叙事类别分布</h3>';
    DATA.narrative_stats.forEach(s=>{
        const w = s.percentage * 3;
        html += `<div class="chart-row"><div class="chart-label">${s.narrative_category}</div><div style="flex:1"><div class="chart-bar" style="width:${w}px"></div></div><div class="chart-value">${s.paragraph_count} (${s.percentage}%)</div></div>`;
    });
    p.innerHTML = html;
}

function renderVolumes(){
    const p = document.getElementById('panel-volumes');
    let html = '<h2 style="color:#e94560;margin-bottom:15px">各卷统计</h2>';
    html += '<table><tr><th>卷名</th><th>叙事类别</th><th>总段数</th><th>神怪段数</th><th>神怪占比</th></tr>';
    DATA.volume_summary.forEach(v=>{
        const pct = v.total>0 ? (v.shengui_count/v.total*100).toFixed(1)+'%' : '-';
        html += `<tr><td>${v.volume_title}</td><td><span class="badge badge-cat">${v.narrative_category}</span></td><td>${v.total}</td><td>${v.shengui_count}</td><td>${pct}</td></tr>`;
    });
    html += '</table>';
    p.innerHTML = html;
}

function renderNarrative(){
    const p = document.getElementById('panel-narrative');
    let html = '<h2 style="color:#e94560;margin-bottom:15px">叙事类别详细统计</h2>';
    html += '<table><tr><th>类别</th><th>段落数</th><th>占比</th></tr>';
    DATA.narrative_stats.forEach(s=>{
        html += `<tr><td>${s.narrative_category}</td><td>${s.paragraph_count}</td><td>${s.percentage}%</td></tr>`;
    });
    html += '</table>';
    p.innerHTML = html;
}

function renderMonster(){
    const p = document.getElementById('panel-monster');
    let html = '<h2 style="color:#e94560;margin-bottom:15px">怪物类型统计</h2>';
    DATA.monster_type_stats.forEach(s=>{
        const w = s.paragraph_count * 2;
        html += `<div class="chart-row"><div class="chart-label">${s.monster_type}</div><div style="flex:1"><div class="chart-bar" style="width:${w}px"></div></div><div class="chart-value">${s.paragraph_count}</div></div>`;
    });
    p.innerHTML = html;
}

function renderThemes(){
    const p = document.getElementById('panel-themes');
    let html = '<h2 style="color:#e94560;margin-bottom:15px">叙事主题频次</h2>';
    html += '<table><tr><th>主题</th><th>出现次数</th></tr>';
    DATA.theme_frequency.slice(0,30).forEach(t=>{
        html += `<tr><td>${t.theme_name}</td><td>${t.frequency}</td></tr>`;
    });
    html += '</table>';
    p.innerHTML = html;
}

function renderShengui(){
    const p = document.getElementById('panel-shengui');
    let html = '<h2 style="color:#e94560;margin-bottom:15px">神怪段落明细</h2>';
    html += '<input class="search-box" id="sg-search" placeholder="搜索卷名、类型、关键词...">';
    html += '<div id="sg-list">';
    DATA.shengui.forEach(s=>{
        html += `<div class="sg-item" style="margin:8px 0;padding:10px;background:#16213e;border-radius:6px;border-left:3px solid #e94560">
            <div><strong>${s.pid}</strong> · ${s.volume_title} <span class="badge badge-mt">${s.monster_type}</span> ${s.narrative_themes.split('、').map(t=>'<span class="shengui-tag">'+t+'</span>').join('')}</div>
            <div style="font-size:13px;color:#a0a0c0;margin-top:4px">${s.brief}</div>
        </div>`;
    });
    html += '</div>';
    p.innerHTML = html;
    document.getElementById('sg-search').addEventListener('input',function(){
        const q = this.value.toLowerCase();
        document.querySelectorAll('.sg-item').forEach(el=>{
            el.style.display = el.textContent.toLowerCase().includes(q)?'block':'none';
        });
    });
}

function renderSearch(){
    const p = document.getElementById('panel-search');
    let html = '<h2 style="color:#e94560;margin-bottom:15px">段落全文检索</h2>';
    html += '<input class="search-box" id="full-search" placeholder="输入关键词搜索...">';
    html += '<div id="search-results" style="margin-top:10px"></div>';
    p.innerHTML = html;
    document.getElementById('full-search').addEventListener('input',function(){
        const q = this.value.toLowerCase();
        if(q.length<2){document.getElementById('search-results').innerHTML='';return;}
        const results = DATA.paragraphs.filter(p=>p.text.toLowerCase().includes(q)).slice(0,50);
        let rh = `<p style="color:#a0a0c0">找到 ${results.length>50?'50+':results.length} 条结果</p>`;
        rh += '<table><tr><th>ID</th><th>卷</th><th>类别</th><th>神怪</th><th>内容</th></tr>';
        results.forEach(r=>{
            rh += `<tr><td>${r.pid}</td><td>${r.volume_short}</td><td><span class="badge badge-cat">${r.narrative_category}</span></td><td>${r.has_supernatural?'<span class="badge badge-sg">神怪</span>':''}</td><td style="max-width:500px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${r.text.substring(0,80)}</td></tr>`;
        });
        rh += '</table>';
        document.getElementById('search-results').innerHTML = rh;
    });
}

renderOverview(); renderVolumes(); renderNarrative(); renderMonster(); renderThemes(); renderShengui(); renderSearch();

document.querySelectorAll('.tab').forEach(tab=>{
    tab.addEventListener('click',function(){
        document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
        document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
        this.classList.add('active');
        document.getElementById('panel-'+this.dataset.tab).classList.add('active');
    });
});
</script>
</body></html>"""


def main():
    print("=" * 60)
    print("酉阳杂俎 三校版 数据库构建 + 可视化")
    print("=" * 60)
    
    conn, vols = build_db()
    
    print("\n构建JSON数据...")
    data = build_json_data(conn, vols)
    json_str = json.dumps(data, ensure_ascii=False, separators=(',',':'))
    
    print(f"  段落数: {len(data['paragraphs'])}")
    print(f"  神怪数: {len(data['shengui'])}")
    
    # Generate HTML
    html = HTML_TEMPLATE.replace('__JSON_DATA__', json_str)
    html_path = BASE_DIR / "youyang_zazu_viz.html"
    html_path.write_text(html, encoding='utf-8')
    print(f"\n可视化页面: {html_path}")
    print(f"数据库: {DB_PATH}")
    
    # Start server
    print(f"\n启动HTTP服务器: http://localhost:{PORT}/")
    
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/' or self.path == '/index.html':
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
            else:
                self.send_error(404)
        def log_message(self, format, *args):
            pass
    
    httpd = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f"打开浏览器访问: http://localhost:{PORT}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
    finally:
        conn.close()


if __name__ == '__main__':
    main()
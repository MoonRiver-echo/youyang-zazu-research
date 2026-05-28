#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出纯静态 HTML 文件，用于 GitHub Pages 部署。
无需 Python 服务器，直接在浏览器中打开即可。
"""
import csv, json
from pathlib import Path

DATA_DIR = Path(r"C:\Users\lx\Desktop\前期准备\GLM处理")
OUTPUT_DIR = Path(r"C:\Users\lx\Desktop\前期准备\GLM处理\docs")
OUTPUT_DIR.mkdir(exist_ok=True)

def load_csv(fn):
    rows = []
    with open(DATA_DIR / fn, encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            rows.append(dict(r))
    return rows

print("正在加载数据...")
narrative_detail = load_csv("叙事分类明细.csv")
narrative_stats = load_csv("叙事分类统计.csv")
theme_detail = load_csv("主题分类明细.csv")
theme_stats = load_csv("主题分类统计.csv")
theme_frequency = load_csv("主题频次统计.csv")
duplicate_themes = load_csv("重复主题分类.csv")

with open(DATA_DIR / "web_extra_data.json", encoding='utf-8') as f:
    extra_data = json.load(f)

EMBED_DATA = json.dumps({
    "narrative_detail": narrative_detail,
    "narrative_stats": narrative_stats,
    "theme_detail": theme_detail,
    "theme_stats": theme_stats,
    "theme_frequency": theme_frequency,
    "duplicate_themes": duplicate_themes,
}, ensure_ascii=False, separators=(',',':'))

EXTRA_DATA = json.dumps(extra_data, ensure_ascii=False, separators=(',',':'))

NAR_COLORS = json.dumps({
    '动植物谱录':'#b5c4b1','异闻志怪':'#c9b8a8','人物轶事':'#a8b5c8','知识考辨':'#d4c4b8',
    '神仙方术':'#b8a9c4','佛道异闻':'#c4d4b0','器艺技法':'#d4b8b8','异境异域':'#b8c4d4',
    '征兆占验':'#e0c8a8','饮食医药':'#d4d4b0','礼俗制度':'#b8c4b8','器物名物':'#d4b8d4',
    '冥界报应':'#a8b8c0','天文地理':'#c8c8c8'
}, ensure_ascii=False)

THEME_COLORS = json.dumps({
    '人物政事':'#c9b8a8','动物':'#b5c4b1','神怪妖魅':'#b8a9c4','植物':'#c4d4b0',
    '器物技艺':'#d4b8b8','建筑寺塔':'#b8c4d4','异域物产':'#d4c4b8','饮食医药':'#d4d4b0',
    '异人方术':'#e0c8a8','梦兆占验':'#a8b5c8','丧葬冥界':'#a8b8c0','佛道信仰':'#ccc0d8',
    '天文地理':'#c8c8c8','礼俗制度':'#b8c4b8'
}, ensure_ascii=False)

NAR_DEFS = json.dumps({
    '动植物谱录':'描述动植物、矿物等自然物的分类谱录','异闻志怪':'含鬼神妖怪、异变怪异、因果报应的叙事故事',
    '人物轶事':'记载帝王将相、名人的轶事趣闻','知识考辨':'杂录典籍引述、文字考证、实用知识',
    '神仙方术':'描述方术、道法、幻术等术数技艺','佛道异闻':'引述佛道经典、宗教义理、修行体系的异闻',
    '器艺技法':'记载手工技艺、奇术表演、纹身等','异境异域':'描述外国异邦风土人情',
    '征兆占验':'涉及梦境、占卜、预言、祥瑞灾异','饮食医药':'涉及食物、烹饪、饮馔、药理医术',
    '礼俗制度':'记载礼仪、官制、婚俗、丧制等制度','器物名物':'涉及珍奇器物、宝物名称考辨',
    '冥界报应':'涉及冥界、阴司、因果报应','天文地理':'涉及天象、地理、自然奇观'
}, ensure_ascii=False)

# Read the HTML template from web_app.py
print("正在读取 HTML 模板...")
import re
with open(DATA_DIR / "web_app.py", encoding='utf-8') as f:
    content = f.read()

# Extract the HTML template between """ marks
match = re.search(r'HTML\s*=\s*r"""(.*?)"""', content, re.DOTALL)
if not match:
    match = re.search(r"HTML\s*=\s*'''\s*(.*?)\s*'''", content, re.DOTALL)
if not match:
    print("ERROR: Could not find HTML template in web_app.py")
    exit(1)

html_template = match.group(1)
print(f"HTML 模板长度: {len(html_template)}")

# Replace placeholders
html = (html_template
    .replace('__EMBED_DATA__', EMBED_DATA)
    .replace('__EXTRA_DATA__', EXTRA_DATA)
    .replace('__NAR_COLORS__', NAR_COLORS)
    .replace('__THEME_COLORS__', THEME_COLORS)
    .replace('__NAR_DEFS__', NAR_DEFS))

output_file = OUTPUT_DIR / "index.html"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"已生成静态网页: {output_file}")
print(f"文件大小: {output_file.stat().st_size / 1024 / 1024:.1f} MB")
print(f"\nGitHub Pages 部署步骤:")
print(f"  1. 将 docs/ 目录推送到 GitHub 仓库")
print(f"  2. 在仓库 Settings → Pages 中选择分支 + /docs 目录")
print(f"  3. 访问 https://<username>.github.io/<repo>/")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《酉阳杂俎》数据可视化 — 全量数据嵌入版 v2
所有数据嵌入HTML，纯客户端渲染，无数据库，无API
端口: 8889

新增:
  - 段落分类总表 Tab: 按描写对象分类浏览所有段落
  - 神鬼妖魔怪 Tab: 神鬼妖魔怪描写对象提取报告
"""
import csv, json, gzip
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

DATA_DIR = Path(r"C:\Users\lx\Desktop\前期准备\GLM处理")

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

# 加载额外数据
with open(DATA_DIR / "web_extra_data.json", encoding='utf-8') as f:
    extra_data = json.load(f)
classification_data = extra_data['classification']
shengui_data = extra_data['shengui']

print(f"  叙事明细: {len(narrative_detail)} 条")
print(f"  主题明细: {len(theme_detail)} 条")
print(f"  分类总表: {len(classification_data)} 大类")
print(f"  神鬼数据: {shengui_data['total_shengui_paragraphs']} 段")

EMBED_DATA = json.dumps({
    "narrative_detail": narrative_detail,
    "narrative_stats": narrative_stats,
    "theme_detail": theme_detail,
    "theme_stats": theme_stats,
    "theme_frequency": theme_frequency,
    "duplicate_themes": duplicate_themes,
}, ensure_ascii=False, separators=(',',':'))

EXTRA_DATA = json.dumps({
    "classification": classification_data,
    "shengui": shengui_data,
}, ensure_ascii=False, separators=(',',':'))

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

print(f"  嵌入数据大小: {len(EMBED_DATA)} 字节")
print(f"  额外数据大小: {len(EXTRA_DATA)} 字节")

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>酉阳杂俎 · 数据可视化</title>
<style>
:root{--bg:#f6f3ee;--card:#fff;--text:#2d2d2d;--muted:#7a7568;--accent:#7a8e6e;--accent2:#c4a882;--border:#e0d8cf;--shadow:0 4px 16px rgba(0,0,0,.06);--radius:10px}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:"Noto Serif SC","Source Han Serif SC","SimSun",serif;background:var(--bg);color:var(--text);line-height:1.7}
.app{max-width:1280px;margin:0 auto;padding:24px 20px}
.hero{text-align:center;padding:36px 20px 24px;border-radius:14px;background:linear-gradient(135deg,#efe8e0 0%,#e8e0f0 50%,#e0e8e4 100%);box-shadow:var(--shadow);margin-bottom:24px}
.hero h1{font-size:2.1em;font-weight:400;letter-spacing:6px;margin-bottom:6px}
.hero p{color:var(--muted);font-size:.95em;letter-spacing:2px}
.tabs{display:flex;gap:5px;justify-content:center;flex-wrap:wrap;margin-bottom:24px;border-bottom:1px solid var(--border);padding-bottom:8px}
.tab{padding:7px 14px;border-radius:6px 6px 0 0;border:1px solid transparent;border-bottom:none;background:transparent;cursor:pointer;font-size:.85em;transition:all .2s;font-family:inherit;color:var(--muted);user-select:none;position:relative}
.tab:hover{color:var(--text);background:var(--card)}
.tab.on{background:var(--card);color:var(--accent);border-color:var(--border);border-bottom:2px solid var(--card);font-weight:600;margin-bottom:-1px}
.section{display:none}.section.on{display:block}
.section-title{color:var(--accent);margin:20px 0 12px;font-weight:400;font-size:1.15em;padding-bottom:6px;border-bottom:2px solid var(--accent2)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:14px;margin:14px 0}
.card{background:var(--card);border-radius:var(--radius);padding:18px;border:1px solid var(--border);cursor:pointer;transition:all .3s}
.card:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(0,0,0,.1)}
.card h3{font-size:1.05em;margin-bottom:4px}
.card .num{font-size:1.9em;color:var(--accent);font-weight:300}
.card .sub{color:var(--muted);font-size:.82em}
.card .hint{margin-top:6px;color:var(--muted);font-size:.78em}
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:14px 0}
.stat{background:var(--card);border-radius:var(--radius);padding:20px;text-align:center;border:1px solid var(--border)}
.stat .val{font-size:2.2em;color:var(--accent);font-weight:300}
.stat .lbl{color:var(--muted);font-size:.85em;margin-top:4px}
.bar-chart{margin:16px 0}
.bar-row{display:flex;align-items:center;margin:5px 0;font-size:.83em}
.bar-label{width:90px;text-align:right;padding-right:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar-track{flex:1;height:24px;background:#f0ece6;border-radius:4px;position:relative;overflow:hidden}
.bar-fill{height:100%;border-radius:4px;min-width:2px;transition:width .8s ease}
.bar-pct{position:absolute;right:6px;top:50%;transform:translateY(-50%);color:#fff;font-size:.72em;text-shadow:0 1px 2px rgba(0,0,0,.3)}
.bar-count{width:52px;text-align:left;padding-left:6px;color:var(--muted);font-size:.8em}
.expand-panel{max-height:0;overflow:hidden;transition:max-height .4s ease}
.expand-panel.open{max-height:8000px}
.para-item{padding:8px 12px;border-bottom:1px solid #f0ece6;font-size:.83em;cursor:pointer;transition:background .2s}
.para-item:hover{background:#f8f5f0}
.para-item .pid{color:var(--accent);font-weight:600;margin-right:6px}
.para-item .vt{color:var(--muted);margin-right:6px;font-size:.78em}
.cat-tag{display:inline-block;padding:1px 7px;border-radius:10px;font-size:.72em;color:#fff;margin:1px 2px;white-space:nowrap}
.search-box{padding:9px 13px;border:1px solid var(--border);border-radius:8px;font-size:.9em;width:100%;max-width:380px;font-family:inherit;margin:10px 0;transition:border-color .3s}
.search-box:focus{outline:none;border-color:var(--accent)}
.filter-row{display:flex;gap:8px;margin:10px 0;flex-wrap:wrap;align-items:center}
.filter-row select,.filter-row button{padding:7px 12px;border:1px solid var(--border);border-radius:8px;font-family:inherit;font-size:.85em;background:var(--card);cursor:pointer;transition:all .2s}
.filter-row button{background:var(--accent);color:#fff;border-color:var(--accent)}
.filter-row button:hover{opacity:.9}
.freq-item{display:flex;align-items:center;padding:8px 12px;border-bottom:1px solid #f0ece6;transition:background .2s;cursor:pointer}
.freq-item:hover{background:#f8f5f0}
.freq-rank{width:32px;color:var(--muted);font-size:.82em;text-align:center}
.freq-name{flex:1;font-size:.88em}
.freq-count{margin-left:6px;color:var(--accent);font-weight:600;font-size:.88em}
.page-row{display:flex;gap:6px;align-items:center;justify-content:center;margin:14px 0}
.page-btn{padding:5px 12px;border:1px solid var(--border);border-radius:6px;background:var(--card);cursor:pointer;font-family:inherit;font-size:.82em;transition:all .2s}
.page-btn:hover:not(:disabled){background:var(--accent);color:#fff;border-color:var(--accent)}
.page-btn:disabled{opacity:.4;cursor:default}
.modal-overlay{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.45);z-index:1000;justify-content:center;align-items:center}
.modal-overlay.show{display:flex}
.modal-box{background:var(--card);border-radius:12px;padding:28px;max-width:820px;width:92%;max-height:82vh;overflow-y:auto;box-shadow:0 8px 40px rgba(0,0,0,.15);position:relative}
.modal-box h3{margin-bottom:10px;color:var(--accent);font-size:1.15em}
.modal-box .meta{color:var(--muted);font-size:.82em;margin-bottom:14px}
.modal-box .full-text{line-height:2;font-size:.92em;white-space:pre-wrap}
.modal-close{position:absolute;top:10px;right:14px;font-size:1.4em;cursor:pointer;color:var(--muted);border:none;background:none;font-family:inherit;line-height:1}
.theme-tree{margin:4px 0;padding-left:14px}
.theme-tree li{margin:2px 0;font-size:.85em}
table.full-table{width:100%;border-collapse:collapse;font-size:.83em}
table.full-table th{background:#e8e2d9;padding:8px 10px;text-align:left;font-weight:600;position:sticky;top:0;z-index:1}
table.full-table td{padding:6px 10px;border-bottom:1px solid #f0ece6;line-height:1.5}
table.full-table tr:hover{background:#f8f5f0}
/* 分类总表专用样式 */
.cls-layout{display:flex;gap:16px;height:calc(100vh - 140px);min-height:500px}
.cls-sidebar{width:220px;overflow-y:auto;border:1px solid var(--border);border-radius:var(--radius);background:var(--card);padding:8px 0;flex-shrink:0}
.cls-broad{padding:6px 12px;cursor:pointer;font-size:.88em;font-weight:600;transition:background .2s;border-bottom:1px solid #f0ece6}
.cls-broad:hover{background:#f0ece6}
.cls-broad.on{background:var(--accent);color:#fff}
.cls-broad .cnt{font-weight:400;font-size:.78em;opacity:.7;margin-left:4px}
.cls-l1{padding:4px 12px 4px 22px;cursor:pointer;font-size:.84em;transition:background .2s;border-bottom:1px solid #f5f0ea}
.cls-l1:hover{background:#f0ece6}
.cls-l1.on{background:var(--accent2);color:#fff}
.cls-l2{padding:3px 12px 3px 34px;cursor:pointer;font-size:.8em;transition:background .2s}
.cls-l2:hover{background:#f0ece6}
.cls-l2.on{font-weight:600;color:var(--accent)}
.cls-content{flex:1;overflow-y:auto;background:var(--card);border-radius:var(--radius);border:1px solid var(--border)}
.cls-header{padding:14px 18px;border-bottom:1px solid var(--border);background:linear-gradient(135deg,#f6f3ee,#efeadf)}
.cls-header h3{font-size:1.05em;color:var(--accent);margin-bottom:2px}
.cls-header .desc{color:var(--muted);font-size:.82em}
.cls-entries{padding:0}
.cls-entry{padding:10px 18px;border-bottom:1px solid #f0ece6;cursor:pointer;transition:background .15s}
.cls-entry:hover{background:#f8f5f0}
.cls-entry .entry-head{display:flex;align-items:center;gap:8px;margin-bottom:3px}
.cls-entry .entry-pid{color:var(--accent);font-weight:600;font-size:.82em}
.cls-entry .entry-vt{color:var(--muted);font-size:.78em}
.cls-entry .entry-nar{font-size:.78em}
.cls-entry .entry-summary{color:#555;font-size:.84em;line-height:1.6;margin-top:2px}
.cls-entry .entry-text{display:none}
/* 神鬼报告专用样式 */
.sg-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:14px 0}
.sg-card{background:var(--card);border-radius:var(--radius);padding:18px;border:1px solid var(--border)}
.sg-card h4{color:var(--accent);margin-bottom:8px;font-size:.95em}
.sg-stat-row{display:flex;justify-content:space-between;padding:4px 0;font-size:.85em;border-bottom:1px dotted #e8e2d9}
.sg-stat-row .label{color:var(--muted)}
.sg-stat-row .value{font-weight:600;color:var(--accent)}
.sg-kw-bar{display:flex;align-items:center;margin:3px 0;font-size:.78em}
.sg-kw-bar .kw{width:50px;text-align:right;padding-right:6px;color:var(--muted)}
.sg-kw-bar .bar{flex:1;height:16px;background:#f0ece6;border-radius:3px;overflow:hidden}
.sg-kw-bar .bar div{height:100%;border-radius:3px;background:var(--accent)}
.sg-kw-bar .cnt{width:30px;padding-left:4px;color:var(--accent);font-size:.78em;font-weight:600}
.sg-table{width:100%;border-collapse:collapse;font-size:.82em}
.sg-table th{background:#e8e2d9;padding:6px 8px;text-align:left;font-weight:600}
.sg-table td{padding:5px 8px;border-bottom:1px solid #f0ece6}
.sg-table tr:hover{background:#f8f5f0}
@media(max-width:768px){.stats-grid{grid-template-columns:repeat(2,1fr)}.cards{grid-template-columns:1fr}.bar-label{width:70px}.cls-layout{flex-direction:column;height:auto}.cls-sidebar{width:100%;max-height:200px}.sg-grid{grid-template-columns:1fr}}
@media(max-width:480px){.stats-grid{grid-template-columns:1fr}.hero h1{font-size:1.5em}.filter-row{flex-direction:column}}
</style>
</head>
<body>
<div class="app">
<div class="hero">
  <h1>酉阳杂俎</h1>
  <p>唐 · 段成式 · 二十卷 · 七百九十四段 · 数据可视化</p>
</div>
<div class="tabs" id="tabs"></div>
<div class="section on" id="sec-overview"></div>
<div class="section" id="sec-narrative"></div>
<div class="section" id="sec-themes"></div>
<div class="section" id="sec-frequency"></div>
<div class="section" id="sec-cross"></div>
<div class="section" id="sec-browse"></div>
<div class="section" id="sec-classification"></div>
<div class="section" id="sec-shengui"></div>
</div>
<div class="modal-overlay" id="modal">
  <div class="modal-box">
    <button class="modal-close" onclick="closeModal()">&times;</button>
    <h3 id="modal-title"></h3>
    <div class="meta" id="modal-meta"></div>
    <div class="full-text" id="modal-body"></div>
  </div>
</div>
<script type="application/json" id="app-data">__EMBED_DATA__</script>
<script type="application/json" id="extra-data">__EXTRA_DATA__</script>
<script type="application/json" id="nar-colors">__NAR_COLORS__</script>
<script type="application/json" id="theme-colors">__THEME_COLORS__</script>
<script type="application/json" id="nar-defs">__NAR_DEFS__</script>
<script>
var D=JSON.parse(document.getElementById('app-data').textContent);
var ED=JSON.parse(document.getElementById('extra-data').textContent);
var NAR_COLORS=JSON.parse(document.getElementById('nar-colors').textContent);
var THEME_COLORS=JSON.parse(document.getElementById('theme-colors').textContent);
var NAR_DEFS=JSON.parse(document.getElementById('nar-defs').textContent);
function esc(s){if(!s)return '';var d=document.createElement('div');d.textContent=s;return d.innerHTML;}
function trunc(s,n){s=s||'';return s.length>n?s.substring(0,n)+'…':s;}
function tag(cat,map){return '<span class="cat-tag" style="background:'+(map[cat]||'#999')+'">'+esc(cat)+'</span>';}
var p2t={},broad2l1={},l1freq={},l1broad={},narMap={},narByCat={};
D.theme_detail.forEach(function(r){if(!p2t[r.paragraph_id])p2t[r.paragraph_id]=[];p2t[r.paragraph_id].push({broad:r.broad_category,l1:r.level1_subject,l2:r.level2_subject});if(!broad2l1[r.broad_category])broad2l1[r.broad_category]=new Set();broad2l1[r.broad_category].add(r.level1_subject);l1broad[r.level1_subject]=r.broad_category;});
D.theme_frequency.forEach(function(r){if(!l1freq[r.level1_subject])l1freq[r.level1_subject]=[];l1freq[r.level1_subject].push({l2:r.level2_subject,count:parseInt(r.appearance_count)});});
D.narrative_detail.forEach(function(r){narMap[r.paragraph_id]=r;if(!narByCat[r.narrative_category])narByCat[r.narrative_category]=[];narByCat[r.narrative_category].push(r);});
var tabNames=['overview','narrative','themes','frequency','cross','browse','classification','shengui'];
var tabLabels=['总览','叙事结构','描写对象','频次排行','交叉分析','全文浏览','分类总表','神鬼妖魔怪'];
var tabsEl=document.getElementById('tabs');
tabLabels.forEach(function(label,i){var d=document.createElement('div');d.className='tab'+(i===0?' on':'');d.dataset.tab=tabNames[i];d.textContent=label;d.addEventListener('click',function(){document.querySelectorAll('.tab').forEach(function(x){x.classList.remove('on');});document.querySelectorAll('.section').forEach(function(x){x.classList.remove('on');});d.classList.add('on');document.getElementById('sec-'+tabNames[i]).classList.add('on');});tabsEl.appendChild(d);});
function openModal(title,meta,body){document.getElementById('modal-title').textContent=title;document.getElementById('modal-meta').textContent=meta;document.getElementById('modal-body').textContent=body||'';document.getElementById('modal').classList.add('show');}
function closeModal(){document.getElementById('modal').classList.remove('show');}
document.getElementById('modal').addEventListener('click',function(e){if(e.target.id==='modal')closeModal();});

/* === Tab 1: 总览 === */
function renderOverview(){var s=document.getElementById('sec-overview');var totalP=D.narrative_detail.length;var narCats=D.narrative_stats.length;var themeCats=D.theme_stats.length;var specCount=new Set(D.theme_frequency.map(function(x){return x.level2_subject;})).size;var h='<div class="stats-grid">';h+='<div class="stat"><div class="val">'+totalP+'</div><div class="lbl">段落总数</div></div>';h+='<div class="stat"><div class="val">'+narCats+'</div><div class="lbl">叙事结构类别</div></div>';h+='<div class="stat"><div class="val">'+themeCats+'</div><div class="lbl">描写对象大类</div></div>';h+='<div class="stat"><div class="val">'+specCount+'</div><div class="lbl">具体描写对象</div></div>';h+='</div>';var narMax=Math.max.apply(null,D.narrative_stats.map(function(x){return parseInt(x.paragraph_count);}));h+='<h2 class="section-title">叙事结构分类分布</h2><div class="bar-chart">';D.narrative_stats.forEach(function(r){var c=parseInt(r.paragraph_count);var pct=(c/narMax*100).toFixed(1);h+='<div class="bar-row"><div class="bar-label">'+esc(r.narrative_category)+'</div>';h+='<div class="bar-track"><div class="bar-fill" style="width:'+pct+'%;background:'+(NAR_COLORS[r.narrative_category]||'#bbb')+'"><span class="bar-pct">'+r.absolute_percentage+'</span></div></div>';h+='<div class="bar-count">'+c+'段</div></div>';});h+='</div>';var thMax=Math.max.apply(null,D.theme_stats.map(function(x){return parseInt(x.paragraph_count);}));h+='<h2 class="section-title">描写对象分类分布</h2><div class="bar-chart">';D.theme_stats.forEach(function(r){var c=parseInt(r.paragraph_count);var pct=(c/thMax*100).toFixed(1);h+='<div class="bar-row"><div class="bar-label">'+esc(r.broad_category)+'</div>';h+='<div class="bar-track"><div class="bar-fill" style="width:'+pct+'%;background:'+(THEME_COLORS[r.broad_category]||'#bbb')+'"><span class="bar-pct">'+r.absolute_percentage+'</span></div></div>';h+='<div class="bar-count">'+c+'段</div></div>';});h+='</div>';s.innerHTML=h;}

/* === Tab 2: 叙事结构 === */
function renderNarrative(){var s=document.getElementById('sec-narrative');var h='<div class="cards">';D.narrative_stats.forEach(function(r){var cat=r.narrative_category;var def=NAR_DEFS[cat]||'';h+='<div class="card" data-cat="'+esc(cat)+'">';h+='<h3>'+tag(cat,NAR_COLORS)+'</h3>';h+='<div class="num">'+esc(r.paragraph_count)+'</div>';h+='<div class="sub">'+esc(r.absolute_percentage)+' — '+esc(def)+'</div>';h+='<div class="hint">点击展开段落列表 ▾</div>';h+='<div class="expand-panel"></div>';h+='</div>';});h+='</div>';s.innerHTML=h;s.querySelectorAll('.card').forEach(function(card){card.addEventListener('click',function(){var panel=card.querySelector('.expand-panel');if(panel.classList.contains('open')){panel.classList.remove('open');return;}var cat=card.dataset.cat;var paras=narByCat[cat]||[];var list='';var show=paras.slice(0,40);show.forEach(function(p){var themes=p2t[p.paragraph_id]||[];var ttags=themes.slice(0,4).map(function(t){return tag(t.broad,THEME_COLORS);}).join('');var extra=themes.length>4?'<span style="color:var(--muted)">+…</span>':'';list+='<div class="para-item" data-pid="'+esc(p.paragraph_id)+'">';list+='<span class="pid">'+esc(p.paragraph_id)+'</span>';list+='<span class="vt">'+esc(p.volume_title)+'</span>';list+=ttags+extra;list+='</div>';});if(paras.length>40)list+='<div style="color:var(--muted);padding:8px">共 '+paras.length+' 段，显示前40段</div>';panel.innerHTML=list;panel.classList.add('open');panel.querySelectorAll('.para-item').forEach(function(pi){pi.addEventListener('click',function(e){e.stopPropagation();var pid=pi.dataset.pid;openModal(pid,narMap[pid]?narMap[pid].volume_title+' | '+narMap[pid].narrative_category:'',narMap[pid]?narMap[pid].text:'');});});});});}

/* === Tab 3: 描写对象 === */
function renderThemes(){var s=document.getElementById('sec-themes');var h='<div class="cards">';D.theme_stats.forEach(function(r){var broad=r.broad_category;var l1s=broad2l1[broad]||new Set();var parts=[];l1s.forEach(function(l1){var items=l1freq[l1]||[];parts.push(l1+'('+items.map(function(i){return i.l2;}).join('、')+')');});var subList=parts.join('；');h+='<div class="card" data-broad="'+esc(broad)+'">';h+='<h3>'+tag(broad,THEME_COLORS)+'</h3>';h+='<div class="num">'+esc(r.paragraph_count)+'</div>';h+='<div class="sub">'+esc(r.absolute_percentage)+'</div>';h+='<div style="margin-top:4px;font-size:.8em;color:var(--muted)">'+esc(trunc(subList,60)||'—')+'</div>';h+='<div class="hint">点击展开子类 ▾</div>';h+='<div class="expand-panel"></div>';h+='</div>';});h+='</div>';s.innerHTML=h;s.querySelectorAll('.card').forEach(function(card){card.addEventListener('click',function(){var panel=card.querySelector('.expand-panel');if(panel.classList.contains('open')){panel.classList.remove('open');return;}var broad=card.dataset.broad;var l1s=broad2l1[broad]||new Set();var h2='<ul class="theme-tree">';l1s.forEach(function(l1){var items=l1freq[l1]||[];h2+='<li><strong>'+esc(l1)+'</strong>：';h2+=items.map(function(i){return esc(i.l2)+' ('+i.count+'次)';}).join('、');h2+='</li>';});h2+='</ul>';panel.innerHTML=h2;panel.classList.add('open');});});}

/* === Tab 4: 频次排行 === */
function renderFrequency(){var s=document.getElementById('sec-frequency');var sorted=D.theme_frequency.slice().sort(function(a,b){return parseInt(b.appearance_count)-parseInt(a.appearance_count);});var maxC=parseInt(sorted[0].appearance_count);var h='<input class="search-box" id="freqSearch" placeholder="搜索描写对象…">';h+='<div id="freqList">';sorted.forEach(function(r,i){var c=parseInt(r.appearance_count);var pct=(c/maxC*100).toFixed(0);h+='<div class="freq-item" data-key="'+esc(r.level1_subject+r.level2_subject).toLowerCase()+'">';h+='<div class="freq-rank">'+(i+1)+'</div>';h+='<div class="freq-name">'+tag(l1broad[r.level1_subject]||'—',THEME_COLORS)+' '+esc(r.level1_subject)+' → <strong>'+esc(r.level2_subject)+'</strong></div>';h+='<div class="bar" style="flex:0 0 120px;height:14px"><div style="width:'+pct+'%;height:100%;background:var(--accent);border-radius:3px"></div></div>';h+='<div class="freq-count">'+c+'</div>';h+='</div>';});h+='</div>';s.innerHTML=h;document.getElementById('freqSearch').addEventListener('input',function(e){var q=e.target.value.toLowerCase();document.querySelectorAll('.freq-item').forEach(function(el){el.style.display=el.dataset.key.includes(q)?'':'none';});});}

/* === Tab 5: 交叉分析 === */
var crossPage=1,crossPS=20;
function renderCross(){var s=document.getElementById('sec-cross');var h='<p style="color:var(--muted);margin-bottom:8px">以下段落同时涉及多个描写对象类别，共 '+D.duplicate_themes.length+' 段。</p>';h+='<input class="search-box" id="crossSearch" placeholder="搜索段落ID或关键词…" style="margin-bottom:10px">';h+='<table class="full-table"><thead><tr><th style="width:80px">段落ID</th><th style="width:130px">卷·篇</th><th style="width:90px">叙事分类</th><th>描写对象</th><th>内容</th></tr></thead>';h+='<tbody id="crossBody"></tbody></table>';h+='<div class="page-row" id="crossPager"></div>';s.innerHTML=h;renderCrossRows();document.getElementById('crossSearch').addEventListener('input',function(e){var q=e.target.value.toLowerCase();document.querySelectorAll('#crossBody tr').forEach(function(tr){tr.style.display=(tr.dataset.search||'').includes(q)?'':'none';});});}
function renderCrossRows(){var start=(crossPage-1)*crossPS;var page=D.duplicate_themes.slice(start,start+crossPS);var tbody=document.getElementById('crossBody');var h='';page.forEach(function(r){var broads=(r.duplicate_broad_categories||'').split('|').map(function(s){return s.trim();}).filter(function(s){return s;});var tags=broads.map(function(b){return tag(b,THEME_COLORS);}).join(' ');var nar=narMap[r.paragraph_id]?narMap[r.paragraph_id].narrative_category:'—';h+='<tr data-search="'+esc((r.paragraph_id+r.duplicate_broad_categories+r.text||'').toLowerCase())+'">';h+='<td style="color:var(--accent);font-weight:600;cursor:pointer" data-pid="'+esc(r.paragraph_id)+'">'+esc(r.paragraph_id)+'</td>';h+='<td>'+esc(r.volume_title)+'</td>';h+='<td>'+tag(nar,NAR_COLORS)+'</td>';h+='<td>'+tags+'</td>';h+='<td style="font-size:.82em;cursor:pointer" data-pidc="'+esc(r.paragraph_id)+'">'+esc(trunc(r.text,50))+'</td>';h+='</tr>';});tbody.innerHTML=h;tbody.querySelectorAll('[data-pid]').forEach(function(td){td.addEventListener('click',function(){var pid=td.dataset.pid;openModal(pid,narMap[pid]?narMap[pid].volume_title+' | '+narMap[pid].narrative_category:'',narMap[pid]?narMap[pid].text:'');});});tbody.querySelectorAll('[data-pidc]').forEach(function(td){td.addEventListener('click',function(){var pid=td.dataset.pidc;openModal(pid,narMap[pid]?narMap[pid].volume_title+' | '+narMap[pid].narrative_category:'',narMap[pid]?narMap[pid].text:'');});});updateCrossPager();}
function updateCrossPager(){var total=D.duplicate_themes.length;var pages=Math.ceil(total/crossPS)||1;var el=document.getElementById('crossPager');if(!el)return;el.innerHTML='<button class="page-btn" onclick="crossGo('+(crossPage-1)+')" '+(crossPage<=1?'disabled':'')+'>上一页</button> <span style="color:var(--muted)">'+crossPage+'/'+pages+'</span> <button class="page-btn" onclick="crossGo('+(crossPage+1)+')" '+(crossPage>=pages?'disabled':'')+'>下一页</button>';}
function crossGo(p){crossPage=p;renderCrossRows();}

/* === Tab 6: 全文浏览 === */
var browsePage=1,bPS=20;var brF={narrative:'',broad:'',search:''};
function renderBrowse(){var s=document.getElementById('sec-browse');var h='<div class="filter-row">';h+='<select id="brNar"><option value="">全部叙事分类</option>';D.narrative_stats.forEach(function(r){h+='<option value="'+esc(r.narrative_category)+'">'+esc(r.narrative_category)+'</option>';});h+='</select>';h+='<select id="brBroad"><option value="">全部描写对象</option>';D.theme_stats.forEach(function(r){h+='<option value="'+esc(r.broad_category)+'">'+esc(r.broad_category)+'</option>';});h+='</select>';h+='<input class="search-box" id="brSearch" placeholder="搜索关键词…" style="margin:0;max-width:280px">';h+='</div>';h+='<div id="browseResults"></div>';h+='<div class="page-row" id="browsePager"></div>';s.innerHTML=h;document.getElementById('brNar').addEventListener('change',function(e){brF.narrative=e.target.value;browsePage=1;browseGo();});document.getElementById('brBroad').addEventListener('change',function(e){brF.broad=e.target.value;browsePage=1;browseGo();});document.getElementById('brSearch').addEventListener('input',function(e){brF.search=e.target.value;browsePage=1;browseGo();});browseGo();}
function browseGo(){var rows=D.narrative_detail;if(brF.narrative) rows=rows.filter(function(r){return r.narrative_category===brF.narrative;});if(brF.broad){var pids=new Set(D.theme_detail.filter(function(t){return t.broad_category===brF.broad;}).map(function(t){return t.paragraph_id;}));rows=rows.filter(function(r){return pids.has(r.paragraph_id);});}if(brF.search){var q=brF.search.toLowerCase();rows=rows.filter(function(r){return (r.text||'').toLowerCase().includes(q)||r.paragraph_id.toLowerCase().includes(q);});}var total=rows.length;var pages=Math.ceil(total/bPS)||1;var start=(browsePage-1)*bPS;var page=rows.slice(start,start+bPS);var h='<p style="color:var(--muted);margin-bottom:6px">共 '+total+' 段，第 '+browsePage+'/'+pages+' 页</p>';h+='<table class="full-table"><thead><tr><th style="width:80px">段落ID</th><th style="width:130px">卷·篇</th><th style="width:90px">叙事分类</th><th>描写对象</th><th>内容</th></tr></thead><tbody>';page.forEach(function(r){var themes=p2t[r.paragraph_id]||[];var ttags=themes.slice(0,4).map(function(t){return tag(t.broad,THEME_COLORS);}).join('');var extra=themes.length>4?'<span style="color:var(--muted)">+…</span>':'';h+='<tr>';h+='<td style="color:var(--accent);font-weight:600;cursor:pointer" data-pidb="'+esc(r.paragraph_id)+'">'+esc(r.paragraph_id)+'</td>';h+='<td>'+esc(r.volume_title)+'</td>';h+='<td>'+tag(r.narrative_category,NAR_COLORS)+'</td>';h+='<td>'+ttags+extra+'</td>';h+='<td style="font-size:.82em;cursor:pointer" data-pidt="'+esc(r.paragraph_id)+'">'+esc(trunc(r.text,70))+'</td>';h+='</tr>';});h+='</tbody></table>';document.getElementById('browseResults').innerHTML=h;document.querySelectorAll('[data-pidb]').forEach(function(td){td.addEventListener('click',function(){var pid=td.dataset.pidb;openModal(pid,narMap[pid]?narMap[pid].volume_title+' | '+narMap[pid].narrative_category:'',narMap[pid]?narMap[pid].text:'');});});document.querySelectorAll('[data-pidt]').forEach(function(td){td.addEventListener('click',function(){var pid=td.dataset.pidt;openModal(pid,narMap[pid]?narMap[pid].volume_title+' | '+narMap[pid].narrative_category:'',narMap[pid]?narMap[pid].text:'');});});var el2=document.getElementById('browsePager');el2.innerHTML='<button class="page-btn" onclick="browsePrev()">上一页</button> <span style="color:var(--muted)">'+browsePage+'/'+pages+'</span> <button class="page-btn" onclick="browseNext()">下一页</button>';}
function browsePrev(){if(browsePage>1){browsePage--;browseGo();}}
function browseNext(){browsePage++;browseGo();}

/* === Tab 7: 分类总表 === */
var clsState={broad:'',l1:'',l2:'',spec:''};
function renderClassification(){
  var s=document.getElementById('sec-classification');
  var cls=ED.classification;
  var broadNames=Object.keys(cls);
  var totalP=D.narrative_detail.length;
  var sg=ED.shengui;
  
  var h='<p style="color:var(--muted);margin-bottom:10px">按描写对象一级类目→二级类目→具体对象浏览所有段落，查看原文与含义概括。</p>';
  h+='<div class="cls-layout">';
  
  // 左侧导航
  h+='<div class="cls-sidebar" id="clsSidebar">';
  broadNames.forEach(function(b){var l1map=cls[b];var bcnt=0;for(var l1 in l1map)for(var l2 in l1map[l1])for(var sp in l1map[l1][l2])bcnt+=l1map[l1][l2][sp].length;
    h+='<div class="cls-broad" data-broad="'+esc(b)+'">'+tag(b,THEME_COLORS)+'<span class="cnt">'+bcnt+'段</span></div>';
    for(var l1 in l1map){var l1cnt=0;for(var l2 in l1map[l1])for(var sp in l1map[l1][l2])l1cnt+=l1map[l1][l2][sp].length;
      h+='<div class="cls-l1" data-broad="'+esc(b)+'" data-l1="'+esc(l1)+'" style="display:none">'+esc(l1)+'<span class="cnt" style="margin-left:4px;font-size:.75em;opacity:.6">'+l1cnt+'</span></div>';
      for(var l2 in l1map[l1]){var l2cnt=l1map[l1][l2].length;
        for(var sp in l1map[l1][l2])l2cnt=l1map[l1][l2][sp].length;
        h+='<div class="cls-l2" data-broad="'+esc(b)+'" data-l1="'+esc(l1)+'" data-l2="'+esc(l2)+'" style="display:none">'+esc(l2)+'</div>';
      }
    }
  });
  h+='</div>';
  
  // 右侧内容
  h+='<div class="cls-content" id="clsContent">';
  h+='<div class="cls-header"><h3>请从左侧选择类目</h3><div class="desc">共 '+broadNames.length+' 个大类，'+totalP+' 段文本</div></div>';
  h+='</div>';
  
  h+='</div>';
  s.innerHTML=h;
  
  // 绑定事件
  s.querySelectorAll('.cls-broad').forEach(function(el){
    el.addEventListener('click',function(){
      var b=el.dataset.broad;
      // 折叠其他大类
      var wasOn=el.classList.contains('on');
      s.querySelectorAll('.cls-broad').forEach(function(x){x.classList.remove('on');});
      s.querySelectorAll('.cls-l1').forEach(function(x){
        if(x.dataset.broad===b && !wasOn){x.style.display='block';}else{x.style.display='none';}
      });
      s.querySelectorAll('.cls-l2').forEach(function(x){x.style.display='none';});
      s.querySelectorAll('.cls-l1').forEach(function(x){x.classList.remove('on');});
      s.querySelectorAll('.cls-l2').forEach(function(x){x.classList.remove('on');});
      if(!wasOn){el.classList.add('on');showClsCategory(b);clsState={broad:b,l1:'',l2:'',spec:''};}
      else{showClsLanding();}
    });
  });
  s.querySelectorAll('.cls-l1').forEach(function(el){
    el.addEventListener('click',function(e){
      e.stopPropagation();
      var b=el.dataset.broad;var l1=el.dataset.l1;
      s.querySelectorAll('.cls-l1').forEach(function(x){x.classList.remove('on');});
      s.querySelectorAll('.cls-l2').forEach(function(x){
        if(x.dataset.broad===b && x.dataset.l1===l1){x.style.display='block';}else{x.style.display='none';}
      });
      s.querySelectorAll('.cls-l2').forEach(function(x){x.classList.remove('on');});
      el.classList.add('on');
      clsState={broad:b,l1:l1,l2:'',spec:''};
      showClsL1(b,l1);
    });
  });
  s.querySelectorAll('.cls-l2').forEach(function(el){
    el.addEventListener('click',function(e){
      e.stopPropagation();
      var b=el.dataset.broad;var l1=el.dataset.l1;var l2=el.dataset.l2;
      s.querySelectorAll('.cls-l2').forEach(function(x){x.classList.remove('on');});
      el.classList.add('on');
      clsState={broad:b,l1:l1,l2:l2,spec:''};
      showClsL2(b,l1,l2);
    });
  });
}

function showClsLanding(){var s=document.getElementById('sec-classification');var c=document.getElementById('clsContent');var cls=ED.classification;var totalP=D.narrative_detail.length;
  c.innerHTML='<div class="cls-header"><h3>段落描写对象分类总表</h3><div class="desc">共 '+Object.keys(cls).length+' 大类，'+totalP+' 段文本</div></div><p style="padding:18px;color:var(--muted)">点击左侧类目浏览段落，或点击下方大类卡片快速跳转。</p>';
}

function showClsCategory(b){var c=document.getElementById('clsContent');var cls=ED.classification;var l1map=cls[b];var cnt=0;for(var l1 in l1map)for(var l2 in l1map[l1])for(var sp in l1map[l1][l2])cnt+=l1map[l1][l2][sp].length;
  var h='<div class="cls-header"><h3>'+tag(b,THEME_COLORS)+' '+esc(b)+'</h3><div class="desc">共 '+cnt+' 段</div></div>';
  h+='<div style="padding:10px 14px">';
  for(var l1 in l1map){var l1cnt=0;for(var l2 in l1map[l1])for(var sp in l1map[l1][l2])l1cnt+=l1map[l1][l2][sp].length;
    h+='<h4 style="margin:8px 0 4px;color:var(--accent)">'+esc(l1)+'（'+l1cnt+'段）</h4>';
    for(var l2 in l1map[l1]){
      for(var sp in l1map[l1][l2]){var entries=l1map[l1][l2][sp];
        h+='<div style="margin:4px 0 2px 8px;font-size:.88em"><strong>'+esc(sp)+'</strong>（'+entries.length+'段）</div>';
        entries.slice(0,10).forEach(function(e){
          h+='<div class="cls-entry" data-pide="'+esc(e.pid)+'"><div class="entry-head"><span class="entry-pid">'+esc(e.pid)+'</span><span class="entry-vt">'+esc(e.vt)+'</span>'+tag(e.nar,NAR_COLORS)+'</div><div class="entry-summary">'+esc(e.summary)+'</div></div>';
        });
        if(entries.length>10)h+='<div style="color:var(--muted);padding:4px 18px;font-size:.82em">…共 '+entries.length+' 段，显示前10段</div>';
      }
    }
  }
  h+='</div>';
  c.innerHTML=h;
  c.querySelectorAll('.cls-entry').forEach(function(el){el.addEventListener('click',function(){var pid=el.dataset.pide;openModal(pid,narMap[pid]?narMap[pid].volume_title+' | '+narMap[pid].narrative_category:'',narMap[pid]?narMap[pid].text:'');});});
}

function showClsL1(b,l1){var c=document.getElementById('clsContent');var cls=ED.classification;var l2map=cls[b][l1];var cnt=0;for(var l2 in l2map)for(var sp in l2map[l2])cnt+=l2map[l2][sp].length;
  var h='<div class="cls-header"><h3>'+tag(b,THEME_COLORS)+' '+esc(b)+' → '+esc(l1)+'</h3><div class="desc">共 '+cnt+' 段</div></div>';
  h+='<div style="padding:10px 14px">';
  for(var l2 in l2map){
    for(var sp in l2map[l2]){var entries=l2map[l2][sp];
      h+='<h4 style="margin:8px 0 4px;color:var(--accent2)">'+esc(sp)+'</h4>';
      entries.slice(0,20).forEach(function(e){
        h+='<div class="cls-entry" data-pide="'+esc(e.pid)+'"><div class="entry-head"><span class="entry-pid">'+esc(e.pid)+'</span><span class="entry-vt">'+esc(e.vt)+'</span>'+tag(e.nar,NAR_COLORS)+'</div><div class="entry-summary">'+esc(e.summary)+'</div></div>';
      });
      if(entries.length>20)h+='<div style="color:var(--muted);padding:4px 18px;font-size:.82em">…共 '+entries.length+' 段，显示前20段</div>';
    }
  }
  h+='</div>';
  c.innerHTML=h;
  c.querySelectorAll('.cls-entry').forEach(function(el){el.addEventListener('click',function(){var pid=el.dataset.pide;openModal(pid,narMap[pid]?narMap[pid].volume_title+' | '+narMap[pid].narrative_category:'',narMap[pid]?narMap[pid].text:'');});});
}

function showClsL2(b,l1,l2){var c=document.getElementById('clsContent');var cls=ED.classification;var l2data=cls[b][l1][l2];
  var cnt=0;for(var sp in l2data)cnt+=l2data[sp].length;
  var h='<div class="cls-header"><h3>'+tag(b,THEME_COLORS)+' '+esc(b)+' → '+esc(l1)+' → '+esc(l2)+'</h3><div class="desc">共 '+cnt+' 段</div></div>';
  h+='<div style="padding:10px 14px">';
  for(var sp in l2data){var entries=l2data[sp];
    h+='<h4 style="margin:8px 0 4px;color:var(--accent2)">'+esc(sp)+'（'+entries.length+'段）</h4>';
    entries.forEach(function(e){
      h+='<div class="cls-entry" data-pide="'+esc(e.pid)+'"><div class="entry-head"><span class="entry-pid">'+esc(e.pid)+'</span><span class="entry-vt">'+esc(e.vt)+'</span>'+tag(e.nar,NAR_COLORS)+'</div><div class="entry-summary">'+esc(e.summary)+'</div></div>';
    });
  }
  h+='</div>';
  c.innerHTML=h;
  c.querySelectorAll('.cls-entry').forEach(function(el){el.addEventListener('click',function(){var pid=el.dataset.pide;openModal(pid,narMap[pid]?narMap[pid].volume_title+' | '+narMap[pid].narrative_category:'',narMap[pid]?narMap[pid].text:'');});});
}

/* === Tab 8: 神鬼妖魔怪 === */
var sgPage=1,sgPS=30;var sgFilter={nar:'',classified:'all',kw:''};
function renderShengui(){
  var s=document.getElementById('sec-shengui');
  var sg=ED.shengui;
  var totalP=D.narrative_detail.length;
  var allP=sg.all_paragraphs;
  var classifiedPids=new Set(sg.classified_pids||[]);
  
  var h='<h2 class="section-title">神鬼妖魔怪 · 全部文段</h2>';
  h+='<p style="color:var(--muted);margin-bottom:10px">基于794段全文分析，使用扩展关键词表（含鬼、仙、精、魅、妖、魔、魂、魄、龙、凤等60+关键词）自动提取。点击任意段落可查看原文。</p>';
  
  // 统计概览
  h+='<div class="stats-grid">';
  h+='<div class="stat"><div class="val">'+sg.total_shengui_paragraphs+'</div><div class="lbl">含超自然段落</div></div>';
  h+='<div class="stat"><div class="val">'+sg.total_sgm_classified+'</div><div class="lbl">已分类为神怪妖魅</div></div>';
  h+='<div class="stat"><div class="val">'+sg.total_uncovered+'</div><div class="lbl">未覆盖超自然段落</div></div>';
  h+='<div class="stat"><div class="val">'+(sg.total_shengui_paragraphs>0?(sg.total_shengui_paragraphs/totalP*100).toFixed(1):0)+'%</div><div class="lbl">占全文比例</div></div>';
  h+='</div>';
  
  // 关键词频次 Top 30 可折叠
  h+='<h2 class="section-title" style="cursor:pointer" id="sgKwToggle">关键词频次排行（Top 30）▾</h2>';
  h+='<div id="sgKwPanel">';
  var maxKw=sg.keyword_frequency[0]?sg.keyword_frequency[0].count:1;
  h+='<div style="columns:2;column-gap:20px;margin-bottom:14px">';
  sg.keyword_frequency.slice(0,30).forEach(function(r){
    var pct=(r.count/maxKw*100).toFixed(0);
    h+='<div class="sg-kw-bar"><span class="kw">'+esc(r.keyword)+'</span><div class="bar"><div style="width:'+pct+'%;background:var(--accent)"></div></div><span class="cnt">'+r.count+'</span></div>';
  });
  h+='</div></div>';
  
  // 叙事分类分布（可折叠）
  h+='<h2 class="section-title" style="cursor:pointer" id="sgNarToggle">按叙事分类分布 ▾</h2>';
  h+='<div id="sgNarPanel">';
  h+='<table class="sg-table"><thead><tr><th>叙事分类</th><th>段落数</th><th>占比</th></tr></thead><tbody>';
  sg.narrative_distribution.forEach(function(r){
    var pct=(r.count/sg.total_shengui_paragraphs*100).toFixed(1);
    h+='<tr><td>'+tag(r.category,NAR_COLORS)+'</td><td>'+r.count+'</td><td>'+pct+'%</td></tr>';
  });
  h+='</tbody></table></div>';
  
  // ===== 全部文段列表 =====
  h+='<h2 class="section-title">全部神鬼妖魔怪文段（'+allP.length+'段）</h2>';
  h+='<div class="filter-row">';
  h+='<select id="sgNarFilter"><option value="">全部叙事分类</option>';
  sg.narrative_distribution.forEach(function(r){h+='<option value="'+esc(r.category)+'">'+esc(r.category)+' ('+r.count+')</option>';});
  h+='</select>';
  h+='<select id="sgClassFilter"><option value="all">全部段落</option><option value="classified">已归入神怪妖魅</option><option value="uncovered">未归入但含关键词</option></select>';
  h+='<input class="search-box" id="sgKwSearch" placeholder="搜索关键词或段落ID…" style="margin:0;max-width:260px">';
  h+='<button id="sgViewFull" style="padding:6px 14px;border-radius:6px;border:1px solid var(--accent);background:var(--accent);color:#fff;cursor:pointer;font-family:inherit;font-size:.85em">显示原文</button>';
  h+='</div>';
  h+='<div id="sgResults"></div>';
  h+='<div class="page-row" id="sgPager"></div>';
  
  s.innerHTML=h;
  
  // 折叠切换
  document.getElementById('sgKwToggle').addEventListener('click',function(){var p=document.getElementById('sgKwPanel');p.style.display=p.style.display==='none'?'block':'none';});
  document.getElementById('sgNarToggle').addEventListener('click',function(){var p=document.getElementById('sgNarPanel');p.style.display=p.style.display==='none'?'block':'none';});
  
  // 筛选事件
  document.getElementById('sgNarFilter').addEventListener('change',function(e){sgFilter.nar=e.target.value;sgPage=1;renderSgList();});
  document.getElementById('sgClassFilter').addEventListener('change',function(e){sgFilter.classified=e.target.value;sgPage=1;renderSgList();});
  document.getElementById('sgKwSearch').addEventListener('input',function(e){sgFilter.kw=e.target.value;sgPage=1;renderSgList();});
  document.getElementById('sgViewFull').addEventListener('click',function(){var el=document.getElementById('sgViewFull');if(el.dataset.mode==='full'){el.dataset.mode='compact';el.textContent='显示原文';}else{el.dataset.mode='full';el.textContent='仅显示概括';}renderSgList();});
  
  renderSgList();
}

function renderSgList(){
  var sg=ED.shengui;
  var allP=sg.all_paragraphs;
  var classifiedPids=new Set(sg.classified_pids||[]);
  var showFull=document.getElementById('sgViewFull')&&document.getElementById('sgViewFull').dataset.mode==='full';
  
  // 筛选
  var rows=allP;
  if(sgFilter.nar) rows=rows.filter(function(r){return r.nar===sgFilter.nar;});
  if(sgFilter.classified==='classified') rows=rows.filter(function(r){return classifiedPids.has(r.pid);});
  else if(sgFilter.classified==='uncovered') rows=rows.filter(function(r){return !classifiedPids.has(r.pid);});
  if(sgFilter.kw){var q=sgFilter.kw.toLowerCase();rows=rows.filter(function(r){return (r.text||'').toLowerCase().includes(q)||r.pid.toLowerCase().includes(q)||r.keywords.join(' ').toLowerCase().includes(q);});}
  
  var total=rows.length;
  var pages=Math.ceil(total/sgPS)||1;
  var start=(sgPage-1)*sgPS;
  var page=rows.slice(start,start+sgPS);
  
  var classifiedTag='<span class="cat-tag" style="background:var(--accent);font-size:.7em">神怪妖魅</span>';
  var uncoveredTag='<span class="cat-tag" style="background:#c97;font-size:.7em">未归入</span>';
  
  var h='<p style="color:var(--muted);margin-bottom:6px">共 '+total+' 段，第 '+sgPage+'/'+pages+' 页</p>';
  
  if(showFull){
    // 原文模式：每段完整展示
    page.forEach(function(r){
      var isClassified=classifiedPids.has(r.pid);
      var kwTags=r.keywords.slice(0,8).map(function(k){return '<span class="cat-tag" style="background:'+(isClassified?'var(--accent2)':'#8a7050')+';font-size:.7em">'+esc(k)+'</span>';}).join(' ');
      var extra=r.keywords.length>8?'<span style="color:var(--muted)">+'+(r.keywords.length-8)+'</span>':'';
      h+='<div style="background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:14px 16px;margin:10px 0;cursor:pointer" data-sgp="'+esc(r.pid)+'">';
      h+='<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:6px">';
      h+='<span style="color:var(--accent);font-weight:600;font-size:.9em">'+esc(r.pid)+'</span>';
      h+='<span style="color:var(--muted);font-size:.82em">'+esc(r.vt)+'</span>';
      h+=tag(r.nar,NAR_COLORS);
      h+=isClassified?classifiedTag:uncoveredTag;
      h+='<span style="color:var(--muted);font-size:.78em">关键词×'+r.keyword_count+'</span>';
      h+=kwTags+extra;
      h+='</div>';
      h+='<div style="font-size:.9em;line-height:1.9;white-space:pre-wrap;max-height:300px;overflow-y:auto">'+esc(r.text)+'</div>';
      h+='</div>';
    });
  } else {
    // 概括模式：表格形式
    h+='<table class="full-table"><thead><tr><th style="width:80px">段落ID</th><th style="width:110px">卷·篇</th><th style="width:80px">叙事分类</th><th style="width:60px">状态</th><th style="width:50px">关键词数</th><th>关键词</th><th>含义概括</th></tr></thead><tbody>';
    page.forEach(function(r){
      var isClassified=classifiedPids.has(r.pid);
      var kwTags=r.keywords.slice(0,6).map(function(k){return '<span class="cat-tag" style="background:'+(isClassified?'var(--accent2)':'#8a7050')+';font-size:.68em">'+esc(k)+'</span>';}).join(' ');
      var extra=r.keywords.length>6?'<span style="color:var(--muted)">+'+(r.keywords.length-6)+'</span>':'';
      h+='<tr style="cursor:pointer" data-sgp="'+esc(r.pid)+'">';
      h+='<td style="color:var(--accent);font-weight:600">'+esc(r.pid)+'</td>';
      h+='<td>'+esc(r.vt)+'</td>';
      h+='<td>'+tag(r.nar,NAR_COLORS)+'</td>';
      h+='<td>'+(isClassified?classifiedTag:uncoveredTag)+'</td>';
      h+='<td>'+r.keyword_count+'</td>';
      h+='<td>'+kwTags+extra+'</td>';
      h+='<td style="font-size:.82em">'+esc(r.summary)+'</td>';
      h+='</tr>';
    });
    h+='</tbody></table>';
  }
  
  document.getElementById('sgResults').innerHTML=h;
  
  // 绑定点击查看原文
  document.querySelectorAll('[data-sgp]').forEach(function(el){
    el.addEventListener('click',function(){
      var pid=el.dataset.sgp;
      var p=narMap[pid];
      if(p) openModal(pid,p.volume_title+' | '+p.narrative_category,p.text);
      else{
        // 从 shengui 数据中找
        var sp=ED.shengui.all_paragraphs.find(function(x){return x.pid===pid;});
        openModal(pid,sp?(sp.vt+' | '+sp.nar):'',sp?sp.text:'');
      }
    });
  });
  
  // 分页
  var pEl=document.getElementById('sgPager');
  if(pEl){
    pEl.innerHTML='<button class="page-btn" onclick="sgPrev()" '+(sgPage<=1?'disabled':'')+'>上一页</button> <span style="color:var(--muted)">'+sgPage+'/'+pages+'</span> <button class="page-btn" onclick="sgNext()" '+(sgPage>=pages?'disabled':'')+'>下一页</button>';
  }
}
function sgPrev(){if(sgPage>1){sgPage--;renderSgList();}}
function sgNext(){sgPage++;renderSgList();}

/* === 初始化 === */
renderOverview();renderNarrative();renderThemes();renderFrequency();renderCross();renderBrowse();renderClassification();renderShengui();
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ('/', '/index.html'):
            html = (HTML
                .replace('__EMBED_DATA__', EMBED_DATA)
                .replace('__EXTRA_DATA__', EXTRA_DATA)
                .replace('__NAR_COLORS__', NAR_COLORS)
                .replace('__THEME_COLORS__', THEME_COLORS)
                .replace('__NAR_DEFS__', NAR_DEFS))
            data = html.encode('utf-8')
            accept = self.headers.get('Accept-Encoding', '')
            if 'gzip' in accept:
                compressed = gzip.compress(data)
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Encoding', 'gzip')
                self.send_header('Content-Length', str(len(compressed)))
                self.end_headers()
                self.wfile.write(compressed)
            else:
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
        else:
            self.send_error(404)

    def log_message(self, fmt, *args):
        pass


def main():
    port = 8889
    print(f'\n{"="*50}')
    print(f'  《酉阳杂俎》数据可视化（全量嵌入版 v2）')
    print(f'  访问 http://localhost:{port}')
    print(f'{"="*50}\n')
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()


if __name__ == '__main__':
    main()
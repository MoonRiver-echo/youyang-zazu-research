#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《酉阳杂俎》三校版 素雅可视化 — 修复版
解决大数据内嵌导致的JS解析失败问题
"""

import csv
import os
import sys
import json
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(r"C:\Users\lx\Desktop\前期准备\清洗数据")
OUTPUT_HTML = BASE_DIR / "酉阳杂俎-三校-素雅可视化.html"

# ============================================================
# 1. 读取所有CSV数据
# ============================================================
def read_csv(name):
    path = BASE_DIR / f"{name}.csv"
    if not path.exists():
        print(f"警告：{path} 不存在")
        return []
    with open(path, 'r', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

print("读取CSV数据...")
narrative_detail = read_csv("叙事分类明细")
narrative_stats = read_csv("叙事分类统计")
subject_stats = read_csv("主题分类统计")
freq_stats = read_csv("主题频次统计")
duplicate_stats = read_csv("重复主题分类")
supernatural_detail = read_csv("超自然力量叙事主题明细")
supernatural_stats = read_csv("超自然力量叙事主题统计")

# 卷统计
def get_vol_short(t):
    if '·' in t: return t.split('·',1)[1]
    return t.replace('续·','')

vol_data = defaultdict(lambda: {'total':0, 'sg':0, 'cat':'', 'paras':[]})
for row in narrative_detail:
    v = row.get('volume_title','')
    vol_data[v]['total'] += 1
    vol_data[v]['cat'] = row.get('narrative_category','')

for row in supernatural_detail:
    v = row.get('volume_title','')
    vol_data[v]['sg'] += 1

vol_list = []
for v, d in sorted(vol_data.items(), key=lambda x: x[0]):
    vol_list.append({
        'volume_title': v,
        'volume_short': get_vol_short(v),
        'narrative_category': d['cat'],
        'total': d['total'],
        'sg': d['sg'],
        'sg_pct': round(d['sg']/d['total']*100,1) if d['total']>0 else 0,
    })

# 统计
total_paras = len(narrative_detail)
total_sg = len(supernatural_detail)
sg_pct = round(total_sg/total_paras*100, 1) if total_paras>0 else 0
narr_cats = len(narrative_stats)
total_subjects = len(subject_stats)
total_themes = len(supernatural_stats)

# 轻量检索数据（只保留前80字）
search_data = []
for row in narrative_detail:
    text = row.get('text','')
    search_data.append({
        'pid': row.get('paragraph_id',''),
        'vol': row.get('volume_title',''),
        'cat': row.get('narrative_category',''),
        'txt': text[:80] + ('……' if len(text)>80 else '')
    })

# 叙事明细前100（轻量）
narr_detail_light = []
for row in narrative_detail[:100]:
    text = row.get('text','')
    narr_detail_light.append({
        'paragraph_id': row.get('paragraph_id',''),
        'volume_title': row.get('volume_title',''),
        'narrative_category': row.get('narrative_category',''),
        'text': text[:80] + ('……' if len(text)>80 else '')
    })

# 超自然明细前500（已经是截断的text字段，CSV中存储的就是text_brief）
sg_detail_light = []
for row in supernatural_detail[:500]:
    sg_detail_light.append({
        'paragraph_id': row.get('paragraph_id',''),
        'volume_title': row.get('volume_title',''),
        'monster_type': row.get('monster_type',''),
        'narrative_themes': row.get('narrative_themes',''),
        'keywords': row.get('keywords',''),
        'text': row.get('text','')  # CSV中已经是截断的text_brief
    })

# 重复分类前200（已经是截断的text字段）
dup_light = []
for row in duplicate_stats[:200]:
    dup_light.append({
        'paragraph_id': row.get('paragraph_id',''),
        'volume_title': row.get('volume_title',''),
        'duplicate_broad_categories': row.get('duplicate_broad_categories',''),
        'duplicate_specific_subjects': row.get('duplicate_specific_subjects',''),
        'text': row.get('text','')
    })

# 序列化
narr_stats_json = json.dumps(narrative_stats, ensure_ascii=False)
subj_stats_json = json.dumps(subject_stats, ensure_ascii=False)
freq_json = json.dumps(freq_stats, ensure_ascii=False)
dup_json = json.dumps(dup_light, ensure_ascii=False)
sg_detail_json = json.dumps(sg_detail_light, ensure_ascii=False)
sg_stats_json = json.dumps(supernatural_stats, ensure_ascii=False)
vol_list_json = json.dumps(vol_list, ensure_ascii=False)
narr_detail_json = json.dumps(narr_detail_light, ensure_ascii=False)
search_json = json.dumps(search_data, ensure_ascii=False)
dup_total = len(duplicate_stats)

# ============================================================
# 2. HTML模板（使用占位符替换）
# ============================================================
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>《酉阳杂俎》三校版 · 数据可视化</title>
<style>
:root {
    --bg-primary: #f5f0e8;
    --bg-card: #ffffff;
    --bg-header: #faf8f3;
    --bg-hover: #f0ebe3;
    --text-primary: #2c2c2c;
    --text-secondary: #5a5a5a;
    --text-muted: #8a8a8a;
    --accent-red: #8b3a3a;
    --accent-blue: #3a5a7a;
    --accent-green: #6b7b5c;
    --accent-brown: #b8926a;
    --accent-purple: #7a6b8a;
    --border: #d4cfc7;
    --border-light: #e8e3db;
    --font-serif: 'Noto Serif SC','Source Han Serif SC','SimSun','STSong',serif;
    --font-sans: 'Noto Sans SC','Microsoft YaHei','PingFang SC',sans-serif;
    --shadow: 0 1px 3px rgba(0,0,0,0.06);
    --shadow-hover: 0 4px 12px rgba(0,0,0,0.08);
}
* { margin:0; padding:0; box-sizing:border-box; }
body {
    font-family: var(--font-sans);
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.7;
    min-height: 100vh;
}
.header {
    background: var(--bg-header);
    border-bottom: 1px solid var(--border);
    padding: 24px 32px;
    text-align: center;
}
.header h1 {
    font-family: var(--font-serif);
    font-size: 26px;
    color: var(--accent-red);
    font-weight: 600;
    letter-spacing: 2px;
}
.header .subtitle {
    font-size: 13px;
    color: var(--text-muted);
    margin-top: 6px;
}
.header .stats-bar {
    display: flex;
    justify-content: center;
    gap: 32px;
    margin-top: 16px;
    flex-wrap: wrap;
}
.header .stats-bar .stat { text-align: center; }
.header .stats-bar .stat .num {
    font-family: var(--font-serif);
    font-size: 24px;
    color: var(--accent-blue);
    font-weight: 600;
}
.header .stats-bar .stat .label {
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 2px;
}
.tabs {
    display: flex;
    background: var(--bg-card);
    border-bottom: 1px solid var(--border);
    overflow-x: auto;
    padding: 0 24px;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: var(--shadow);
}
.tab {
    padding: 12px 20px;
    cursor: pointer;
    color: var(--text-secondary);
    border-bottom: 3px solid transparent;
    white-space: nowrap;
    transition: all .25s ease;
    font-size: 14px;
    font-family: var(--font-serif);
}
.tab:hover {
    color: var(--accent-red);
    background: rgba(139,58,58,0.03);
}
.tab.active {
    color: var(--accent-red);
    border-bottom-color: var(--accent-red);
    font-weight: 600;
}
.content {
    padding: 24px 32px;
    max-width: 1400px;
    margin: 0 auto;
    min-height: 600px;
}
.panel { display: none; }
.panel.active { display: block; animation: fadeIn .3s ease; }
@keyframes fadeIn { from { opacity:0; transform: translateY(6px); } to { opacity:1; } }
.card {
    background: var(--bg-card);
    border-radius: 6px;
    border: 1px solid var(--border-light);
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: var(--shadow);
    transition: box-shadow .2s;
}
.card:hover { box-shadow: var(--shadow-hover); }
.card-title {
    font-family: var(--font-serif);
    font-size: 18px;
    color: var(--accent-red);
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border-light);
    display: flex;
    align-items: center;
    gap: 8px;
}
.card-title .icon { font-size: 20px; }
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 16px;
    margin-bottom: 20px;
}
.stat-card {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: 6px;
    padding: 16px;
    text-align: center;
    transition: all .2s;
}
.stat-card:hover {
    border-color: var(--border);
    transform: translateY(-2px);
}
.stat-card .num {
    font-family: var(--font-serif);
    font-size: 28px;
    color: var(--accent-blue);
    font-weight: 600;
}
.stat-card .label {
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 4px;
}
.table-wrap {
    overflow-x: auto;
    border-radius: 4px;
    border: 1px solid var(--border-light);
}
table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}
th {
    background: var(--bg-header);
    color: var(--text-primary);
    padding: 10px 12px;
    text-align: left;
    font-weight: 600;
    border-bottom: 2px solid var(--border);
    position: sticky;
    top: 0;
    font-family: var(--font-serif);
    font-size: 13px;
    white-space: nowrap;
}
td {
    padding: 8px 12px;
    border-bottom: 1px solid var(--border-light);
    vertical-align: top;
}
tr:hover td { background: var(--bg-hover); }
tr:nth-child(even) td { background: rgba(0,0,0,0.01); }
tr:nth-child(even):hover td { background: var(--bg-hover); }
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: 500;
    white-space: nowrap;
    letter-spacing: 0.5px;
}
.badge-red { background: rgba(139,58,58,0.1); color: var(--accent-red); border: 1px solid rgba(139,58,58,0.2); }
.badge-blue { background: rgba(58,90,122,0.1); color: var(--accent-blue); border: 1px solid rgba(58,90,122,0.2); }
.badge-green { background: rgba(107,123,92,0.1); color: var(--accent-green); border: 1px solid rgba(107,123,92,0.2); }
.badge-brown { background: rgba(184,146,106,0.1); color: var(--accent-brown); border: 1px solid rgba(184,146,106,0.2); }
.badge-purple { background: rgba(122,107,138,0.1); color: var(--accent-purple); border: 1px solid rgba(122,107,138,0.2); }
.badge-gray { background: rgba(0,0,0,0.04); color: var(--text-muted); border: 1px solid var(--border); }
.chart-row {
    display: flex;
    align-items: center;
    margin: 5px 0;
    font-size: 12px;
}
.chart-label {
    width: 110px;
    text-align: right;
    padding-right: 10px;
    color: var(--text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-family: var(--font-serif);
}
.chart-bar-wrap {
    flex: 1;
    height: 20px;
    background: var(--bg-primary);
    border-radius: 3px;
    overflow: hidden;
    position: relative;
}
.chart-bar {
    height: 100%;
    border-radius: 3px;
    transition: width .6s ease;
    position: relative;
}
.chart-value {
    padding-left: 8px;
    color: var(--text-secondary);
    white-space: nowrap;
    font-variant-numeric: tabular-nums;
}
.search-box {
    width: 100%;
    padding: 10px 14px;
    border: 1px solid var(--border);
    border-radius: 4px;
    font-size: 14px;
    background: var(--bg-card);
    color: var(--text-primary);
    transition: border-color .2s;
    font-family: var(--font-sans);
}
.search-box:focus {
    outline: none;
    border-color: var(--accent-blue);
    box-shadow: 0 0 0 3px rgba(58,90,122,0.08);
}
.limit-note {
    font-size: 12px;
    color: var(--text-muted);
    text-align: center;
    padding: 12px;
    font-style: italic;
}
.sg-item {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: 6px;
    padding: 14px;
    margin-bottom: 10px;
    transition: all .2s;
}
.sg-item:hover {
    border-color: var(--border);
    box-shadow: var(--shadow-hover);
}
.sg-header {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 6px;
}
.sg-pid {
    font-family: var(--font-sans);
    font-size: 12px;
    font-weight: 600;
    color: var(--accent-blue);
}
.sg-vol {
    font-size: 12px;
    color: var(--text-muted);
}
.sg-text {
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.8;
}
.two-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}
@media (max-width: 900px) {
    .two-col { grid-template-columns: 1fr; }
    .content { padding: 16px; }
    .tabs { padding: 0 12px; }
    .tab { padding: 10px 14px; font-size: 13px; }
}
.btn {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 4px;
    font-size: 12px;
    cursor: pointer;
    border: 1px solid var(--border);
    background: var(--bg-card);
    color: var(--text-secondary);
    transition: all .2s;
    font-family: var(--font-sans);
}
.btn:hover {
    border-color: var(--accent-blue);
    color: var(--accent-blue);
    background: rgba(58,90,122,0.04);
}
</style>
</head>
<body>

<div class="header">
    <h1>《酉阳杂俎》三校版 · 数据可视化</h1>
    <div class="subtitle">基于关键词规则的自动分类 · 共 __TOTAL_PARAS__ 段 · __NARR_CATS__ 个叙事类别 · __TOTAL_THEMES__ 个超自然叙事主题</div>
    <div class="stats-bar">
        <div class="stat"><div class="num">__TOTAL_PARAS__</div><div class="label">总段落</div></div>
        <div class="stat"><div class="num">__TOTAL_SG__</div><div class="label">超自然段落</div></div>
        <div class="stat"><div class="num">__SG_PCT__%</div><div class="label">占比</div></div>
        <div class="stat"><div class="num">__NARR_CATS__</div><div class="label">叙事类别</div></div>
        <div class="stat"><div class="num">__TOTAL_SUBJECTS__</div><div class="label">描写对象大类</div></div>
        <div class="stat"><div class="num">__VOL_COUNT__</div><div class="label">卷/子篇</div></div>
    </div>
</div>

<div class="tabs">
    <div class="tab active" data-tab="overview">📊 数据总览</div>
    <div class="tab" data-tab="volumes">📚 卷目统计</div>
    <div class="tab" data-tab="narrative">📖 叙事结构</div>
    <div class="tab" data-tab="subjects">🌿 描写对象</div>
    <div class="tab" data-tab="supernatural">🔮 超自然力量</div>
    <div class="tab" data-tab="cross">🔄 交叉分析</div>
    <div class="tab" data-tab="search">🔍 数据检索</div>
</div>

<div class="content">

<div class="panel active" id="panel-overview">
    <div class="two-col">
        <div class="card">
            <div class="card-title"><span class="icon">📊</span>叙事类别分布</div>
            <div id="narrative-chart"></div>
        </div>
        <div class="card">
            <div class="card-title"><span class="icon">🌿</span>描写对象大类分布</div>
            <div id="subject-chart"></div>
        </div>
    </div>
    <div class="card">
        <div class="card-title"><span class="icon">🔮</span>超自然叙事主题分布（Top 15）</div>
        <div id="sg-chart"></div>
    </div>
</div>

<div class="panel" id="panel-volumes">
    <div class="card">
        <div class="card-title"><span class="icon">📚</span>各卷段落统计</div>
        <div class="table-wrap">
            <table id="vol-table">
                <thead><tr><th>卷名</th><th>叙事类别</th><th>总段数</th><th>超自然段数</th><th>超自然占比</th></tr></thead>
                <tbody></tbody>
            </table>
        </div>
    </div>
</div>

<div class="panel" id="panel-narrative">
    <div class="two-col">
        <div class="card">
            <div class="card-title"><span class="icon">📊</span>叙事类别统计</div>
            <div class="table-wrap">
                <table id="narr-stats-table">
                    <thead><tr><th>叙事类别</th><th>段落数</th><th>占比</th></tr></thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
        <div class="card">
            <div class="card-title"><span class="icon">📋</span>叙事分类明细（前100段）</div>
            <div class="table-wrap">
                <table id="narr-detail-table">
                    <thead><tr><th>ID</th><th>卷名</th><th>类别</th><th>内容摘要</th></tr></thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<div class="panel" id="panel-subjects">
    <div class="two-col">
        <div class="card">
            <div class="card-title"><span class="icon">📊</span>描写对象大类统计</div>
            <div class="table-wrap">
                <table id="subj-stats-table">
                    <thead><tr><th>大类</th><th>段落数</th><th>占比</th></tr></thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
        <div class="card">
            <div class="card-title"><span class="icon">📈</span>描写对象细类频次（Top 20）</div>
            <div class="table-wrap">
                <table id="freq-table">
                    <thead><tr><th>大类</th><th>细类</th><th>出现次数</th></tr></thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<div class="panel" id="panel-supernatural">
    <div class="two-col">
        <div class="card">
            <div class="card-title"><span class="icon">📊</span>超自然叙事主题统计</div>
            <div class="table-wrap">
                <table id="sg-stats-table">
                    <thead><tr><th>叙事主题</th><th>描述</th><th>段落数</th><th>占比</th></tr></thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
        <div class="card">
            <div class="card-title"><span class="icon">📋</span>超自然段落明细（前500段）</div>
            <div style="margin-bottom:10px">
                <input type="text" class="search-box" id="sg-filter" placeholder="筛选主题、怪物类型或关键词...">
            </div>
            <div id="sg-list" style="max-height:600px;overflow-y:auto"></div>
        </div>
    </div>
</div>

<div class="panel" id="panel-cross">
    <div class="card">
        <div class="card-title"><span class="icon">🔄</span>多类归属交叉分析（重复主题分类）</div>
        <div style="margin-bottom:10px">
            <input type="text" class="search-box" id="dup-filter" placeholder="筛选卷名或分类组合...">
        </div>
        <div class="table-wrap">
            <table id="dup-table">
                <thead><tr><th>ID</th><th>卷名</th><th>归属大类</th><th>归属细类</th><th>内容摘要</th></tr></thead>
                <tbody></tbody>
            </table>
        </div>
        <div class="limit-note" id="dup-note"></div>
    </div>
</div>

<div class="panel" id="panel-search">
    <div class="card">
        <div class="card-title"><span class="icon">🔍</span>全文段落检索</div>
        <div style="display:flex;gap:10px;margin-bottom:12px;flex-wrap:wrap">
            <input type="text" class="search-box" id="full-search" placeholder="输入关键词搜索全文段落..." style="flex:1">
            <select class="search-box" id="search-cat" style="width:150px">
                <option value="">全部类别</option>
            </select>
            <button class="btn" onclick="exportSearch()">📥 导出结果</button>
        </div>
        <div id="search-results-count" style="font-size:12px;color:var(--text-muted);margin-bottom:8px"></div>
        <div class="table-wrap">
            <table id="search-table">
                <thead><tr><th>ID</th><th>卷名</th><th>类别</th><th>内容（前80字）</th></tr></thead>
                <tbody></tbody>
            </table>
        </div>
        <div class="limit-note" id="search-note"></div>
    </div>
</div>

</div>

<script>
// === 数据（轻量版）===
const NARR_STATS = __NARR_STATS_JSON__;
const SUBJ_STATS = __SUBJ_STATS_JSON__;
const FREQ_STATS = __FREQ_JSON__;
const DUP_STATS = __DUP_JSON__;
const SG_DETAIL = __SG_DETAIL_JSON__;
const SG_STATS = __SG_STATS_JSON__;
const VOL_LIST = __VOL_LIST_JSON__;
const NARR_DETAIL = __NARR_DETAIL_JSON__;
const SEARCH_DATA = __SEARCH_JSON__;
const DUP_TOTAL = __DUP_TOTAL__;

const CHART_COLORS = [
    '#8b3a3a','#3a5a7a','#6b7b5c','#b8926a','#7a6b8a',
    '#8a9a7a','#a87b6b','#6a8a9a','#9a7a5a','#7a8a6b',
    '#8a7a6b','#6b8a7a','#9a8a7a','#7a7a8a','#8a8a7a'
];

// === 错误处理 ===
window.onerror = function(msg, url, line) {
    console.error("JS Error:", msg, "at line", line);
    var errDiv = document.createElement('div');
    errDiv.style.cssText = 'position:fixed;top:10px;right:10px;background:#8b3a3a;color:#fff;padding:10px 16px;border-radius:4px;font-size:12px;z-index:9999;max-width:400px;';
    errDiv.textContent = 'JavaScript错误: ' + msg + ' (行' + line + ')';
    document.body.appendChild(errDiv);
    setTimeout(function(){ errDiv.remove(); }, 5000);
};

// === 图表渲染 ===
function renderBarChart(containerId, data, labelKey, valueKey, maxItems) {
    var container = document.getElementById(containerId);
    if(!container) return;
    maxItems = maxItems || 15;
    var sorted = data.slice().sort(function(a,b) {
        return parseFloat((b[valueKey]||'0').toString().replace('%','')) - parseFloat((a[valueKey]||'0').toString().replace('%',''));
    }).slice(0, maxItems);
    var maxVal = 0;
    sorted.forEach(function(d) {
        var v = parseFloat((d[valueKey]||'0').toString().replace('%',''));
        if(v > maxVal) maxVal = v;
    });
    var html = '';
    sorted.forEach(function(d, i) {
        var val = parseFloat((d[valueKey]||'0').toString().replace('%',''));
        var pct = maxVal > 0 ? (val/maxVal*100).toFixed(1) : 0;
        var color = CHART_COLORS[i % CHART_COLORS.length];
        html += '<div class="chart-row">' +
            '<div class="chart-label">' + d[labelKey] + '</div>' +
            '<div class="chart-bar-wrap"><div class="chart-bar" style="width:' + pct + '%;background:' + color + '"></div></div>' +
            '<div class="chart-value">' + val + '</div>' +
        '</div>';
    });
    container.innerHTML = html;
}

function renderTable(tbodyId, data, columns, limit) {
    limit = limit || 100;
    var tbody = document.querySelector('#' + tbodyId + ' tbody');
    if(!tbody) return;
    var html = '';
    data.slice(0, limit).forEach(function(row) {
        html += '<tr>';
        columns.forEach(function(col) {
            var val = row[col.key] || '';
            if(col.badge) {
                var cls = col.badgeClass ? col.badgeClass(row) : 'badge-gray';
                val = '<span class="badge ' + cls + '">' + val + '</span>';
            }
            html += '<td>' + val + '</td>';
        });
        html += '</tr>';
    });
    tbody.innerHTML = html;
}

function getBadgeClass(cat) {
    var map = {
        '异闻志怪':'badge-red','佛道异闻':'badge-purple','神仙方术':'badge-blue',
        '器物名物':'badge-brown','器艺技法':'badge-green','知识考辨':'badge-gray',
        '佛寺塔庙':'badge-purple','礼俗制度':'badge-brown','广知博物':'badge-green',
        '丧葬礼俗':'badge-red','异境异域':'badge-blue','语资谈助':'badge-gray',
        '饮食医药':'badge-green','帝王纪事':'badge-red','梦兆占验':'badge-purple',
        '天文地理':'badge-blue','侠盗刺客':'badge-red','征兆占验':'badge-brown',
        '事物怪变':'badge-red','器物名物':'badge-brown','幽冥冥迹':'badge-purple',
        '精诚感应':'badge-green','史料序跋':'badge-gray','动植物谱录':'badge-green',
        '未分类':'badge-gray'
    };
    return map[cat] || 'badge-gray';
}

// === 1. 总览 ===
function renderOverview() {
    renderBarChart('narrative-chart', NARR_STATS, 'narrative_category', 'paragraph_count', 20);
    renderBarChart('subject-chart', SUBJ_STATS, 'broad_category', 'paragraph_count', 15);
    renderBarChart('sg-chart', SG_STATS, 'narrative_theme', 'paragraph_count', 15);
}

// === 2. 卷目统计 ===
function renderVolumes() {
    var tbody = document.querySelector('#vol-table tbody');
    var html = '';
    VOL_LIST.forEach(function(v) {
        var badgeCls = getBadgeClass(v.narrative_category);
        var sgCls = v.sg > 0 ? 'badge-red' : 'badge-gray';
        html += '<tr>' +
            '<td><strong>' + v.volume_title + '</strong></td>' +
            '<td><span class="badge ' + badgeCls + '">' + v.narrative_category + '</span></td>' +
            '<td style="text-align:center">' + v.total + '</td>' +
            '<td style="text-align:center"><span class="badge ' + sgCls + '">' + v.sg + '</span></td>' +
            '<td style="text-align:center">' + v.sg_pct + '%</td>' +
        '</tr>';
    });
    tbody.innerHTML = html;
}

// === 3. 叙事结构 ===
function renderNarrative() {
    renderTable('narr-stats-table', NARR_STATS, [
        {key:'narrative_category', badge:true, badgeClass:function(r){return getBadgeClass(r.narrative_category);}},
        {key:'paragraph_count'},
        {key:'absolute_percentage'}
    ]);

    renderTable('narr-detail-table', NARR_DETAIL, [
        {key:'paragraph_id'},
        {key:'volume_title'},
        {key:'narrative_category', badge:true, badgeClass:function(r){return getBadgeClass(r.narrative_category);}},
        {key:'text'}
    ]);
}

// === 4. 描写对象 ===
function renderSubjects() {
    renderTable('subj-stats-table', SUBJ_STATS, [
        {key:'broad_category', badge:true, badgeClass:function(){return 'badge-blue';}},
        {key:'paragraph_count'},
        {key:'absolute_percentage'}
    ]);

    renderTable('freq-table', FREQ_STATS.slice(0,20), [
        {key:'level1_subject', badge:true, badgeClass:function(){return 'badge-blue';}},
        {key:'level2_subject'},
        {key:'appearance_count'}
    ]);
}

// === 5. 超自然力量 ===
function renderSupernatural() {
    renderTable('sg-stats-table', SG_STATS, [
        {key:'narrative_theme', badge:true, badgeClass:function(){return 'badge-purple';}},
        {key:'description'},
        {key:'paragraph_count'},
        {key:'percentage'}
    ]);

    renderSGList(SG_DETAIL);

    document.getElementById('sg-filter').addEventListener('input', function() {
        var q = this.value.toLowerCase();
        var filtered = SG_DETAIL.filter(function(s) {
            return (s.narrative_themes||'').toLowerCase().includes(q) ||
                (s.monster_type||'').toLowerCase().includes(q) ||
                (s.keywords||'').toLowerCase().includes(q) ||
                (s.volume_title||'').toLowerCase().includes(q);
        });
        renderSGList(filtered);
    });
}

function renderSGList(data) {
    var container = document.getElementById('sg-list');
    var html = '';
    data.slice(0,200).forEach(function(s) {
        var themes = (s.narrative_themes||'').split('、').filter(function(t){return t;}).map(function(t){return '<span class="badge badge-purple">' + t + '</span>';}).join(' ');
        var mt = s.monster_type ? '<span class="badge badge-red">' + s.monster_type + '</span>' : '';
        html += '<div class="sg-item">' +
            '<div class="sg-header">' +
                '<span class="sg-pid">' + s.paragraph_id + '</span>' +
                '<span class="sg-vol">' + s.volume_title + '</span>' +
                mt + ' ' + themes +
            '</div>' +
            '<div class="sg-text">' + (s.text || '') + '</div>' +
        '</div>';
    });
    if(data.length > 200) {
        html += '<div class="limit-note">共 ' + data.length + ' 段，仅显示前200段</div>';
    }
    container.innerHTML = html;
}

// === 6. 交叉分析 ===
function renderCross() {
    var tbody = document.querySelector('#dup-table tbody');
    var html = '';
    DUP_STATS.forEach(function(d) {
        var cats = (d.duplicate_broad_categories||'').split('、').map(function(c){return '<span class="badge badge-blue">' + c + '</span>';}).join(' ');
        var subs = (d.duplicate_specific_subjects||'').split('、').map(function(s){return '<span class="badge badge-brown">' + s + '</span>';}).join(' ');
        html += '<tr>' +
            '<td>' + d.paragraph_id + '</td>' +
            '<td>' + d.volume_title + '</td>' +
            '<td>' + cats + '</td>' +
            '<td>' + subs + '</td>' +
            '<td>' + (d.text || '') + '</td>' +
        '</tr>';
    });
    tbody.innerHTML = html;

    document.getElementById('dup-filter').addEventListener('input', function() {
        var q = this.value.toLowerCase();
        var rows = document.querySelectorAll('#dup-table tbody tr');
        rows.forEach(function(row) {
            row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
        });
    });

    document.getElementById('dup-note').textContent = '显示前' + DUP_STATS.length + '条（共' + DUP_TOTAL + '条），完整数据请查看重复主题分类.csv';
}

// === 7. 数据检索 ===
function renderSearch() {
    var catSelect = document.getElementById('search-cat');
    var cats = NARR_STATS.map(function(s){return s.narrative_category;}).filter(function(v,i,a){return a.indexOf(v)===i;}).sort();
    cats.forEach(function(c) {
        var opt = document.createElement('option');
        opt.value = c; opt.textContent = c;
        catSelect.appendChild(opt);
    });

    function doSearch() {
        var q = document.getElementById('full-search').value.toLowerCase().trim();
        var cat = document.getElementById('search-cat').value;
        if(q.length < 1 && !cat) {
            document.getElementById('search-results-count').textContent = '';
            document.querySelector('#search-table tbody').innerHTML = '';
            document.getElementById('search-note').textContent = '';
            return;
        }
        var filtered = SEARCH_DATA;
        if(cat) filtered = filtered.filter(function(p){ return p.cat === cat; });
        if(q.length >= 1) filtered = filtered.filter(function(p){ return (p.txt||'').toLowerCase().includes(q); });
        var count = filtered.length;
        var show = filtered.slice(0, 100);

        var tbody = document.querySelector('#search-table tbody');
        var html = '';
        show.forEach(function(p) {
            var badgeCls = getBadgeClass(p.cat);
            html += '<tr>' +
                '<td>' + p.pid + '</td>' +
                '<td>' + p.vol + '</td>' +
                '<td><span class="badge ' + badgeCls + '">' + p.cat + '</span></td>' +
                '<td>' + p.txt + '</td>' +
            '</tr>';
        });
        tbody.innerHTML = html;

        document.getElementById('search-results-count').textContent = '找到 ' + count + ' 条结果' + (count>100 ? '，显示前100条' : '');
        document.getElementById('search-note').textContent = count > 100 ? '更多结果请使用更精确的关键词或类别筛选' : '';
    }

    document.getElementById('full-search').addEventListener('input', doSearch);
    document.getElementById('search-cat').addEventListener('change', doSearch);

    window.exportSearch = function() {
        var q = document.getElementById('full-search').value.toLowerCase().trim();
        var cat = document.getElementById('search-cat').value;
        var filtered = SEARCH_DATA;
        if(cat) filtered = filtered.filter(function(p){ return p.cat === cat; });
        if(q.length >= 1) filtered = filtered.filter(function(p){ return (p.txt||'').toLowerCase().includes(q); });
        if(filtered.length === 0) { alert('无结果可导出'); return; }

        var csv = 'paragraph_id,volume_title,narrative_category,text\\n';
        filtered.forEach(function(p) {
            var text = (p.txt||'').replace(/"/g,'""').replace(/\\n/g,' ');
            csv += '"' + p.pid + '","' + p.vol + '","' + p.cat + '","' + text + '"\\n';
        });

        var blob = new Blob(["\\uFEFF"+csv], {type:'text/csv;charset=utf-8;'});
        var link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = '检索结果.csv';
        link.click();
    };
}

// === Tab切换 ===
document.querySelectorAll('.tab').forEach(function(tab) {
    tab.addEventListener('click', function() {
        document.querySelectorAll('.tab').forEach(function(t){t.classList.remove('active');});
        document.querySelectorAll('.panel').forEach(function(p){p.classList.remove('active');});
        this.classList.add('active');
        document.getElementById('panel-'+this.dataset.tab).classList.add('active');
    });
});

// === 初始化 ===
renderOverview();
renderVolumes();
renderNarrative();
renderSubjects();
renderSupernatural();
renderCross();
renderSearch();
</script>

</body>
</html>
'''

# 替换占位符
html = HTML_TEMPLATE
html = html.replace('__TOTAL_PARAS__', str(total_paras))
html = html.replace('__TOTAL_SG__', str(total_sg))
html = html.replace('__SG_PCT__', str(sg_pct))
html = html.replace('__NARR_CATS__', str(narr_cats))
html = html.replace('__TOTAL_SUBJECTS__', str(total_subjects))
html = html.replace('__TOTAL_THEMES__', str(total_themes))
html = html.replace('__VOL_COUNT__', str(len(vol_list)))
html = html.replace('__NARR_STATS_JSON__', narr_stats_json)
html = html.replace('__SUBJ_STATS_JSON__', subj_stats_json)
html = html.replace('__FREQ_JSON__', freq_json)
html = html.replace('__DUP_JSON__', dup_json)
html = html.replace('__SG_DETAIL_JSON__', sg_detail_json)
html = html.replace('__SG_STATS_JSON__', sg_stats_json)
html = html.replace('__VOL_LIST_JSON__', vol_list_json)
html = html.replace('__NARR_DETAIL_JSON__', narr_detail_json)
html = html.replace('__SEARCH_JSON__', search_json)
html = html.replace('__DUP_TOTAL__', str(dup_total))

with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
    f.write(html)

size_kb = OUTPUT_HTML.stat().st_size / 1024
print(f"✓ 生成完成: {OUTPUT_HTML}")
print(f"  文件大小: {size_kb:.1f} KB")
print(f"  修复内容: 移除完整文本内嵌，改用轻量检索数据，避免JS解析失败")

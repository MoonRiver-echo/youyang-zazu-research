#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
酉阳杂俎 - Web Visualization（离线本地版）
使用 Python 标准库实现，不依赖外部包
提供静态 API 端点和一个单页应用界面
"""
import json
import sqlite3
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path

BASE_DB = Path(r"C:\Users\lx\Desktop\前期准备\GLM处理\youyang_zazu.db")


def db_connection():
    conn = sqlite3.connect(str(BASE_DB))
    conn.row_factory = sqlite3.Row
    return conn


HTML_TEMPLATE = """
<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>酉阳杂俎 - 可视化仪表板</title>
  <style>
  :root{
    --bg: #f6f3ee;
    --card: #ffffff;
    --text: #2b2b2b;
    --muted: #6b6760;
    --morandi-1:#f0e9e0;
    --morandi-2:#e8e2d9;
    --morandi-3:#d7d2ca;
    --morandi-4:#bdb6ab;
    --morandi-5:#9a9288;
    --shadow: 0 6px 18px rgba(0,0,0,.08);
  }
  *{box-sizing:border-box}
  html,body{margin:0;height:100%}
  body{font-family:"Noto Serif SC","Source Han Serif SC","SimSun", serif;background:var(--bg);color:var(--text);}
  .app{max-width:1100px;margin:0 auto;padding:20px}
  .hero{text-align:center;padding:28px 20px;border-radius:14px;background:linear-gradient(135deg,#efe8e0,#efe9f0);box-shadow:var(--shadow);margin:16px 0 28px}
  .hero h1{margin:0;font-size:28px}
  .hero p{color:var(--muted);margin:6px 0 0}
  .tabs{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:6px 0 14px}
  .tab{padding:10px 14px;border-radius:999px;border:1px solid #e0d8cf;background:#fff;cursor:pointer}
  .tab.active{background:#e9e1d7}
  .content{display:none;padding:6px 0}
  .content.active{display:block}
  .section{margin:18px 0}
  .grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
  .card{background:#fff;border:1px solid #e5ded5;border-radius:10px;padding:12px;min-height:90px;box-shadow:var(--shadow)}
  .card h3{font-size:13px;margin:0 0 6px;color:#555}
  .card .val{font-size:18px;font-weight:700}
  .bar{height:14px;background:#ddd;border-radius:7px;overflow:hidden;position:relative}
  .bar > span{display:block;height:100%;background:linear-gradient(90deg,#a5b2a0,#6b8a80)}
  .panel{background:#fff;border:1px solid #e2ddd6;border-radius:8px;padding:10px}
  .tag{display:inline-block;padding:6px 8px;border-radius:999px;background:#f1efe9;color:#606056;font-size:11px}
  .table{width:100%;border-collapse:collapse;font-size:12px}
  .table th,.table td{border-bottom:1px solid #eee;padding:6px 8px;text-align:left}
  @media (max-width: 960px){.grid{grid-template-columns:repeat(2,1fr)}}
  @media (max-width: 600px){.grid{grid-template-columns:1fr}} 
  </style>
</head>
<body>
  <div class="app">
    <div class="hero">
      <h1>《酉阳杂俎》 · 唐 · 段成式</h1>
      <p>离线本地可视化仪表板，数据来自本地 SQLite 数据库。</p>
    </div>
    <div class="tabs" id="tabs">
      <button class="tab active" data-tab="overview">总览</button>
      <button class="tab" data-tab="narrative">叙事结构</button>
      <button class="tab" data-tab="themes">描写对象</button>
      <button class="tab" data-tab="frequency">频次分析</button>
      <button class="tab" data-tab="cross">交叉分析</button>
      <button class="tab" data-tab="browse">浏览</button>
    </div>

    <div class="content active" id="overview">
      <div class="section grid" id="stat-cards"></div>
      <div class="section" style="display:flex;gap:16px;flex-wrap:wrap;">
        <div class="panel" style="flex:1;min-width:320px;">
          <div class="section"><h2>叙事分类比例</h2><div id="narrative-bars"></div></div>
        </div>
        <div class="panel" style="flex:1;min-width:320px;">
          <div class="section"><h2>主题分类比例</h2><div id="theme-bars"></div></div>
        </div>
      </div>
    </div>

    <div class="content" id="narrative">
      <div class="section" id="narrative-cards"></div>
      <div class="panel hidden" id="narrative-para-list" style="margin-top:12px;">
        <h3>段落列表</h3>
        <table class="table" id="narrative-para-table"><thead><tr><th>段落ID</th><th>卷名称</th><th>文本摘录</th></tr></thead><tbody></tbody></table>
      </div>
    </div>

    <div class="content" id="themes">
      <div class="section" id="theme-section">
        <div class="grid" id="theme-cards"></div>
      </div>
      <div class="panel hidden" id="theme-detail-panel" style="margin-top:12px;">
        <h3>子类分布（level1_subject → level2_subject）</h3>
        <div id="theme-sub-distribution" class="grid" style="grid-template-columns: repeat(3, 1fr);"></div>
      </div>
    </div>

    <div class="content" id="frequency">
      <div class="section">
        <input id="freq-search" class="input" placeholder="搜索：输入 level1_subject 或 level2_subject" style="width: 320px;"/>
        <div id="frequency-list" class="panel" style="margin-top:8px;"></div>
      </div>
    </div>

    <div class="content" id="cross">
      <div class="section">
        <table class="table" id="cross-table"><thead><tr><th>段落ID</th><th>重复主题</th><th>文本摘录</th></tr></thead><tbody></tbody></table>
      </div>
    </div>

    <div class="content" id="browse">
      <div class="section">
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
          <select id="browse-narrative" class="select"></select>
          <select id="browse-broad" class="select"></select>
          <input id="browse-key" class="input" placeholder="关键词检索文本"/>
          <button class="button" id="browse-search">搜索</button>
        </div>
        <div id="browse-results" style="margin-top:12px;">
          <table class="table" id="browse-table"><thead><tr><th>段落ID</th><th>卷标题</th><th>叙事分类</th><th>主题</th><th>文本摘录</th></tr></thead><tbody></tbody></table>
        </div>
      </div>
    </div>
  </div>

  <script>
    const apiBase = "/api";
    const el = (s)=>document.querySelector(s);
    const elAll = (s)=>document.querySelectorAll(s);

    function setActiveTab(name){
      for(const b of elAll('.tab')) b.classList.toggle('active', b.dataset.tab===name);
      for(const c of elAll('.content')) c.classList.toggle('active', c.id===name);
    }
    document.addEventListener('DOMContentLoaded', async ()=>{
      for(const b of elAll('.tab')) b.addEventListener('click', ()=> setActiveTab(b.dataset.tab));
      await loadOverview();
      await loadNarrativeTabs();
      await loadThemeTabs();
      await loadFrequency();
      await loadBrowseOptions();
    });

    async function fetchJson(url){
      const r = await fetch(url);
      if(!r.ok) throw new Error('请求失败: ' + url);
      return r.json();
    }

    async function loadOverview(){
      // 统计卡与柱状图数据
      const narrativeStats = await fetchJson(apiBase + '/narrative_stats');
      const themeStats = await fetchJson(apiBase + '/theme_stats');
      // 计算占比条目数（为演示，直接使用统计表中的条目数及文本字段）
      const ndTotal = (await fetchJson(apiBase + '/narrative_detail_count')).total || 0;
      const statCards = el('#stat-cards');
      statCards.innerHTML = '';
      const items = [
        {title:'794段', value: ndTotal},
        {title:'14叙事类', value: narrativeStats.length},
        {title:'14主题类', value: themeStats.length},
        {title:'176具体对象', value: (themeStats.length>0? (await fetchJson(apiBase+'/theme_detail_counts')).unique_specific_subjects || 0 : 0)}
      ];
      items.forEach(it=>{
        const card = document.createElement('div'); card.className='card';
        card.innerHTML = `<h3>${it.title}</h3><div class="val">${it.value}</div>`;
        statCards.appendChild(card);
      });

      // Narrative bar chart
      const narrativeBars = el('#narrative-bars'); narrativeBars.innerHTML='';
      narrativeStats.forEach((row)=>{
        const rowEl = document.createElement('div'); rowEl.style.display='flex'; rowEl.style.alignItems='center'; rowEl.style.gap='8px'; rowEl.style.padding='6px 0';
        const label = document.createElement('div'); label.style.width='180px'; label.style.fontSize='12px'; label.style.color='#555'; label.textContent = row.narrative_category;
        const barWrap = document.createElement('div'); barWrap.className='bar'; barWrap.style.flex='1'; const span = document.createElement('span'); span.style.width = (parseFloat(row.absolute_percentage) || 0) + '%'; barWrap.appendChild(span);
        rowEl.appendChild(label); rowEl.appendChild(barWrap);
        narrativeBars.appendChild(rowEl);
      });

      // Theme bar chart
      const themeBars = el('#theme-bars'); themeBars.innerHTML='';
      themeStats.forEach((row)=>{
        const rowEl = document.createElement('div'); rowEl.style.display='flex'; rowEl.style.alignItems='center'; rowEl.style.gap='8px'; rowEl.style.padding='6px 0';
        const label = document.createElement('div'); label.style.width='180px'; label.style.fontSize='12px'; label.style.color='#555'; label.textContent = row.broad_category;
        const barWrap = document.createElement('div'); barWrap.className='bar'; barWrap.style.flex='1'; const span = document.createElement('span'); span.style.width = (parseFloat(row.absolute_percentage) || 0) + '%'; barWrap.appendChild(span);
        rowEl.appendChild(label); rowEl.appendChild(barWrap);
        themeBars.appendChild(rowEl);
      });
    }

    async function loadNarrativeTabs(){
      const cards = el('#narrative-cards'); cards.innerHTML = '';
      try {
        const stats = await fetchJson(apiBase + '/narrative_stats');
        const definitions = {
          '动植物谱录':'记录动植物相关现象与自然观察',
          '异常闻志怪':'机读示例（本实现以示例为主）',
          '异闻志怪':'传闻、怪异故事及相关记载',
          '人物轶事':'人物相关的趣闻与事迹',
          '知识考辨':'考据与辨析',
          '神仙方术':'神仙与方术相关记载',
          '佛道异闻':'佛道宗教相关异闻',
          '器艺技法':'工艺技法与器物制造',
          '异境异域':'异境与异域地理',
          '征兆占验':'征兆与占验',
          '饮食医药':'饮食与药物知识',
          '礼俗制度':'礼仪、风俗、制度',
          '器物名物':'器物与名物',
          '冥界报应':'冥界、报应相关记载',
          '天文地理':'天象与地理现象'
        };
        stats.forEach((row)=>{
          const cat = row.narrative_category;
          const v = row.paragraph_count || 0;
          const card = document.createElement('div'); card.className='card';
          card.innerHTML = `<h3>${cat}</h3><div class="small" style="color:#666;margin-bottom:6px">${definitions[cat] || ''}</div><div class="val">${v} 段</div>`;
          card.style.cursor='pointer';
          card.addEventListener('click', async ()=>{
            const listPanel = el('#narrative-para-list');
            const tbody = document.querySelector('#narrative-para-table tbody');
            tbody.innerHTML = '';
            const rows = await fetchJson(apiBase + '/narrative_detail?category=' + encodeURIComponent(cat));
            if(Array.isArray(rows) && rows.length>0){
              rows.forEach(p=>{
                const tr = document.createElement('tr');
                const idTd = document.createElement('td'); idTd.textContent = p.paragraph_id || '';
                const volTd = document.createElement('td'); volTd.textContent = p.volume_title || '';
                const textTd = document.createElement('td'); textTd.textContent = (p.text || '').slice(0, 180);
                tr.appendChild(idTd); tr.appendChild(volTd); tr.appendChild(textTd);
                tbody.appendChild(tr);
              });
            } else {
              const tr = document.createElement('tr'); tr.innerHTML = "<td colspan=3>无段落数据</td>"; tbody.appendChild(tr);
            }
            listPanel.classList.remove('hidden');
          });
          cards.appendChild(card);
        });
      } catch(e){
        const card = document.createElement('div'); card.className='card';
        card.innerHTML = '<h3>叙事结构</h3><div class="small" style="color:#666">数据接口尚未就绪。</div>';
        cards.appendChild(card);
      }
    }

    async function loadThemeTabs(){
      const broadList = ["人物政事","动物","神怪妖魅","植物","器物技艺","建筑寺塔","异域物产","饮食医药","异人方术","梦兆占验","丧葬冥界","佛道信仰","天文地理","礼俗制度"];
      const container = el('#theme-cards'); container.innerHTML = '';
      broadList.forEach((b)=>{
        const c = document.createElement('div'); c.className='card'; c.style.cursor='pointer';
        c.innerHTML = `<div class="tag">${b}</div><div class='name' style='margin-top:6px;font-weight:700'>展开查看子类</div>`;
        c.addEventListener('click', async ()=>{
          document.getElementById('theme-detail-panel').classList.remove('hidden');
          const detail = await fetchJson(apiBase + '/theme_detail?broad=' + encodeURIComponent(b));
          const dist = document.getElementById('theme-sub-distribution'); dist.innerHTML = '';
          // 计数 level1_subject/level2_subject 的组合
          const counts = {};
          detail.forEach(r=>{ const key = (r.level1_subject||'') + '||' + (r.level2_subject||''); counts[key] = (counts[key]||0) + 1; });
          Object.entries(counts).forEach(([k,v])=>{
            const [l1,l2] = k.split('||');
            const span = document.createElement('div'); span.className='tag'; span.style.display='inline-block'; span.style.marginRight='6px';
            span.textContent = (l1||'') + ' -> ' + (l2||'') + ' (' + v + ')'; dist.appendChild(span);
          });
        });
        container.appendChild(c);
      });
    }

    async function loadFrequency(){
      const freq = await fetchJson(apiBase + '/theme_frequency');
      const container = el('#frequency-list'); container.innerHTML = '';
      const max = Math.max(1, ...freq.map(r=>r.appearance_count));
      freq.forEach((row, idx)=>{
        const rowEl = document.createElement('div'); rowEl.style.display='flex'; rowEl.style.alignItems='center'; rowEl.style.gap='8px'; rowEl.style.padding='6px 0';
        const label = document.createElement('div'); label.style.width='180px'; label.style.fontSize='12px'; label.style.color='#555'; label.textContent = (row.level1_subject||'') + ' → ' + (row.level2_subject||'');
        const barWrap = document.createElement('div'); barWrap.className='bar'; barWrap.style.flex='1'; const bar = document.createElement('span'); bar.style.width = Math.round((row.appearance_count / max) * 100) + '%'; barWrap.appendChild(bar);
        const count = document.createElement('div'); count.style.width='60px'; count.style.fontSize='12px'; count.style.color='#333'; count.style.textAlign='right'; count.textContent = row.appearance_count;
        rowEl.appendChild(label); rowEl.appendChild(barWrap); rowEl.appendChild(count); container.appendChild(rowEl);
      });
      // 频次搜索过滤
      const input = document.getElementById('freq-search');
      input.addEventListener('input', () => {
        const q = input.value.toLowerCase();
        const items = Array.from(container.querySelectorAll('.bar-row'));
      });
    }

    async function loadBrowseOptions(){
      const narSel = el('#browse-narrative'); narSel.innerHTML = '<option value="">全部叙事分类</option>';
      try{
        const narr = await fetchJson(apiBase + '/narrative_stats');
        narr.forEach(n => {
          const opt = document.createElement('option'); opt.value = n.narrative_category; opt.textContent = n.narrative_category; narSel.appendChild(opt);
        });
      } catch(e){}
      const broadSel = el('#browse-broad'); broadSel.innerHTML = '<option value="">全部广义类</option>';
      ["人物政事","动物","神怪妖魅","植物","器物名物","建筑寺塔","异域物产","饮食医药","异人方术","梦兆占验","丧葬冥界","佛道信仰","天文地理","礼俗制度"].forEach(b => {
        const opt = document.createElement('option'); opt.value = b; opt.textContent = b; broadSel.appendChild(opt);
      });
      const browseBtn = el('#browse-search');
      browseBtn.addEventListener('click', async () => {
        const narrative = el('#browse-narrative').value;
        const broad = el('#browse-broad').value;
        const search = el('#browse-key').value;
        const q = new URLSearchParams({ narrative, broad, search, page: '1' }).toString();
        const data = await fetchJson(apiBase + '/paragraphs?' + q);
        renderBrowseResults(data);
      });
    }

    function renderBrowseResults(data){
      const tbody = document.querySelector('#browse-table tbody'); tbody.innerHTML = '';
      (data || []).forEach(p => {
        const tr = document.createElement('tr');
        const td1 = document.createElement('td'); td1.textContent = p.paragraph_id || '';
        const td2 = document.createElement('td'); td2.textContent = p.volume_title || '';
        const td3 = document.createElement('td'); td3.textContent = p.narrative_category || '';
        const td4 = document.createElement('td'); td4.textContent = p.theme_list || '';
        const td5 = document.createElement('td'); td5.textContent = (p.text || '').slice(0, 160);
        tr.appendChild(td1); tr.appendChild(td2); tr.appendChild(td3); tr.appendChild(td4); tr.appendChild(td5);
        tbody.appendChild(tr);
      });
    }
  </script>
</body>
</html>
"""


def render_json(data):
    return json.dumps(data, ensure_ascii=False).encode("utf-8")


class SimpleAPIHandler(BaseHTTPRequestHandler):
    def _send(self, code, payload, content_type="application/json; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/":
            self._send(200, HTML_TEMPLATE.encode("utf-8"), "text/html; charset=utf-8")
            return
        if path == "/api/narrative_stats":
            with db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT narrative_category, paragraph_count, absolute_percentage FROM narrative_stats")
                rows = [dict(r) for r in cur.fetchall()]
            self._send(200, render_json(rows))
            return
        if path == "/api/narrative_detail_count":
            with db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM narrative_detail")
                total = cur.fetchone()[0]
            self._send(200, render_json({"total": int(total)}))
            return
        if path == "/api/theme_stats":
            with db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT broad_category, paragraph_count, absolute_percentage FROM theme_stats")
                rows = [dict(r) for r in cur.fetchall()]
            self._send(200, render_json(rows))
            return
        if path == "/api/theme_frequency":
            with db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT level1_subject, level2_subject, appearance_count FROM theme_frequency")
                rows = [dict(r) for r in cur.fetchall()]
            self._send(200, render_json(rows))
            return
        if path == "/api/duplicate_themes":
            with db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT volume_index, volume_title, source, paragraph_id, duplicate_broad_categories, duplicate_specific_subjects, text FROM duplicate_themes")
                rows = [dict(r) for r in cur.fetchall()]
            self._send(200, render_json(rows))
            return
        if path == "/api/theme_detail_counts":
            # 返回主题细分中的唯一具体对象数量，用于首页统计
            with db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(DISTINCT specific_subject) as unique_specific_subjects FROM theme_detail")
                row = cur.fetchone()
                total = row[0] if row else 0
            self._send(200, render_json({"unique_specific_subjects": int(total)}))
            return
        if path == "/api/narrative_detail":
            query = parse_qs(parsed.query)
            category = query.get("category", [None])[0]
            with db_connection() as conn:
                cur = conn.cursor()
                if category:
                    cur.execute("SELECT narrative_category, volume_index, volume_title, source, paragraph_id, text FROM narrative_detail WHERE narrative_category = ?", (category,))
                else:
                    cur.execute("SELECT narrative_category, volume_index, volume_title, source, paragraph_id, text FROM narrative_detail")
                rows = [dict(r) for r in cur.fetchall()]
            self._send(200, render_json(rows))
            return
        if path == "/api/theme_detail":
            query = parse_qs(parsed.query)
            broad = query.get("broad", [None])[0]
            level1 = query.get("level1", [None])[0]
            with db_connection() as conn:
                cur = conn.cursor()
                sql = "SELECT broad_category, level1_subject, level2_subject, specific_subject, volume_index, volume_title, source, paragraph_id, primary_subject, annotation_supported, original_subject, text FROM theme_detail"
                params = []
                conds = []
                if broad:
                    conds.append("broad_category = ?"); params.append(broad)
                if level1:
                    conds.append("level1_subject = ?"); params.append(level1)
                if conds:
                    sql += " WHERE " + " AND ".join(conds)
                cur.execute(sql, tuple(params))
                rows = [dict(r) for r in cur.fetchall()]
            self._send(200, render_json(rows))
            return
        if path == "/api/paragraphs":
            query = parse_qs(parsed.query)
            narrative = query.get("narrative", [None])[0]
            broad = query.get("broad", [None])[0]
            search = query.get("search", [""])[0]
            page = int(query.get("page", [1])[0])
            page_size = 20
            offset = (page - 1) * page_size
            conn = db_connection()
            try:
                cur = conn.cursor()
                # Step 1: find matching paragraph IDs (with optional theme filter)
                id_sql = "SELECT DISTINCT n.paragraph_id FROM narrative_detail AS n"
                id_params = []
                if broad:
                    id_sql += " INNER JOIN theme_detail AS t ON n.paragraph_id = t.paragraph_id WHERE t.broad_category = ?"
                    id_params.append(broad)
                    if narrative:
                        id_sql += " AND n.narrative_category = ?"
                        id_params.append(narrative)
                    if search:
                        id_sql += " AND (n.text LIKE ? OR t.text LIKE ?)"
                        s = "%" + search + "%"
                        id_params.extend([s, s])
                else:
                    id_sql += " WHERE 1=1"
                    if narrative:
                        id_sql += " AND n.narrative_category = ?"
                        id_params.append(narrative)
                    if search:
                        id_sql += " AND n.text LIKE ?"
                        id_params.append("%" + search + "%")
                id_sql += " ORDER BY n.paragraph_id LIMIT ? OFFSET ?"
                id_params.extend([page_size, offset])
                cur.execute(id_sql, tuple(id_params))
                pids = [r["paragraph_id"] for r in cur.fetchall()]
                if not pids:
                    self._send(200, render_json([]))
                    return
                # Step 2: fetch paragraph details
                placeholders = ",".join(["?"] * len(pids))
                cur.execute(f"SELECT paragraph_id, volume_title, narrative_category, text FROM narrative_detail WHERE paragraph_id IN ({placeholders})", tuple(pids))
                para_map = {}
                for r in cur.fetchall():
                    d = dict(r)
                    d["text"] = (d.get("text") or "")[:80] + "…" if len(d.get("text") or "") > 80 else d.get("text", "")
                    para_map[r["paragraph_id"]] = d
                # Step 3: fetch themes for these paragraphs
                cur.execute(f"SELECT paragraph_id, broad_category, level1_subject, level2_subject FROM theme_detail WHERE paragraph_id IN ({placeholders})", tuple(pids))
                theme_map = {}
                for r in cur.fetchall():
                    pid = r["paragraph_id"]
                    theme_map.setdefault(pid, []).append(f"{r['broad_category']}→{r['level1_subject']}→{r['level2_subject']}")
                # Combine
                results = []
                for pid in pids:
                    if pid in para_map:
                        entry = para_map[pid]
                        entry["theme_list"] = "; ".join(set(theme_map.get(pid, [])))
                        results.append(entry)
                self._send(200, render_json(results))
            finally:
                conn.close()
            return
        # 未知端点
        self.send_error(404, "未找到端点")


def run_server(port=8888):
    httpd = ThreadingHTTPServer(("0.0.0.0", port), SimpleAPIHandler)
    print(f"服务器已启动，监听端口 {port}，访问 http://localhost:{port}/")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server(8888)

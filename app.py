import http.server
import socketserver
import json
import sqlite3
import os
import re
from urllib.parse import urlparse, parse_qs
from typing import List, Dict, Any

# Configuration
HOST = "0.0.0.0"
PORT = 8890

# Path to the existing SQLite database (as requested)
DB_PATH = r"C:\Users\lx\Desktop\前期准备\GLM处理\youyang_zazu.db"

# Path to the story data JSON (DO NOT OVERWRITE in runtime)
STORY_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'story_data.json')

// Inline HTML template (single-file HTML page). All CSS/JS are embedded per requirements.
INDEX_HTML = r"""
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>酉阳杂俎 · 诺皋记 神怪可视化</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700&display=swap');
    :root{ --bg:#f4f1ea; --ink:#2c2c2c; --accent:#8b2500; --secondary:#5b7e5b; --gold:#b8860b; --card:#faf8f0; --muted:#7a7265; }
    html,body{height:100%;margin:0;background:var(--bg);color:var(--ink);font-family:'Noto Serif SC', serif;}
    .section{min-height:100vh;padding:6vh 6vw;box-sizing:border-box}
    .hero{display:grid;place-items:center;text-align:center; background:#f5efe0; position:relative}
    .hero .title{font-family:'Noto Serif SC', serif; font-size:14vw; line-height:.9; color:var(--ink);}
    .hero .subtitle{font-size:2.2vw;color:var(--muted); margin-top:1rem}
    .scroll-down{position:absolute;bottom:2vh;left:50%;transform:translateX(-50%);width:28px;height:40px;border-bottom:2px solid var(--ink);border-right:2px solid var(--ink);transform:rotate(45deg);animation:bounce 1.5s infinite}
    @keyframes bounce{0%,100%{transform:rotate(45deg) translateY(0)}50%{transform:rotate(45deg) translateY(8px)}}
    .container{max-width:1100px;margin:0 auto}
    h2{font-family:'Noto Serif SC', serif;font-size:2rem;margin:.5em 0}
    .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}
    .card{background:var(--card);border-radius:8px;padding:16px;border:1px solid #eee;box-shadow:0 2px 8px rgba(0,0,0,.04)}
    .tag{padding:6px 8px;border-radius:999px;font-size:.8rem;margin-right:6px;display:inline-block}
    .tag.red{background:#ffe6e6;border:1px solid #f5caca;color:var(--accent)}
    .tag.green{background:#e8f5e9;border:1px solid #c8e5d0;color:#2e7d32}
    /* Story carousel */
    .carousel{position:relative;overflow:hidden;height:54vh;min-height:360px;border-radius:12px;background:#111}
    .slides{display:flex;height:100%;transition:transform .6s ease}
    .slide{min-width:100%;display:grid;grid-template-columns:1fr 1fr;gap:0}
    .slide .panel{padding:20px;display:flex;flex-direction:column;justify-content:center}
    .image{position:relative;height:100%;border-radius:0 0 0 0;overflow:hidden;background:linear-gradient(135deg,#7a1d1d 0%,#111 60%)}
    .image .grad{position:absolute;inset:0;background:radial-gradient(circle at 20% 20%, rgba(139,37,0,.65) 0%, rgba(0,0,0,.0) 40%), radial-gradient(circle at 80% 60%, rgba(0,0,0,.45) 0%, rgba(0,0,0,.0) 60%)}
    .image .title{position:absolute;left:50%;top:60%;transform:translate(-50%,-60%);color:#fff;font-family:'Brush Script MT', cursive;font-size:3.5rem;opacity:.95}
    .dots{position:absolute;left:50%;bottom:12px;transform:translateX(-50%);display:flex;gap:8px}
    .dot{width:10px;height:10px;border-radius:50%;background:rgba(255,255,255,.5);cursor:pointer}
    .dot.active{background:white}
    @media (max-width: 900px){ .slide{grid-template-columns:1fr} .image{height:260px} .hero .title{font-size:12vw} }
    /* 3a-3d visuals */
    .viz{display:grid;grid-template-columns:1fr 1fr;gap:16px}
    .bar{height:18px;background:#eee;border-radius:9px;overflow:hidden}
    .bar > span{display:block;height:100%;background:linear-gradient(90deg, #8b2500, #5b7e5b)}
  </style>
</head>
<body>
  <section class="section hero" id="overview">
    <div class="container">
      <div class="title" aria-label="酉阳杂俎">酉阳杂俎</div>
      <div class="subtitle">诺皋记 · 唐代志怪的世界</div>
    </div>
    <div class="scroll-down" aria-hidden="true"></div>
  </section>

  <section class="section" id="authors">
    <div class="container">
      <h2>作者介绍</h2>
      <div class="grid">
        <div class="card"><strong>段成式</strong><div>(约803–863), 字柯古</div><p>唐代临淄人；父亲段文昌曾任宰相，官至太常少卿，博闻强记。</p></div>
        <div class="card"><strong>写作动机</strong><p>自序云“固役而不耻者，抑志怪小说之书也”，记录所见所闻之怪异事。</p></div>
      </div>
    </div>
  </section>

  <section class="section" id="stories">
    <div class="container">
      <h2>诺皋记五篇 – Monster & Text</h2>
      <div class="carousel" id="carousel">
        <div class="slides" id="slides"></div>
        <div class="dots" id="dots"></div>
      </div>
      <div class="annotation-note" style="color:var(--muted); font-size:0.95rem; margin-top:8px;">滑动/点击圆点切换故事，触控滑动可通过左右滑动切换。</div>
    </div>
  </section>

  <section class="section" id="detail_text">
    <div class="container" id="detail_container"></div>
  </section>

  <section class="section" id="data_viz">
    <div class="container">
      <h2>数据展示</h2>
      <div class="viz" id="stats_grid"></div>
      <div class="viz" id="narrative_dist"></div>
      <div class="viz" id="keyword_freq"></div>
      <div class="grid" id="story_explanations"></div>
    </div>
  </section>

  <footer class="section" id="footer" style="padding:2rem 6vw;text-align:center;color:var(--muted);border-top:1px solid #e6dacf;">
    数据来源：《酉阳杂俎》初校本 | 分析代码：youyang_analyzer.py<br>
    GitHub: https://github.com/MoonRiver-echo/youyang-zazu
  </footer>

  <script>
    function fetchJSON(url){return fetch(url).then(r => r.ok ? r.json() : Promise.reject('Failed'))}
    let stories = [];
    async function loadStories(){
      try{ stories = await fetchJSON('/api/stories'); }catch(e){ console.error(e); stories = []; }
      buildCarousel();
      return stories;
    }
    function buildCarousel(){
      const slides = document.getElementById('slides'); const dots = document.getElementById('dots'); slides.innerHTML=''; dots.innerHTML='';
      stories.forEach((st, idx) => {
        const slide = document.createElement('div'); slide.className='slide';
        const left = document.createElement('div'); left.className='panel image';
        const grad = document.createElement('div'); grad.className='grad'; left.appendChild(grad);
        const t = document.createElement('div'); t.className='title'; t.textContent = st.title || ('故事'+(idx+1)); left.appendChild(t);
        const right = document.createElement('div'); right.className='panel';
        const meta = document.createElement('div'); meta.style.marginBottom='6px';
        const tag = document.createElement('span'); tag.className='tag red'; tag.textContent = st.monster_type || '神怪';
        const num = document.createElement('span'); num.style.marginLeft='6px'; num.textContent = ' 序号: ' + (st.number || ('S'+(idx+1)));
        meta.appendChild(tag); meta.appendChild(num);
        const brief = document.createElement('p'); brief.textContent = st.brief || st.description || '简述：无';
        right.appendChild(meta); right.appendChild(brief);
        slide.appendChild(left); slide.appendChild(right); slides.appendChild(slide);
        const dot = document.createElement('span'); dot.className = 'dot' + (idx===0?' active':''); dot.dataset.idx = idx; dots.appendChild(dot);
      });
      // basic carousel behavior
      let current = 0; const total = stories.length; function render(){ slides.style.transform = `translateX(${-current*100}%)`; Array.from(dots.children).forEach((d,i)=> d.className = 'dot'+(i===current?' active':'')); }
      render(); // initial
      Array.from(dots.children).forEach(d => d.addEventListener('click', () => { current = Number(d.dataset.idx); render(); }));
      // auto-advance
      let timer = setInterval(() => { if(total>0){ current = (current+1)%total; render(); } }, 8000);
      const carousel = document.getElementById('carousel');
      carousel.addEventListener('mouseenter', () => clearInterval(timer));
      carousel.addEventListener('mouseleave', () => { timer = setInterval(() => { if(total>0){ current = (current+1)%total; render(); } }, 8000); });
      // touch swipe
      let startX = 0; carousel.addEventListener('touchstart', (e)=>{ startX = e.touches[0].clientX; });
      carousel.addEventListener('touchend', (e)=>{ const dx = e.changedTouches[0].clientX - startX; if(Math.abs(dx) > 40){ if(dx<0) { current = (current+1)%total; } else { current = (current-1+total)%total; } render(); } });
    }
    async function loadStats(){ try{ const stats = await fetchJSON('/api/stats'); renderStats(stats); renderNarrative(stats.narrative_stats); renderKeywords(stats.keyword_frequency); renderExplanations(); }catch(e){ console.error(e); } }
    function renderStats(data){ const grid = document.getElementById('stats_grid'); grid.innerHTML=''; const items=[{l:'全书段落',v: data.total_paragraphs || 0},{l:'含超自然关键词段落',v: data.total_shengui_paragraphs || 0},{l:'诺皋记段落 / 神怪相关',v: (data.nuogao_total||0)+' / '+(data.nuogao_shengui||0)},{l:'神怪妖魅类子类',v: (data.narrative_stats? data.narrative_stats.length:0)}]; items.forEach(it=>{ const c=document.createElement('div'); c.className='card'; const h=document.createElement('div'); h.style.fontWeight='700'; h.textContent=it.l; const val=document.createElement('div'); val.style.fontSize='1.6rem'; val.style.marginTop='6px'; val.textContent=it.v; c.appendChild(h); c.appendChild(val); grid.appendChild(c); }); }
    function renderNarrative(rows){ if(!rows) return; const el=document.getElementById('narrative_dist'); el.innerHTML=''; const title=document.createElement('div'); title.style.gridColumn='1 / -1'; title.style.fontWeight='700'; title.style.marginBottom='6px'; title.textContent='叙事分类分布'; el.appendChild(title); rows.forEach(r=>{ const row=document.createElement('div'); row.style.display='flex'; row.style.alignItems='center'; row.style.gap='8px'; const label=document.createElement('div'); label.style.minWidth='180px'; label.textContent = r.narrative_category; row.appendChild(label); const bar=document.createElement('div'); bar.style.flex='1'; bar.className='bar'; const fill=document.createElement('span'); fill.style.width = r.absolute_percentage || '0%'; bar.appendChild(fill); row.appendChild(bar); const pct=document.createElement('div'); pct.style.width='60px'; pct.style.textAlign='right'; pct.textContent = r.absolute_percentage; row.appendChild(pct); el.appendChild(row); }); }
    function renderKeywords(arr){ const el=document.getElementById('keyword_freq'); el.innerHTML=''; if(!arr||arr.length===0){ el.textContent='关键词频次数据不可用'; return; } const title=document.createElement('div'); title.style.gridColumn='1 / -1'; title.style.fontWeight='700'; title.style.marginBottom='6px'; title.textContent='神怪关键词频次 Top 20'; el.appendChild(title); const cloud=document.createElement('div'); cloud.style.display='flex'; cloud.style.flexWrap='wrap'; cloud.style.gap='8px'; const max = Math.max(...arr.map(x=>x.count||1)); arr.forEach(x=>{ const f=(x.count||1)/max; const elTag=document.createElement('span'); elTag.className='tag'; elTag.style.fontSize = (12 + Math.round(8*f))+'px'; elTag.textContent = x.keyword || x[0] || ''; cloud.appendChild(elTag); }); el.appendChild(cloud); }
    function renderExplanations(){ const container=document.getElementById('story_explanations'); container.innerHTML=''; const five = stories.slice(0,5); five.forEach((s, idx)=>{ const card=document.createElement('div'); card.className='card'; const title=document.createElement('div'); title.style.fontWeight='700'; title.textContent = s.title || ('故事'+(idx+1)); const tag=document.createElement('span'); tag.className='tag green'; tag.style.marginLeft='6px'; tag.textContent = s.narrative_category || '分类'; const p=document.createElement('p'); p.style.marginTop='6px'; p.textContent = s.explanation || ''; card.appendChild(title); card.appendChild(tag); card.appendChild(p); container.appendChild(card); }); }
    window.addEventListener('DOMContentLoaded', async () => { await loadStories(); await loadStats(); });
    // Simple scroll-triggered reveal using IntersectionObserver
    const sections = document.querySelectorAll('.section');
    sections.forEach(sec => sec.style.opacity = '0');
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.style.opacity = '1';
          e.target.style.transition = 'opacity 0.6s ease';
        }
      });
    }, { threshold: 0.15 });
    sections.forEach(sec => obs.observe(sec));
  </script>
</body>
</html>
"""

def load_story_data() -> List[Dict[str, Any]]:
    """Load story_data.json from disk. Do not modify the file."""
    try:
        with open(STORY_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'stories' in data:
                return data['stories']
    except FileNotFoundError:
        pass
    # Fallback hard-coded minimal data if the file is missing (safe guard)
    return [
        {"number": "V14-P003", "title": "帝江", "monster_type": "神话异兽", "brief": "天山之神的怪异形态。", "brief": "天山之神的怪异形态。", "brief2": "六足重翼、无面目。", "brief3": "来自山海经的神话意象。", "story": 1},
        {"number": "V14-P006", "title": "天翁张坚", "monster_type": "神仙志怪", "brief": "凡人窃天帝之车登天。"},
        {"number": "V14-P010", "title": "灶神", "monster_type": "民俗神灵", "brief": "灶神家族体系与职权。"},
        {"number": "V14-P014", "title": "龟兹降龙", "monster_type": "降妖伏魔", "brief": "佛道融合的降龙叙事。"},
        {"number": "V15-P001", "title": "骨珠化人", "monster_type": "妖怪变形", "brief": "妖怪变形的诡异叙事。"},
    ]


class YouyangRequestHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="text/html; charset=utf-8"):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        # Parse path and query
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == '/':
            self._set_headers(200, 'text/html; charset=utf-8')
            self.wfile.write(INDEX_HTML.encode('utf-8'))
            return
        if path == '/api/stories':
            data = _get_stories()
            self._set_headers(200, 'application/json; charset=utf-8')
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            return
        if path == '/api/stats':
            data = _get_stats()
            self._set_headers(200, 'application/json; charset=utf-8')
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            return
        if path == '/api/nuogao':
            data = _get_nuogao()
            self._set_headers(200, 'application/json; charset=utf-8')
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            return
        if path == '/api/shengui':
            category = query.get('category', [None])[0]
            data = _get_shengui(category)
            self._set_headers(200, 'application/json; charset=utf-8')
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            return
        # Fallback: 404
        self._set_headers(404, 'text/plain; charset=utf-8')
        self.wfile.write(b'Not Found')

def _read_json_file(path: str) -> Any:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def _get_stories() -> List[Dict[str, Any]]:
    # Read from story_data.json (DO NOT OVERWRITE)
    data = load_story_data()
    if not isinstance(data, list):
        data = []
    return data[:5]

def _get_stats() -> Dict[str, Any]:
    # Connect to SQLite and return aggregate stats. If anything fails, return a best-effort subset.
    stats: Dict[str, Any] = {
        'narrative_stats': [],
        'theme_stats': [],
        'theme_frequency': [],
        'total_paragraphs': 0,
        'total_shengui_paragraphs': 0,
        'nuogao_total': 0,
        'nuogao_shengui': 0,
        'keyword_frequency': []
    }
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        # total paragraphs
        cur.execute("SELECT COUNT(*) FROM narrative_detail")
        total = cur.fetchone()[0] or 0
        stats['total_paragraphs'] = total
        # narrative stats
        try:
            cur.execute("SELECT narrative_category, COUNT(*) AS cnt FROM narrative_detail GROUP BY narrative_category ORDER BY cnt DESC")
            rows = cur.fetchall()
            narrative = []
            for cat, cnt in rows:
                narrative.append({'narrative_category': cat, 'paragraph_count': int(cnt), 'absolute_percentage': _pct(cnt, total)})
            stats['narrative_stats'] = narrative
        except Exception:
            stats['narrative_stats'] = []

        # theme stats (broad categories)
        try:
            cur.execute("SELECT broad_category, COUNT(*) AS cnt FROM narrative_detail GROUP BY broad_category ORDER BY cnt DESC")
            rows = cur.fetchall()
            themes = []
            for cat, cnt in rows:
                themes.append({'broad_category': cat, 'paragraph_count': int(cnt), 'absolute_percentage': _pct(cnt, total)})
            stats['theme_stats'] = themes
        except Exception:
            stats['theme_stats'] = []

        # theme frequency (level1, level2) - best-effort
        try:
            cur.execute("SELECT level1_subject, level2_subject, COUNT(*) AS cnt FROM narrative_detail GROUP BY level1_subject, level2_subject ORDER BY cnt DESC LIMIT 50")
            rows = cur.fetchall()
            stats['theme_frequency'] = [ {'level1_subject': r[0], 'level2_subject': r[1], 'appearance_count': int(r[2])} for r in rows ]
        except Exception:
            stats['theme_frequency'] = []

        # nuogao counts
        try:
            cur.execute("SELECT COUNT(*) FROM narrative_detail WHERE volume_title LIKE ?", ('%诺皋%',))
            nu_total = cur.fetchone()[0] or 0
            stats['nuogao_total'] = int(nu_total)
        except Exception:
            stats['nuogao_total'] = 0
        try:
            cur.execute("SELECT COUNT(*) FROM narrative_detail WHERE volume_title LIKE ? AND (keywords IS NOT NULL OR shengui IS NOT NULL)", ('%诺皋%',))
            nu_shengui = cur.fetchone()[0] or 0
            stats['nuogao_shengui'] = int(nu_shengui)
        except Exception:
            stats['nuogao_shengui'] = 0

        # keyword frequency (top 20) - try table first, then fallback to story_data.json
        try:
            cur.execute("SELECT keyword, COUNT(*) AS cnt FROM keyword_frequency GROUP BY keyword ORDER BY cnt DESC LIMIT 20")
            rows = cur.fetchall()
            stats['keyword_frequency'] = [ {'keyword': r[0], 'count': int(r[1])} for r in rows ]
        except Exception:
            # Fallback: load from story_data.json if available
            kf = []
            data = load_story_data()
            if isinstance(data, list):
                freq = {}
                for s in data:
                    for kw in s.get('keywords', []) if isinstance(s.get('keywords', []), list) else []:
                        freq[kw] = freq.get(kw, 0) + 1
                kf = sorted([{'keyword': k, 'count': v} for k, v in freq.items()], key=lambda x: x['count'], reverse=True)[:20]
            stats['keyword_frequency'] = kf
        conn.close()
    except Exception:
        # All else fails, return empty structures to keep UI functional
        pass
    return stats

def _pct(part: int, total: int) -> str:
    if total <= 0:
        return '0%'
    val = int(round((part / total) * 100, 0))
    return f"{val}%"

def _get_nuogao() -> Dict[str, Any]:
    data = []
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        try:
            cur.execute("SELECT id, volume_title, paragraph_text FROM narrative_detail WHERE volume_title LIKE ? ORDER BY id LIMIT 200", ('%诺皋%',))
        except Exception:
            cur.execute("SELECT id, volume_title, paragraph_text FROM narrative_detail WHERE volume_title LIKE ? ORDER BY id LIMIT 200", ('%诺皋%',))
        rows = cur.fetchall()
        for r in rows:
            data.append({'id': r[0], 'volume_title': r[1], 'paragraph': (r[2] if len(r) > 2 else '')})
        conn.close()
    except Exception:
        pass
    return {'paragraphs': data}

def _get_shengui(category: str | None) -> Dict[str, Any]:
    # Best-effort: retrieve a subset of paragraphs with shengui keywords, optionally filter by category
    results = []
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        if category:
            try:
                cur.execute("SELECT id, volume_title, paragraph_text, keywords FROM narrative_detail WHERE keywords LIKE ? AND volume_title LIKE ? LIMIT 100", ('%'+category+'%', '%'))
            except Exception:
                cur.execute("SELECT id, volume_title, paragraph_text, keywords FROM narrative_detail WHERE volume_title LIKE ? LIMIT 100", ('%',))
        else:
            cur.execute("SELECT id, volume_title, paragraph_text, keywords FROM narrative_detail WHERE keywords IS NOT NULL LIMIT 100")
        rows = cur.fetchall()
        for r in rows:
            results.append({ 'id': r[0], 'volume_title': r[1], 'paragraph': r[2], 'keywords': r[3:] if len(r) > 3 else [] })
        conn.close()
    except Exception:
        pass
    return {'paragraphs': results}

def _get_stories_cache() -> List[Dict[str, Any]]:
    return load_story_data()[:5]

def load_configured_db() -> None:
    # Helper to ensure DB path exists; no hard requirement to create DB here
    if not os.path.exists(DB_PATH):
        print("Warning: Database path not found:", DB_PATH)

def main():
    load_configured_db()
    with socketserver.TCPServer((HOST, PORT), YouyangRequestHandler) as httpd:
        print(f"Serving at http://{HOST}:{PORT}/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自包含神怪可视化服务器。
数据直接嵌入HTML，无需API调用。
"""
import json, webbrowser, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

BASE_DIR = Path(__file__).parent
PORT = 8890


def build_html():
    """Load data and build self-contained HTML."""
    with open(BASE_DIR / "story_data.json", encoding="utf-8") as f:
        data = json.load(f)

    stories = data["stories"]
    stats = data["stats"]

    # Process annotations
    import re
    for s in stories:
        anns = []
        counter = [0]
        def mk(m):
            counter[0] += 1
            nid = "n" + str(counter[0])
            anns.append({"id": nid, "text": m.group(1).strip()})
            return "[" + nid + "]"
        t = re.sub(r"\{\{([^}]+)\}\}", mk, s.get("original_text", ""))
        t = re.sub(r"（([^）]*?(?:一曰|一作)[^）]*?)）", mk, t)
        t = re.sub(r"\(([^)]*?(?:一曰|一作)[^)]*?)\)", mk, t)
        s["annotated_text"] = t
        s["annotations"] = anns

    stories_json = json.dumps(stories, ensure_ascii=False)
    stats_json = json.dumps(stats, ensure_ascii=False)

    # Explanations
    expl = {
        "V14-P003": "此段归入「异闻志怪」，因描写天山之神帝江的怪异形态——六足重翼、无面目，实为帝江。刑天与帝争神，被断首葬于常羊山，以乳为目、脐为口、操干戚而舞——这正是《山海经》中著名的刑天神话。关键词「神」标志神灵描写核心。",
        "V14-P006": "凡人窃天帝之车登天、封白雀为上卿——此段融合神仙志怪与梦境母题，展现道教天界想象。张坚以白雀预警、乘龙升天的叙事结构，是典型的「凡人窃位」母题。关键词「龙」指向乘龙登天的升仙叙事。",
        "V14-P010": "灶神名隗状如美女——此段详述灶神家族体系与职权，是研究唐代民间信仰的重要材料。灶神「常以月晦日上天白人罪状」的描述，揭示了从家宅神灵到天界官僚的信仰体系。关键词「精」「神」「天帝」指向精怪与天界官僚体系的交织。",
        "V14-P014": "龟兹国王降伏毒龙、乘龙而行——此段融合佛教罗汉与本土降龙叙事，展现西域佛教文化与中原志怪传统的交汇。罗汉指出龙居北山、国王持剑降伏的情节，暗示唐代对异域宗教与武力的双重认知。关键词「罗汉」「龙」体现佛道融合特色。",
        "V15-P001": "食鱼吐骨珠化为活人——此段是典型的妖怪变形叙事，骨头→骨珠→骨人→分裂→合体的变形链条极度诡奇。骨珠随视而长、两半人触合成一的描写，表现了唐代志怪中对「身体边界」的想象。关键词「怪」标志妖怪变形母题。",
    }
    expl_json = json.dumps(expl, ensure_ascii=False)

    # CSS for slide backgrounds
    slide_bg_css = """
.slide-bg-0 { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 40%, #0f3460 100%); }
.slide-bg-1 { background: linear-gradient(135deg, #2d1b00 0%, #5c3d2e 40%, #8b5e3c 100%); }
.slide-bg-2 { background: linear-gradient(135deg, #1b3a1b 0%, #2d5a2d 40%, #3e7a3e 100%); }
.slide-bg-3 { background: linear-gradient(135deg, #3d0c02 0%, #6b1d0e 40%, #8b2500 100%); }
.slide-bg-4 { background: linear-gradient(135deg, #2a1a3e 0%, #4a2a6e 40%, #6b3fa0 100%); }
"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>酉阳杂俎 · 诺皋记 — 神怪可视化</title>
<style>
:root{{
--bg:#f4f1ea;--card:#faf8f0;--ink:#2c2c2c;--vermillion:#8b2500;--bamboo:#5b7e5b;--gold:#b8860b;--muted:#7a7265;--light:#e8e2d6;--shadow:0 4px 20px rgba(0,0,0,.08);--radius:8px
}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{font-family:"Noto Serif SC","Songti SC","SimSun","STSong",serif;background:var(--bg);color:var(--ink);line-height:1.8;overflow-x:hidden}}
a{{color:var(--vermillion);text-decoration:none}}
.reveal{{opacity:0;transform:translateY(30px);transition:opacity .8s ease,transform .8s ease}}
.reveal.visible{{opacity:1;transform:translateY(0)}}

/* Hero */
.hero{{min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:2rem;background:linear-gradient(180deg,#f4f1ea 0%,#e8e0d0 100%);position:relative}}
.hero::before{{content:'';position:absolute;top:0;left:0;width:100%;height:100%;background:radial-gradient(circle at 30% 40%,rgba(139,37,0,.06),transparent 60%),radial-gradient(circle at 70% 60%,rgba(91,126,91,.06),transparent 60%);pointer-events:none}}
.hero-title{{font-size:clamp(3rem,8vw,6rem);font-weight:900;letter-spacing:.4em;color:var(--ink);position:relative;margin-bottom:1rem;text-shadow:2px 2px 0 rgba(139,37,0,.1)}}
.hero-subtitle{{font-size:clamp(1rem,3vw,1.5rem);color:var(--muted);letter-spacing:.3em;margin-bottom:2rem}}
.hero-arrow{{animation:bounce 2s infinite;cursor:pointer;margin-top:2rem;font-size:1.5rem;color:var(--muted)}}
@keyframes bounce{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(10px)}}}}

/* Sections */
.section{{max-width:960px;margin:0 auto;padding:4rem 2rem}}
.section h2{{font-size:1.8rem;color:var(--vermillion);margin-bottom:1.5rem;border-bottom:2px solid var(--vermillion);padding-bottom:.5rem;display:inline-block}}
.section h3{{font-size:1.4rem;color:var(--ink);margin:1.5rem 0 1rem}}
.section p{{margin-bottom:1rem;text-align:justify}}

/* Author card */
.author-card{{background:var(--card);border-radius:var(--radius);box-shadow:var(--shadow);padding:2rem;margin-bottom:2rem;border-left:4px solid var(--vermillion)}}
.author-name{{font-size:1.6rem;font-weight:700;color:var(--vermillion);margin-bottom:.5rem}}
.author-detail{{color:var(--muted);font-size:.95rem;margin-bottom:1rem}}
.source-note{{font-size:.85rem;color:var(--muted);font-style:italic;margin-top:1rem}}

/* Direction */
.direction-box{{background:linear-gradient(135deg,var(--card),#f0ede5);border-radius:var(--radius);box-shadow:var(--shadow);padding:2rem;margin-bottom:2rem}}
.stat-inline{{color:var(--vermillion);font-weight:700}}
.dimension-list{{display:flex;gap:2rem;margin-top:1.5rem;flex-wrap:wrap}}
.dimension-item{{flex:1;min-width:200px;background:var(--card);border-radius:var(--radius);padding:1.5rem;border-top:3px solid var(--bamboo)}}
.dimension-item h4{{color:var(--bamboo);font-size:1.1rem;margin-bottom:.5rem}}

.divider{{text-align:center;padding:3rem 0;color:var(--muted);font-size:1.2rem;letter-spacing:1em}}

/* Carousel */
.carousel-wrap{{position:relative;overflow:hidden;margin:2rem 0;border-radius:12px;box-shadow:var(--shadow)}}
.carousel-track{{display:flex;transition:transform .5s ease}}
.carousel-slide{{min-width:100%;padding:2.5rem;min-height:320px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;position:relative;color:#fff}}
.slide-mist{{position:absolute;top:0;left:0;width:100%;height:100%;background:radial-gradient(ellipse at 20% 50%,rgba(255,255,255,.08),transparent 50%),radial-gradient(ellipse at 80% 30%,rgba(255,255,255,.05),transparent 40%),radial-gradient(ellipse at 50% 80%,rgba(0,0,0,.3),transparent 60%);pointer-events:none}}
.slide-number{{font-size:.9rem;color:rgba(255,255,255,.5);letter-spacing:.2em;margin-bottom:.5rem;position:relative;z-index:1}}
.slide-title{{font-size:clamp(1.6rem,4vw,2.4rem);font-weight:900;color:#fff;text-shadow:2px 2px 8px rgba(0,0,0,.5);margin-bottom:.8rem;position:relative;z-index:1}}
.slide-type{{display:inline-block;background:rgba(255,255,255,.15);color:#fff;border:1px solid rgba(255,255,255,.3);border-radius:20px;padding:3px 14px;font-size:.85rem;margin-bottom:1rem;position:relative;z-index:1}}
.slide-brief{{font-size:1rem;color:rgba(255,255,255,.85);max-width:600px;line-height:1.8;margin-bottom:1rem;position:relative;z-index:1}}
.slide-img{{width:auto;max-width:90%;max-height:260px;border-radius:8px;box-shadow:0 4px 16px rgba(0,0,0,.4);position:relative;z-index:1;margin-bottom:1rem;object-fit:contain}}
.slide-img-credit{{font-size:.7rem;color:rgba(255,255,255,.45);position:relative;z-index:1;margin-bottom:.5rem}}
.carousel-dots{{position:absolute;bottom:20px;left:20px;display:flex;gap:8px;z-index:5}}
.carousel-dots .dot{{width:10px;height:10px;border-radius:50%;background:rgba(255,255,255,.4);cursor:pointer;transition:background .3s;border:none;padding:0}}
.carousel-dots .dot.active{{background:#fff}}
.carousel-btn{{position:absolute;top:50%;transform:translateY(-50%);background:rgba(0,0,0,.4);color:#fff;border:none;padding:12px 16px;cursor:pointer;font-size:1.2rem;z-index:5;border-radius:4px;transition:background .3s}}
.carousel-btn:hover{{background:rgba(0,0,0,.7)}}
.carousel-btn.prev{{left:10px}}
.carousel-btn.next{{right:10px}}

{slide_bg_css}

/* Story detail */
.story-detail{{background:var(--card);border-radius:var(--radius);box-shadow:var(--shadow);padding:2rem;margin:2rem 0}}
.story-metadata{{display:flex;gap:.5rem;flex-wrap:wrap;margin-bottom:1.5rem;align-items:center}}
.story-tag{{display:inline-block;padding:2px 10px;border-radius:20px;font-size:.85rem;background:var(--light);color:var(--ink)}}
.story-tag.keyword{{background:rgba(139,37,0,.1);color:var(--vermillion);border:1px solid rgba(139,37,0,.2)}}
.story-tag.theme{{background:rgba(91,126,91,.1);color:var(--bamboo);border:1px solid rgba(91,126,91,.2)}}
.original-text{{font-size:1.05rem;line-height:2;background:var(--card);padding:1.5rem;border-radius:6px;border-left:3px solid var(--vermillion);margin:1.5rem 0}}
.annotation{{color:var(--vermillion);border-bottom:1px dotted var(--vermillion);cursor:help;position:relative;background:rgba(139,37,0,.06);padding:0 2px;border-radius:2px}}
.annotation:hover{{background:rgba(139,37,0,.15)}}
.annotation .tip{{display:none;position:absolute;bottom:125%;left:50%;transform:translateX(-50%);background:#2c2c2c;color:#fff;padding:8px 14px;border-radius:6px;font-size:.85rem;max-width:300px;min-width:100px;z-index:100;line-height:1.6;box-shadow:0 4px 12px rgba(0,0,0,.3);white-space:normal;text-align:left}}
.annotation:hover .tip{{display:block}}
.annotation .tip::after{{content:'';position:absolute;top:100%;left:50%;transform:translateX(-50%);border:6px solid transparent;border-top-color:#2c2c2c}}
.translation-box{{background:var(--card);border-radius:6px;padding:1.5rem 2rem;margin:1.5rem 0;border-left:3px solid var(--bamboo)}}
.translation-header{{font-size:1.1rem;font-weight:700;color:var(--bamboo);margin-bottom:.8rem}}
.translation-ai-note{{font-size:.75rem;font-weight:400;color:var(--muted)}}
.translation-content{{font-size:1rem;line-height:2;color:var(--ink);text-align:justify}}
.brief-box{{background:rgba(139,37,0,.05);border-left:3px solid var(--vermillion);padding:1rem 1.5rem;border-radius:0 6px 6px 0;margin-top:1.5rem}}

/* Stats */
.stats-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;margin:2rem 0}}
.stat-card{{background:var(--card);border-radius:var(--radius);box-shadow:var(--shadow);padding:1.5rem;text-align:center;border-top:3px solid var(--vermillion)}}
.stat-number{{font-size:2.5rem;font-weight:900;color:var(--vermillion)}}
.stat-label{{font-size:.95rem;color:var(--muted);margin-top:.3rem}}
.bar-chart{{margin:2rem 0}}
.bar-row{{display:flex;align-items:center;gap:8px;margin-bottom:8px}}
.bar-label{{width:100px;font-size:.85rem;text-align:right;color:var(--ink);flex-shrink:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.bar-track{{flex:1;height:20px;background:var(--light);border-radius:10px;overflow:hidden;position:relative}}
.bar-fill{{height:100%;border-radius:10px;transition:width 1s ease}}
.bar-value{{width:50px;font-size:.8rem;color:var(--muted);text-align:left}}
.bar-fill.highlight{{background:linear-gradient(90deg,#8b2500,#c44020)}}
.bar-fill.normal{{background:linear-gradient(90deg,#5b7e5b,#8ba88b)}}
.keyword-cloud{{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;padding:1rem;margin:2rem 0}}
.keyword-bubble{{display:inline-flex;align-items:center;justify-content:center;border-radius:50%;color:var(--ink);font-weight:600;transition:transform .2s;cursor:default}}
.keyword-bubble:hover{{transform:scale(1.15)}}
.explain-cards{{display:flex;flex-direction:column;gap:1.5rem;margin:2rem 0}}
.explain-card{{background:var(--card);border-radius:var(--radius);box-shadow:var(--shadow);padding:1.5rem;border-left:4px solid var(--gold)}}
.explain-card h4{{color:var(--vermillion);font-size:1.1rem;margin-bottom:.5rem}}
.explain-card .meta{{font-size:.85rem;color:var(--muted);margin-bottom:.8rem}}
.explain-card .explanation{{font-size:.95rem;line-height:1.8;text-align:justify}}

/* Footer */
footer{{text-align:center;padding:3rem 2rem;color:var(--muted);font-size:.85rem;border-top:1px solid var(--light);margin-top:4rem}}

/* Responsive */
@media(max-width:600px){{
.hero-title{{letter-spacing:.2em}}
.section{{padding:2rem 1rem}}
.carousel-slide{{padding:1.5rem;min-height:280px}}
.stats-grid{{grid-template-columns:1fr 1fr}}
.bar-label{{width:60px;font-size:.75rem}}
.dimension-list{{flex-direction:column}}
}}
</style>
</head>
<body>

<!-- HERO -->
<section class="hero" id="top">
  <div class="hero-title">酉阳杂俎</div>
  <div class="hero-subtitle">诺皋记 · 唐代志怪的世界</div>
  <div style="color:var(--muted);font-size:.95rem;margin-top:1rem">段成式 · 晚唐志怪笔记</div>
  <div class="hero-arrow" onclick="document.getElementById('overview').scrollIntoView({{behavior:'smooth'}})">▽</div>
</section>

<div class="divider">◆ ◆ ◆</div>

<!-- OVERVIEW -->
<section class="section reveal" id="overview">
  <h2>总览</h2>
  <div class="author-card reveal">
    <div class="author-name">段成式（约803—863）</div>
    <div class="author-detail">字柯古 · 唐代临淄人 · 太常少卿</div>
    <p>段成式出身显赫，其父段文昌曾任唐宪宗朝宰相。成式历任集贤殿学士、处州刺史、江州刺史，官至太常少卿。他博闻强记，精通佛典，与李商隐、温庭筠齐名，时称"三十六才子"。</p>
    <p>关于著书动机，段成式在自序中明言：<em>"固役而不耻者，抑志怪小说之书也"</em>，又道<em>"饱食之暇，偶录记忆"</em>。他在诺皋记卷首写道，因"览历代怪书，偶疏所记"，遂成此编。这表明《酉阳杂俎》是一部自觉的志怪之书，作者以记录者的姿态，广泛收罗鬼神怪异之事。</p>
    <div class="source-note">据《旧唐书》《新唐书》及段成式自序整理</div>
  </div>

  <h3>从叙事性与文化史角度进入神怪世界</h3>
  <div class="direction-box reveal">
    <p>本网站聚焦《酉阳杂俎》中的神怪描写，尤其是<strong>诺皋记</strong>卷所收录的志怪故事。全书<em class="stat-inline">794段</em>中，<em class="stat-inline">341段（43%）</em>含超自然关键词。诺皋记上下两卷共<em class="stat-inline">65段</em>，其中<em class="stat-inline">44段（68%）</em>涉及神鬼妖魔怪。</p>
    <div class="dimension-list">
      <div class="dimension-item">
        <h4>叙事性维度</h4>
        <p>每一段志怪故事如何建构其怪异叙事——从起因、变形到结局。段成式笔下的怪异不是目的，而是理解唐代想象力的入口。</p>
      </div>
      <div class="dimension-item">
        <h4>文化史维度</h4>
        <p>这些故事反映了唐代人怎样的鬼神观念、巫术信仰与文化想象。从灶神官僚体系到刑天舞干戚，从降龙故事到骨珠化人——志怪是理解一个时代精神世界的密码。</p>
      </div>
    </div>
  </div>
</section>

<div class="divider">◆ ◆ ◆</div>

<!-- STORIES -->
<section class="section reveal" id="stories">
  <h2>诺皋记 · 五篇</h2>
  <p style="color:var(--muted);margin-bottom:2rem">诺皋记为《酉阳杂俎》专述鬼神怪异之卷。"诺皋"一名，学界多认为与巫祝禁咒之语有关，段成式自言因"览历代怪书，偶疏所记"而作。以下五篇，各见一种怪异的形与意。</p>

  <div class="carousel-wrap" id="carousel">
    <div class="carousel-track" id="carouselTrack"></div>
    <button class="carousel-btn prev" onclick="slideCarousel(-1)">&#8249;</button>
    <button class="carousel-btn next" onclick="slideCarousel(1)">&#8250;</button>
    <div class="carousel-dots" id="carouselDots"></div>
  </div>

  <div class="story-detail" id="storyDetail">
    <div class="story-metadata" id="storyTags"></div>
    <h3 id="storyTitle" style="color:var(--vermillion)"></h3>
    <div style="font-size:.85rem;color:var(--muted);margin-bottom:1rem" id="storyVolume"></div>
    <div class="original-text" id="storyText"></div>
    <div class="translation-box" id="storyTranslation">
      <div class="translation-header">译文 <span class="translation-ai-note">（AI生成，仅供参考）</span></div>
      <div class="translation-content" id="storyTranslationText"></div>
    </div>
    <div class="brief-box" id="storyBrief"></div>
  </div>
</section>

<div class="divider">◆ ◆ ◆</div>

<!-- DATA -->
<section class="section reveal" id="data">
  <h2>数据 · 神怪的面孔</h2>
  <div class="stats-grid" id="statsGrid"></div>
  <h3>叙事分类分布</h3>
  <div class="bar-chart" id="barChart"></div>
  <h3>神怪关键词频次（前20）</h3>
  <div class="keyword-cloud" id="keywordCloud"></div>
  <h3>五篇故事的分类解读</h3>
  <div class="explain-cards" id="explainCards"></div>
</section>

<footer>
  <div>数据来源：《酉阳杂俎》初校本 · 分析代码：youyang_analyzer.py</div>
  <div style="margin-top:.5rem"><a href="https://github.com/MoonRiver-echo/youyang-zazu" target="_blank">GitHub → youyang-zazu</a></div>
</footer>

<script>
// ── INLINE DATA ──
var storiesData = {stories_json};
var statsData = {stats_json};
var EXPLANATIONS = {expl_json};

var currentSlide = 0;
var autoAdvanceTimer = null;
var autoAdvanceResumeTimer = null;
var AUTO_ADVANCE_MS = 20000;  // 20 seconds between slides
var RESUME_DELAY_MS = 60000;  // 60 seconds pause after user interaction

// ── Carousel ──
function renderCarousel() {{
  var track = document.getElementById("carouselTrack");
  var dots = document.getElementById("carouselDots");
  if (!track || !dots) return;
  var bgs = ["slide-bg-0","slide-bg-1","slide-bg-2","slide-bg-3","slide-bg-4"];
  track.innerHTML = "";
  dots.innerHTML = "";
  for (var i = 0; i < storiesData.length; i++) {{
    var s = storiesData[i];
    var div = document.createElement("div");
    div.className = "carousel-slide " + bgs[i % bgs.length];
    div.innerHTML = '<div class="slide-mist"></div>'
      + '<div class="slide-number">' + s.volume_title + ' · 第' + (i+1) + '篇</div>'
      + '<img class="slide-img" src="/images/' + s.pid + '.png?v=2" alt="' + s.title + ' 插图">'
      + '<div class="slide-img-credit">插图 · AI 生成</div>'
      + '<div class="slide-title">' + s.title + '</div>'
      + '<div class="slide-type">' + s.monster_type + '</div>'
      + '<div class="slide-brief">' + s.brief + '</div>';
    track.appendChild(div);
    var dot = document.createElement("button");
    dot.className = "dot" + (i === 0 ? " active" : "");
    dot.setAttribute("data-idx", i);
    dot.onclick = function() {{ goToSlide(parseInt(this.getAttribute("data-idx"))); pauseAutoAdvance(); }};
    dots.appendChild(dot);
  }}
}}

function goToSlide(idx) {{
  currentSlide = idx;
  document.getElementById("carouselTrack").style.transform = "translateX(-" + (idx * 100) + "%)";
  var allDots = document.querySelectorAll(".carousel-dots .dot");
  for (var i = 0; i < allDots.length; i++) {{
    allDots[i].className = "dot" + (i === idx ? " active" : "");
  }}
  renderStory(idx);
}}

function pauseAutoAdvance() {{
  clearInterval(autoAdvanceTimer);
  autoAdvanceTimer = null;
  clearTimeout(autoAdvanceResumeTimer);
  autoAdvanceResumeTimer = setTimeout(function() {{ startAutoAdvance(); }}, RESUME_DELAY_MS);
}}

function slideCarousel(dir) {{
  var next = currentSlide + dir;
  if (next < 0) next = storiesData.length - 1;
  if (next >= storiesData.length) next = 0;
  goToSlide(next);
  pauseAutoAdvance();
}}

function startAutoAdvance() {{ autoAdvanceTimer = setInterval(function() {{ slideCarousel(1); }}, AUTO_ADVANCE_MS); }}

// ── Story detail ──
function renderStory(idx) {{
  var s = storiesData[idx];
  if (!s) return;
  document.getElementById("storyTitle").textContent = s.title;
  document.getElementById("storyVolume").textContent = s.volume_title + " · " + s.narrative_category;

  var tags = "";
  tags += '<span class="story-tag" style="background:rgba(139,37,0,.15);color:var(--vermillion);border:1px solid rgba(139,37,0,.3)">' + s.monster_type + '</span>';
  var kw = s.shengui_keywords || [];
  for (var k = 0; k < kw.length; k++) {{
    tags += '<span class="story-tag keyword">' + kw[k] + '</span>';
  }}
  var th = s.themes || [];
  for (var t = 0; t < th.length; t++) {{
    tags += '<span class="story-tag theme">' + th[t].broad_category + ' · ' + th[t].level1_subject + ' · ' + th[t].level2_subject + '</span>';
  }}
  document.getElementById("storyTags").innerHTML = tags;

  // Build annotations
  var text = s.annotated_text || s.original_text || "";
  var annMap = {{}};
  var annList = s.annotations || [];
  for (var a = 0; a < annList.length; a++) {{
    annMap[annList[a].id] = annList[a].text;
  }}
  // Replace [nX] with annotation spans
  var result = "";
  var regex = /\[n(\d+)\]/g;
  var match;
  var lastIdx = 0;
  while ((match = regex.exec(text)) !== null) {{
    result += text.substring(lastIdx, match.index);
    var noteText = annMap["n" + match[1]];
    if (noteText) {{
      result += '<span class="annotation" tabindex="0">' + noteText + '<span class="tip">' + noteText + '</span></span>';
    }} else {{
      result += match[0];
    }}
    lastIdx = regex.lastIndex;
  }}
  result += text.substring(lastIdx);
  document.getElementById("storyText").innerHTML = result;
  // Translation
  var transEl = document.getElementById("storyTranslationText");
  if (transEl) {{
    if (s.translation && s.translation.length > 0) {{
      transEl.textContent = s.translation;
    }} else {{
      transEl.textContent = "【译文待补充】";
    }}
  }}
  document.getElementById("storyBrief").innerHTML = "<strong>段落概括：</strong>" + s.brief;
}}

// ── Stats ──
function renderStats() {{
  var grid = document.getElementById("statsGrid");
  if (!grid) return;
  var tp = statsData.total_paragraphs || 794;
  var ts = statsData.total_shengui_paragraphs || 341;
  var nt = statsData.nuogao_total || 65;
  var ns = statsData.nuogao_shengui || 44;
  var items = [
    {{"label": "全书段落", "value": tp}},
    {{"label": "含超自然关键词", "value": ts + "段 (" + Math.round(ts / tp * 100) + "%)"}},
    {{"label": "诺皋记 / 神怪相关", "value": nt + "段 / " + ns + "段 (" + Math.round(ns / nt * 100) + "%)"}},
    {{"label": "神怪妖魅类子类", "value": "14"}}
  ];
  var html = "";
  for (var i = 0; i < items.length; i++) {{
    html += '<div class="stat-card"><div class="stat-number">' + items[i].value + '</div><div class="stat-label">' + items[i].label + '</div></div>';
  }}
  grid.innerHTML = html;
}}

function renderBars() {{
  var narr = statsData.narrative_stats || [];
  if (!narr.length) return;
  var chart = document.getElementById("barChart");
  if (!chart) return;
  var maxVal = 0;
  for (var i = 0; i < narr.length; i++) {{
    if (narr[i].paragraph_count > maxVal) maxVal = narr[i].paragraph_count;
  }}
  if (maxVal <= 0) return;
  var html = "";
  for (var i = 0; i < narr.length; i++) {{
    var n = narr[i];
    var pct = (n.paragraph_count / maxVal * 100).toFixed(1);
    var isHL = (n.narrative_category === "异闻志怪");
    html += '<div class="bar-row">'
      + '<div class="bar-label">' + n.narrative_category + '</div>'
      + '<div class="bar-track"><div class="bar-fill ' + (isHL ? 'highlight' : 'normal') + '" style="width:' + pct + '%"></div></div>'
      + '<div class="bar-value">' + n.paragraph_count + '段</div>'
      + '</div>';
  }}
  chart.innerHTML = html;
}}

function renderKeywords() {{
  var kw = (statsData.keyword_frequency || []).slice(0, 20);
  if (!kw.length) return;
  var cloud = document.getElementById("keywordCloud");
  if (!cloud) return;
  var maxC = 0;
  for (var i = 0; i < kw.length; i++) {{
    if (kw[i].count > maxC) maxC = kw[i].count;
  }}
  if (maxC <= 0) return;
  var html = "";
  for (var i = 0; i < kw.length; i++) {{
    var ratio = kw[i].count / maxC;
    var size = Math.max(12, Math.round(ratio * 32 + 12));
    var op = Math.max(0.4, ratio);
    html += '<span class="keyword-bubble" style="font-size:' + size + 'px;width:' + (size * 2.5) + 'px;height:' + (size * 2.5) + 'px;background:rgba(139,37,0,' + (op * 0.15).toFixed(2) + ');padding:' + (size * 0.4) + 'px" title="' + kw[i].keyword + ': ' + kw[i].count + '次">'
      + kw[i].keyword + '</span>';
  }}
  cloud.innerHTML = html;
}}

function renderExplanations() {{
  var container = document.getElementById("explainCards");
  if (!container) return;
  var html = "";
  for (var i = 0; i < storiesData.length; i++) {{
    var s = storiesData[i];
    var exp = EXPLANATIONS[s.pid] || "暂无解读";
    html += '<div class="explain-card">'
      + '<h4>' + s.title + '</h4>'
      + '<div class="meta">' + s.volume_title + ' · ' + s.narrative_category + ' · 关键词: ' + (s.shengui_keywords || []).join("、") + '</div>'
      + '<div class="explanation">' + exp + '</div>'
      + '</div>';
  }}
  container.innerHTML = html;
}}

// ── Init ──
document.addEventListener("DOMContentLoaded", function() {{
  renderCarousel();
  if (storiesData.length > 0) renderStory(0);
  renderStats();
  renderBars();
  renderKeywords();
  renderExplanations();
  startAutoAdvance();

  // Touch swipe
  var el = document.getElementById("carousel");
  if (el) {{
    var startX = 0;
    el.addEventListener("touchstart", function(e) {{ startX = e.touches[0].clientX; }}, {{passive: true}});
    el.addEventListener("touchend", function(e) {{
      var dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 40) {{ slideCarousel(dx > 0 ? -1 : 1); }}
    }}, {{passive: true}});
    el.addEventListener("mouseenter", function() {{ clearInterval(autoAdvanceTimer); autoAdvanceTimer = null; clearTimeout(autoAdvanceResumeTimer); }});
    el.addEventListener("mouseleave", function() {{ if (!autoAdvanceTimer) startAutoAdvance(); }});
  }}

  // Scroll reveal
  var reveals = document.querySelectorAll(".reveal");
  for (var i = 0; i < reveals.length; i++) {{
    reveals[i].classList.add("visible");
  }}
}});
</script>
</body>
</html>"""

    return html


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self._html = build_html()
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(self._html.encode("utf-8"))
            return
        if self.path.startswith("/images/"):
            # Serve image files from the images directory
            image_path = BASE_DIR / self.path.lstrip("/")
            if image_path.exists() and image_path.is_file():
                ext = image_path.suffix.lower()
                content_type = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif", "webp": "image/webp"}.get(ext.lstrip("."), "application/octet-stream")
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.end_headers()
                with open(str(image_path), "rb") as f:
                    self.wfile.write(f.read())
                return
            self.send_error(404)
            return
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()


def run_server(port=PORT):
    httpd = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"酉阳杂俎 · 神怪可视化 服务器已启动")
    print(f"访问地址: http://localhost:{port}/")
    webbrowser.open(f"http://localhost:{port}/")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server(PORT)
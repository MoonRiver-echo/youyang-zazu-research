/**
 * analysis.js — 数据分析页面图表渲染
 */

(function() {
  const navbar = document.getElementById('navbar');

  function initNavbar() {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    });
  }

  function initAnimations() {
    const observerOptions = {
      threshold: 0.06,
      rootMargin: '-40px 0px -40px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        const el = entry.target;
        if (entry.isIntersecting) {
          const parent = el.parentElement;
          const siblings = parent ? Array.from(parent.children).filter(c => c.hasAttribute('data-animate')) : [];
          const index = siblings.indexOf(el);
          const delay = Math.max(0, index) * 0.1;
          el.style.transitionDelay = delay + 's';
          el.classList.add('animated');
        } else {
          el.classList.remove('animated');
          el.style.transitionDelay = '0s';
        }
      });
    }, observerOptions);

    document.querySelectorAll('[data-animate]').forEach(el => observer.observe(el));
  }

  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href && href !== '#') {
          e.preventDefault();
          const target = document.querySelector(href);
          if (target) {
            const offset = 100;
            const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offset;
            window.scrollTo({ top: targetPosition, behavior: 'smooth' });
          }
        }
      });
    });
  }

  // Chart colors
  const tagColors = {
    '神佛': '#c44a4a',
    '征兆': '#d4a574',
    '妖怪': '#5a8a6a',
    '神兽': '#6a7a9a',
    '鬼怪': '#8a6a8a'
  };

  function renderTagChart(data) {
    const container = document.getElementById('tag-chart');
    if (!container) return;
    const max = Math.max(...data.map(d => d.count));
    data.forEach((d, i) => {
      const item = document.createElement('div');
      item.className = 'bar-item';
      const pct = (d.count / max * 100).toFixed(1);
      const color = tagColors[d.tag] || 'var(--accent)';
      item.innerHTML = `
        <span class="bar-label">${d.tag}</span>
        <div class="bar-track">
          <div class="bar-fill" style="width:0%;background:${color};opacity:0.75" data-width="${pct}%"></div>
        </div>
        <span class="bar-value">${d.count}</span>
      `;
      container.appendChild(item);
    });
    // Animate bars
    requestAnimationFrame(() => {
      container.querySelectorAll('.bar-fill').forEach((fill, i) => {
        setTimeout(() => {
          fill.style.width = fill.dataset.width;
        }, i * 120);
      });
    });
  }

  function renderVolumeChart(data) {
    const container = document.getElementById('volume-chart');
    if (!container) return;
    const max = Math.max(...data.map(d => d.count));
    data.slice(0, 12).forEach((d, i) => {
      const item = document.createElement('div');
      item.className = 'bar-item';
      const pct = (d.count / max * 100).toFixed(1);
      item.innerHTML = `
        <span class="bar-label">${d.volume.replace('卷', '')}</span>
        <div class="bar-track">
          <div class="bar-fill" style="width:0%;opacity:0.6" data-width="${pct}%"></div>
        </div>
        <span class="bar-value">${d.count}</span>
      `;
      container.appendChild(item);
    });
    requestAnimationFrame(() => {
      container.querySelectorAll('.bar-fill').forEach((fill, i) => {
        setTimeout(() => {
          fill.style.width = fill.dataset.width;
        }, i * 100);
      });
    });
  }

  function renderCooccurChart(data) {
    const container = document.getElementById('cooccur-chart');
    if (!container) return;
    const max = Math.max(...data.map(d => d.count));
    data.forEach((d, i) => {
      const item = document.createElement('div');
      item.className = 'bar-item';
      const pct = (d.count / max * 100).toFixed(1);
      const label = d.tags.join(' + ');
      item.innerHTML = `
        <span class="bar-label" style="min-width:120px">${label}</span>
        <div class="bar-track">
          <div class="bar-fill" style="width:0%;opacity:0.65" data-width="${pct}%"></div>
        </div>
        <span class="bar-value">${d.count}</span>
      `;
      container.appendChild(item);
    });
    requestAnimationFrame(() => {
      container.querySelectorAll('.bar-fill').forEach((fill, i) => {
        setTimeout(() => {
          fill.style.width = fill.dataset.width;
        }, i * 100);
      });
    });
  }

  function renderHeatmap(data) {
    const container = document.getElementById('heatmap-chart');
    if (!container) return;

    const tags = ['神佛', '征兆', '妖怪', '神兽', '鬼怪'];
    const volumes = [
      '卷二·玉格', '卷三·贝编', '卷八·梦', '卷十·物异',
      '卷十一·广知', '卷十二·语资', '卷十四·诺皋记上', '卷十五·诺皋记下',
      '卷十六·广动植之一', '卷十七·广动植之二'
    ];

    const maxVal = 30; // approximate max for scaling

    const heatmap = document.createElement('div');
    heatmap.className = 'heatmap';

    // Header row
    const headerRow = document.createElement('div');
    headerRow.className = 'heatmap-row';
    headerRow.innerHTML = '<div></div>' + tags.map(t => `<div class="heatmap-header">${t}</div>`).join('');
    heatmap.appendChild(headerRow);

    volumes.forEach(vol => {
      const row = document.createElement('div');
      row.className = 'heatmap-row';
      const volData = data[vol] || {};
      let cells = '';
      tags.forEach(tag => {
        const val = volData[tag] || 0;
        const opacity = Math.min(0.85, Math.max(0.08, val / maxVal));
        const color = tagColors[tag] || '#c44a4a';
        cells += `<div class="heatmap-cell" style="background:${color};opacity:${opacity}">${val}</div>`;
      });
      row.innerHTML = `<div class="heatmap-label">${vol}</div>${cells}`;
      heatmap.appendChild(row);
    });

    container.appendChild(heatmap);
  }

  async function loadData() {
    try {
      const res = await fetch('data/analysis_data.json');
      const data = await res.json();
      renderTagChart(data.tag_counts);
      renderVolumeChart(data.volume_counts);
      renderCooccurChart(data.co_occurrence);
      renderHeatmap(data.tag_by_volume);
    } catch (e) {
      console.error('Failed to load analysis data:', e);
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    initAnimations();
    initSmoothScroll();
    loadData();
  });
})();

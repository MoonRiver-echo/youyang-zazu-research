/**
 * text-analysis.js — 文本分析页面图表
 */

(function() {
  const tagColors = {
    '神佛': '#8b0000',
    '征兆': '#b35900',
    '妖怪': '#2e7d32',
    '神兽': '#1565c0',
    '鬼怪': '#7b1fa2'
  };

  function renderBarChart(containerId, data, options = {}) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const max = Math.max(...data.map(d => d.value));
    const isHorizontal = options.horizontal;
    const colorMap = options.colorMap || {};

    data.forEach((d, i) => {
      const item = document.createElement('div');
      item.className = 'ac-bar-item';
      const pct = (d.value / max * 100).toFixed(1);
      const color = colorMap[d.label] || '#8b0000';
      const labelWidth = isHorizontal ? '140px' : '100px';
      item.style.gridTemplateColumns = `${labelWidth} 1fr 50px`;

      item.innerHTML = `
        <span class="bar-label">${d.label}</span>
        <div class="bar-track">
          <div class="bar-fill" style="width:0%;background:${color};opacity:0.75" data-width="${pct}%"></div>
        </div>
        <span class="bar-value-outside">${d.value}</span>
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

  async function loadData() {
    try {
      const res = await fetch('data/analysis_data.json');
      const data = await res.json();

      // Tag chart
      const tagData = data.tag_counts.map(t => ({
        label: t.tag,
        value: t.count
      }));
      renderBarChart('tag-chart', tagData, { colorMap: tagColors });

      // Volume chart
      const volData = data.volume_counts.slice(0, 12).map(v => ({
        label: v.volume.replace('卷', ''),
        value: v.count
      }));
      renderBarChart('volume-chart', volData, { horizontal: true });

      // Cooccur chart
      const coData = data.co_occurrence.slice(0, 10).map(c => ({
        label: c.tags.join('+'),
        value: c.count
      }));
      renderBarChart('cooccur-chart', coData, { horizontal: true });

    } catch (e) {
      console.error('Failed to load analysis data:', e);
    }
  }

  document.addEventListener('DOMContentLoaded', loadData);
})();

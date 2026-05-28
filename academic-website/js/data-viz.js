/**
 * data-viz.js — 数据可视化页面图表
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

  function renderHeatmap(data) {
    const container = document.getElementById('heatmap-container');
    if (!container) return;

    const tags = ['神佛', '征兆', '妖怪', '神兽', '鬼怪'];
    const volumes = [
      '卷二·玉格', '卷三·贝编', '卷八·梦', '卷十·物异',
      '卷十一·广知', '卷十二·语资', '卷十四·诺皋记上', '卷十五·诺皋记下',
      '卷十六·广动植之一', '卷十七·广动植之二'
    ];
    const maxVal = 30;

    const heatmap = document.createElement('div');
    heatmap.className = 'heatmap-grid';

    // Header row
    const headerRow = document.createElement('div');
    headerRow.className = 'heatmap-header-row';
    headerRow.innerHTML = '<div></div>' + tags.map(t => `<div class="heatmap-h-label">${t}</div>`).join('');
    heatmap.appendChild(headerRow);

    volumes.forEach(vol => {
      const row = document.createElement('div');
      row.className = 'heatmap-row';
      const volData = data[vol] || {};
      let cells = '';
      tags.forEach(tag => {
        const val = volData[tag] || 0;
        const opacity = Math.min(0.85, Math.max(0.08, val / maxVal));
        const color = tagColors[tag] || '#8b0000';
        cells += `<div class="heatmap-cell" style="background:${color};opacity:${opacity}">${val}<span class="tooltip">${vol} · ${tag}: ${val}</span></div>`;
      });
      row.innerHTML = `<div class="heatmap-v-label">${vol}</div>${cells}`;
      heatmap.appendChild(row);
    });

    container.appendChild(heatmap);
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
      renderBarChart('tag-bar-chart', tagData, { colorMap: tagColors });

      // Volume chart
      const volData = data.volume_counts.slice(0, 12).map(v => ({
        label: v.volume.replace('卷', ''),
        value: v.count
      }));
      renderBarChart('volume-bar-chart', volData, { horizontal: true });

      // Cooccur chart
      const coData = data.co_occurrence.slice(0, 10).map(c => ({
        label: c.tags.join('+'),
        value: c.count
      }));
      renderBarChart('cooccur-bar-chart', coData, { horizontal: true });

      // Heatmap
      renderHeatmap(data.tag_by_volume);

    } catch (e) {
      console.error('Failed to load analysis data:', e);
    }
  }

  document.addEventListener('DOMContentLoaded', loadData);
})();

/**
 * visualization.js — 图表可视化辅助工具
 */

const Visualization = (function() {
    const colorPalette = [
        '#c53d43', '#c9a959', '#3d7a7a', '#8b5a2b',
        '#5a7a9a', '#7a5a8a', '#9a7a5a', '#5a9a7a',
        '#b05a5a', '#5a5ab0', '#b08a3a', '#3a8ab0'
    ];

    function getColors(count) {
        const colors = [];
        for (let i = 0; i < count; i++) {
            colors.push(colorPalette[i % colorPalette.length]);
        }
        return colors;
    }

    function countBy(data, key) {
        const map = {};
        data.forEach(item => {
            const val = item[key] || '未知';
            map[val] = (map[val] || 0) + 1;
        });
        return Object.entries(map)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 12);
    }

    function groupByPeriod(data, periodKey) {
        const map = {};
        data.forEach(item => {
            let period = item[periodKey] || '未知';
            // Try to extract dynasty/period info
            if (!period || period === '未知') {
                const src = item.source || item.description || '';
                const dynasties = ['先秦', '秦', '汉', '魏晋', '南北朝', '隋', '唐', '宋', '元', '明', '清'];
                for (const d of dynasties) {
                    if (src.includes(d)) {
                        period = d;
                        break;
                    }
                }
            }
            map[period] = (map[period] || 0) + 1;
        });
        // Custom sort for dynasties
        const dynastyOrder = ['先秦', '秦', '汉', '魏晋', '南北朝', '隋', '唐', '宋', '元', '明', '清', '未知'];
        return Object.entries(map).sort((a, b) => {
            const idxA = dynastyOrder.indexOf(a[0]);
            const idxB = dynastyOrder.indexOf(b[0]);
            if (idxA >= 0 && idxB >= 0) return idxA - idxB;
            if (idxA >= 0) return -1;
            if (idxB >= 0) return 1;
            return b[1] - a[1];
        });
    }

    function createDoughnutChart(canvasId, data, labels) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        const colors = getColors(labels.length);
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderColor: '#fafaf8',
                    borderWidth: 2,
                    hoverOffset: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            font: { family: "'Noto Sans SC', sans-serif", size: 12 },
                            color: '#4a4a4a',
                            padding: 16,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        backgroundColor: '#2c2c2c',
                        titleFont: { family: "'Noto Serif SC', serif", size: 13 },
                        bodyFont: { family: "'Noto Sans SC', sans-serif", size: 12 },
                        padding: 12,
                        cornerRadius: 6,
                        displayColors: true,
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const pct = ((context.raw / total) * 100).toFixed(1);
                                return `${context.label}: ${context.raw} (${pct}%)`;
                            }
                        }
                    }
                },
                cutout: '58%',
                animation: {
                    animateRotate: true,
                    duration: 900,
                    easing: 'easeOutQuart'
                }
            }
        });
    }

    function createBarChart(canvasId, data, labels) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        const colors = getColors(labels.length);
        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: '数量',
                    data: data,
                    backgroundColor: colors,
                    borderRadius: 4,
                    borderSkipped: false,
                    barPercentage: 0.65
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#2c2c2c',
                        titleFont: { family: "'Noto Serif SC', serif", size: 13 },
                        bodyFont: { family: "'Noto Sans SC', sans-serif", size: 12 },
                        padding: 12,
                        cornerRadius: 6
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: {
                            font: { family: "'Noto Sans SC', sans-serif", size: 11 },
                            color: '#888888',
                            maxRotation: 45,
                            minRotation: 0
                        }
                    },
                    y: {
                        grid: { color: '#e8e2d4', drawBorder: false },
                        ticks: {
                            font: { family: "'Noto Sans SC', sans-serif", size: 11 },
                            color: '#888888',
                            padding: 8
                        },
                        border: { display: false }
                    }
                },
                animation: {
                    duration: 900,
                    easing: 'easeOutQuart'
                }
            }
        });
    }

    return {
        countBy,
        groupByPeriod,
        createDoughnutChart,
        createBarChart,
        getColors
    };
})();

/**
 * culture-layer.js — 文化关联层
 */

const CultureLayer = (function() {
    let categoryChart = null;
    let timelineChart = null;
    let dataStore = [];

    function init() {
        // Category cards click -> filter entries
        document.querySelectorAll('.category-card').forEach(card => {
            card.addEventListener('click', () => {
                const cat = card.dataset.cat;
                const mapping = {
                    religion: '宗教',
                    supernatural: '神怪',
                    folklore: '民俗',
                    geography: '地理',
                    products: '物产',
                    rituals: '仪式'
                };
                const target = mapping[cat] || cat;

                // Switch to entries tab and filter
                const entriesTab = document.querySelector('.nav-tab[data-layer="entries"]');
                if (entriesTab) entriesTab.click();

                const filterSelect = document.getElementById('entries-filter');
                if (filterSelect) {
                    let found = false;
                    for (let i = 0; i < filterSelect.options.length; i++) {
                        if (filterSelect.options[i].value === target) {
                            filterSelect.selectedIndex = i;
                            found = true;
                            break;
                        }
                    }
                    if (found && typeof EntriesLayer !== 'undefined') {
                        // Trigger update via simulated change or direct call
                        filterSelect.dispatchEvent(new Event('change'));
                    }
                }
            });
        });
    }

    function update(data) {
        dataStore = data;

        const hasCategory = data.some(d => d.category || d.culture_type);
        const hasPeriod = data.some(d => d.period);

        if (!hasCategory && !hasPeriod) {
            document.getElementById('culture-empty').classList.add('visible');
            document.querySelector('.culture-layout').style.display = 'none';
            return;
        }

        document.getElementById('culture-empty').classList.remove('visible');
        document.querySelector('.culture-layout').style.display = 'grid';

        updateCategoryChart();
        updateTimelineChart();
        updateCategoryCounts();
    }

    function updateCategoryChart() {
        const counts = Visualization.countBy(dataStore, 'category');
        if (counts.length === 0) {
            if (categoryChart) { categoryChart.destroy(); categoryChart = null; }
            return;
        }

        if (categoryChart) categoryChart.destroy();
        categoryChart = Visualization.createDoughnutChart(
            'category-chart',
            counts.map(c => c[1]),
            counts.map(c => c[0])
        );
    }

    function updateTimelineChart() {
        const counts = Visualization.groupByPeriod(dataStore, 'period');
        if (counts.length === 0) {
            if (timelineChart) { timelineChart.destroy(); timelineChart = null; }
            return;
        }

        if (timelineChart) timelineChart.destroy();
        timelineChart = Visualization.createBarChart(
            'timeline-chart',
            counts.map(c => c[1]),
            counts.map(c => c[0])
        );
    }

    function updateCategoryCounts() {
        const counts = {};
        dataStore.forEach(item => {
            const cat = item.category || '未知';
            counts[cat] = (counts[cat] || 0) + 1;
        });

        const mapping = {
            '宗教': 'count-religion',
            '神怪': 'count-supernatural',
            '民俗': 'count-folklore',
            '地理': 'count-geography',
            '物产': 'count-products',
            '仪式': 'count-rituals'
        };

        Object.keys(mapping).forEach(key => {
            const el = document.getElementById(mapping[key]);
            if (el) el.textContent = counts[key] || 0;
        });
    }

    return { init, update };
})();

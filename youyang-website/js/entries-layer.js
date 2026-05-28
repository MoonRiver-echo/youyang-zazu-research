/**
 * entries-layer.js — 条目浏览层
 */

const EntriesLayer = (function() {
    let dataStore = [];
    let filteredData = [];
    let currentPage = 1;
    const pageSize = 12;

    function init() {
        const searchInput = document.getElementById('entries-search');
        const filterSelect = document.getElementById('entries-filter');

        searchInput.addEventListener('input', debounce(() => {
            currentPage = 1;
            applyFilters();
        }, 250));

        filterSelect.addEventListener('change', () => {
            currentPage = 1;
            applyFilters();
        });
    }

    function update(data) {
        dataStore = data;
        populateCategoryFilter();
        applyFilters();
    }

    function populateCategoryFilter() {
        const select = document.getElementById('entries-filter');
        const categories = new Set();
        dataStore.forEach(item => {
            if (item.category) categories.add(item.category);
        });

        // Keep first option (all categories)
        const firstOption = select.options[0];
        select.innerHTML = '';
        select.appendChild(firstOption);

        Array.from(categories).sort().forEach(cat => {
            const opt = document.createElement('option');
            opt.value = cat;
            opt.textContent = cat;
            select.appendChild(opt);
        });
    }

    function applyFilters() {
        const query = document.getElementById('entries-search').value.trim().toLowerCase();
        const category = document.getElementById('entries-filter').value;

        filteredData = dataStore.filter(item => {
            const matchesQuery = !query ||
                (item.name && item.name.toLowerCase().includes(query)) ||
                (item.title && item.title.toLowerCase().includes(query)) ||
                (item.description && item.description.toLowerCase().includes(query));
            const matchesCategory = !category || item.category === category;
            return matchesQuery && matchesCategory;
        });

        render();
    }

    function render() {
        const grid = document.getElementById('entries-grid');
        const empty = document.getElementById('entries-empty');
        const countEl = document.getElementById('entries-count');

        countEl.textContent = I18n.t('entries.count', { count: filteredData.length });

        if (filteredData.length === 0) {
            grid.innerHTML = '';
            grid.style.display = 'none';
            empty.classList.add('visible');
            document.getElementById('entries-pagination').innerHTML = '';
            return;
        }

        grid.style.display = 'grid';
        empty.classList.remove('visible');

        const start = (currentPage - 1) * pageSize;
        const end = start + pageSize;
        const pageData = filteredData.slice(start, end);

        grid.innerHTML = pageData.map(item => createCard(item)).join('');
        renderPagination();
    }

    function createCard(item) {
        const name = escapeHtml(item.name || item.title || '未命名');
        const category = escapeHtml(item.category || '未知');
        const desc = escapeHtml(truncate(item.description || '', 140));
        const source = escapeHtml(item.source || '');

        return `
            <div class="entry-card">
                <div class="entry-card-title">${name}</div>
                <div class="entry-card-category">${category}</div>
                ${desc ? `<div class="entry-card-desc">${desc}</div>` : ''}
                ${source ? `<div class="entry-card-source">来源：${source}</div>` : ''}
            </div>
        `;
    }

    function renderPagination() {
        const container = document.getElementById('entries-pagination');
        const totalPages = Math.ceil(filteredData.length / pageSize);

        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }

        let html = '';
        // Prev
        html += `<button class="page-btn" ${currentPage === 1 ? 'disabled' : ''} data-page="prev">←</button>`;

        const maxVisible = 5;
        let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
        let endPage = Math.min(totalPages, startPage + maxVisible - 1);
        if (endPage - startPage < maxVisible - 1) {
            startPage = Math.max(1, endPage - maxVisible + 1);
        }

        if (startPage > 1) {
            html += `<button class="page-btn" data-page="1">1</button>`;
            if (startPage > 2) html += `<span class="page-btn" disabled>…</span>`;
        }

        for (let i = startPage; i <= endPage; i++) {
            html += `<button class="page-btn ${i === currentPage ? 'active' : ''}" data-page="${i}">${i}</button>`;
        }

        if (endPage < totalPages) {
            if (endPage < totalPages - 1) html += `<span class="page-btn" disabled>…</span>`;
            html += `<button class="page-btn" data-page="${totalPages}">${totalPages}</button>`;
        }

        // Next
        html += `<button class="page-btn" ${currentPage === totalPages ? 'disabled' : ''} data-page="next">→</button>`;

        container.innerHTML = html;

        container.querySelectorAll('button[data-page]').forEach(btn => {
            btn.addEventListener('click', () => {
                const page = btn.dataset.page;
                if (page === 'prev') {
                    if (currentPage > 1) currentPage--;
                } else if (page === 'next') {
                    if (currentPage < totalPages) currentPage++;
                } else {
                    currentPage = parseInt(page, 10);
                }
                render();
                document.getElementById('layer-entries').scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
        });
    }

    function debounce(fn, delay) {
        let timer;
        return function(...args) {
            clearTimeout(timer);
            timer = setTimeout(() => fn.apply(this, args), delay);
        };
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function truncate(str, len) {
        if (!str) return '';
        return str.length > len ? str.substring(0, len) + '…' : str;
    }

    return { init, update };
})();

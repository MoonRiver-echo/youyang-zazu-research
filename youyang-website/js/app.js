/**
 * app.js — 酉阳杂俎 · 神怪志异
 * 双向动画版：进入视口正向播放，离开视口反向播放
 */

(function() {
  // Data storage
  let allEntries = [];
  let featuredEntries = [];
  let currentFilter = 'all';
  let currentQuery = '';
  let displayedCount = 0;
  const PAGE_SIZE = 12;

  // DOM refs
  const navbar = document.getElementById('navbar');
  const searchInput = document.getElementById('search-input');
  const searchBtn = document.getElementById('search-btn');
  const resultsGrid = document.getElementById('results-grid');
  const resultsCount = document.getElementById('results-count');
  const loadMoreBtn = document.getElementById('load-more-btn');
  const filterTags = document.querySelectorAll('.filter-tag');
  const modal = document.getElementById('story-modal');
  const modalBackdrop = modal.querySelector('.modal-backdrop');
  const modalClose = modal.querySelector('.modal-close');
  const modalTitle = document.getElementById('modal-title');
  const modalText = document.getElementById('modal-text');
  const modalTag = document.getElementById('modal-tag');
  const modalMeta = document.getElementById('modal-meta');
  const storyBtns = document.querySelectorAll('.story-btn');
  const sectionArrows = document.querySelectorAll('.section-arrow');

  // ===================== LOAD DATA =====================
  async function loadData() {
    try {
      const res = await fetch('data/entries.json');
      const data = await res.json();
      allEntries = data.entries || [];
      featuredEntries = data.featured || [];
      renderResults(true);
    } catch (e) {
      console.error('Failed to load entries:', e);
      resultsCount.textContent = '数据加载失败';
    }
  }

  // ===================== BIDIRECTIONAL ANIMATION =====================
  function initAnimations() {
    const observerOptions = {
      threshold: 0.06,
      rootMargin: '-40px 0px -40px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        const el = entry.target;
        if (entry.isIntersecting) {
          // Element enters viewport — play forward
          // Stagger by sibling index
          const parent = el.parentElement;
          const siblings = parent ? Array.from(parent.children).filter(c => c.hasAttribute('data-animate')) : [];
          const index = siblings.indexOf(el);
          const delay = Math.max(0, index) * 0.1;
          el.style.transitionDelay = delay + 's';
          el.classList.add('animated');
        } else {
          // Element leaves viewport — reverse animation by removing class
          el.classList.remove('animated');
          el.style.transitionDelay = '0s';
        }
      });
    }, observerOptions);

    // Observe all elements with data-animate
    document.querySelectorAll('[data-animate]').forEach(el => observer.observe(el));
  }

  // Also apply observer to dynamically added result cards
  function observeCard(card) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animated');
        } else {
          entry.target.classList.remove('animated');
        }
      });
    }, { threshold: 0.08, rootMargin: '-30px 0px' });
    observer.observe(card);
  }

  // ===================== NAVBAR SCROLL =====================
  function initNavbar() {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    });
  }

  // ===================== SMOOTH SECTION SCROLL =====================
  function initSectionArrows() {
    sectionArrows.forEach(arrow => {
      arrow.addEventListener('click', (e) => {
        e.preventDefault();
        const href = arrow.getAttribute('href');
        if (href) {
          const target = document.querySelector(href);
          if (target) smoothScrollTo(target);
        }
      });
    });
  }

  function smoothScrollTo(target) {
    const targetPosition = target.getBoundingClientRect().top + window.pageYOffset;
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition;
    const duration = 1000;
    let start = null;

    function step(timestamp) {
      if (!start) start = timestamp;
      const progress = timestamp - start;
      const ease = easeInOutCubic(Math.min(progress / duration, 1));
      window.scrollTo(0, startPosition + distance * ease);
      if (progress < duration) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  function easeInOutCubic(t) {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  }

  // ===================== FILTER & SEARCH =====================
  function getFilteredEntries() {
    let list = allEntries;
    if (currentFilter !== 'all') {
      list = list.filter(e => e.tags && e.tags.includes(currentFilter));
    }
    if (currentQuery.trim()) {
      const q = currentQuery.toLowerCase();
      list = list.filter(e =>
        (e.text && e.text.toLowerCase().includes(q)) ||
        (e.title && e.title.toLowerCase().includes(q)) ||
        (e.volume && e.volume.toLowerCase().includes(q))
      );
    }
    return list;
  }

  function renderResults(reset = false) {
    const list = getFilteredEntries();
    if (reset) displayedCount = 0;
    const toShow = list.slice(displayedCount, displayedCount + PAGE_SIZE);

    if (reset) resultsGrid.innerHTML = '';

    toShow.forEach((item, idx) => {
      const card = document.createElement('div');
      card.className = 'result-card';
      card.setAttribute('data-animate', 'fade-up');
      card.innerHTML = `
        <div class="result-volume">${escapeHtml(item.volume || '')}</div>
        <div class="result-title">${escapeHtml(item.title || '')}</div>
        <div class="result-text">${escapeHtml(item.text || '')}</div>
        <div class="result-tags">
          ${(item.tags || []).map(t => `<span class="result-tag">${escapeHtml(t)}</span>`).join('')}
        </div>
      `;
      card.addEventListener('click', () => openModal(item));
      resultsGrid.appendChild(card);
      observeCard(card);
    });

    displayedCount += toShow.length;
    resultsCount.textContent = list.length > 0 ? `共 ${list.length} 条结果` : '未找到相关条目';

    if (displayedCount >= list.length) {
      loadMoreBtn.classList.add('hidden');
    } else {
      loadMoreBtn.classList.remove('hidden');
    }
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // ===================== EVENT LISTENERS =====================
  searchInput.addEventListener('input', debounce(() => {
    currentQuery = searchInput.value;
    renderResults(true);
  }, 300));

  searchBtn.addEventListener('click', () => {
    currentQuery = searchInput.value;
    renderResults(true);
  });

  searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      currentQuery = searchInput.value;
      renderResults(true);
    }
  });

  filterTags.forEach(btn => {
    btn.addEventListener('click', () => {
      filterTags.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilter = btn.dataset.filter;
      renderResults(true);
    });
  });

  loadMoreBtn.addEventListener('click', () => renderResults(false));

  // ===================== MODAL =====================
  function openModal(item) {
    modalTitle.textContent = item.title || item.story_name || '无标题';
    modalText.innerHTML = formatText(item.text || '');
    modalTag.textContent = item.volume || '';
    modalMeta.innerHTML = `标签：${(item.tags || []).join('、')} · 编号：${item.id || ''}`;

    modal.classList.add('visible');
    document.body.style.overflow = 'hidden';

    // Animate modal content elements staggered
    const modalElements = modal.querySelectorAll('.modal-tag, .modal-content h2, .modal-text, .modal-meta');
    modalElements.forEach((el, i) => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(20px)';
      el.style.transition = `opacity 0.5s ease ${0.12 * i}s, transform 0.5s ease ${0.12 * i}s`;
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          el.style.opacity = '1';
          el.style.transform = 'translateY(0)';
        });
      });
    });
  }

  function closeModal() {
    modal.classList.remove('visible');
    document.body.style.overflow = '';
  }

  function formatText(text) {
    return escapeHtml(text)
      .replace(/\n/g, '<br>')
      .replace(/「([^」]+)」/g, '<span style="color:var(--text);font-weight:500;">「$1」</span>');
  }

  modalClose.addEventListener('click', closeModal);
  modalBackdrop.addEventListener('click', closeModal);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
  });

  // ===================== FEATURED STORY BUTTONS =====================
  storyBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const name = btn.dataset.story;
      const item = featuredEntries.find(f => f.story_name === name);
      if (item) {
        openModal({
          title: item.story_name,
          text: item.story_quote + '\n\n' + item.text,
          volume: item.volume,
          tags: item.tags,
          id: item.id
        });
      }
    });
  });

  // ===================== SMOOTH NAV LINKS =====================
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href && href !== '#') {
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) smoothScrollTo(target);
      }
    });
  });

  // ===================== UTILITIES =====================
  function debounce(fn, delay) {
    let timer;
    return function(...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), delay);
    };
  }

  // ===================== INIT =====================
  document.addEventListener('DOMContentLoaded', () => {
    initAnimations();
    initNavbar();
    initSectionArrows();
    loadData();
  });
})();

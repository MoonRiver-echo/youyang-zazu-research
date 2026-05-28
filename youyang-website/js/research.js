/**
 * research.js — 研究页面通用脚本
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

  document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    initAnimations();
    initSmoothScroll();
  });
})();

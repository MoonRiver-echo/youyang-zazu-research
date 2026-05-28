/**
 * academic.js — 学术网站通用脚本
 */

(function() {
  const navbar = document.querySelector('.site-header');

  // Navbar scroll effect
  function initNavbar() {
    if (!navbar) return;
    window.addEventListener('scroll', () => {
      if (window.scrollY > 20) {
        navbar.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)';
      } else {
        navbar.style.boxShadow = 'none';
      }
    });
  }

  // Smooth scroll for sidebar nav
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
            // Update active state in sidebar
            document.querySelectorAll('.sidebar-nav a').forEach(a => a.classList.remove('active'));
            this.classList.add('active');
          }
        }
      });
    });
  }

  // Collapsible sections
  function initCollapsible() {
    document.querySelectorAll('.collapsible-header').forEach(header => {
      header.addEventListener('click', () => {
        const collapsible = header.parentElement;
        collapsible.classList.toggle('open');
      });
    });
  }

  // Highlight sidebar on scroll
  function initScrollSpy() {
    const sections = document.querySelectorAll('.content-section[id]');
    const sidebarLinks = document.querySelectorAll('.sidebar-nav a[href^="#"]');
    if (!sections.length || !sidebarLinks.length) return;

    const observerOptions = {
      rootMargin: '-120px 0px -60% 0px',
      threshold: 0
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          sidebarLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + entry.target.id) {
              link.classList.add('active');
            }
          });
        }
      });
    }, observerOptions);

    sections.forEach(section => observer.observe(section));
  }

  document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    initSmoothScroll();
    initCollapsible();
    initScrollSpy();
  });
})();

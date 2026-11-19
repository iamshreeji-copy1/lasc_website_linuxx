/**
* Template Name: Impact (BootstrapMade) – customised for SATs
* Template URL: https://bootstrapmade.com/impact-bootstrap-business-website-template/
* Author: BootstrapMade.com
* License: https://bootstrapmade.com/license/
*
* SATs changes: guarded vendor calls (works on pages that load fewer libraries), fixed the
* scroll-to-top handler, rAF-throttled passive scroll work, Swiper loop only when it has enough
* slides, keyboard-accessible toggles/filters, reduced-motion support, scroll progress bar.
*/

document.addEventListener('DOMContentLoaded', () => {
  "use strict";

  const reduceMotion = document.documentElement.getAttribute('data-motion') === 'reduced' || (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);

  /**
   * Preloader – hide as soon as the page has loaded, but never block longer than 2.5s
   */
  const preloader = document.querySelector('#preloader');
  if (preloader) {
    let done = false;
    const hidePreloader = () => {
      if (done) return;
      done = true;
      preloader.classList.add('is-hidden');
      setTimeout(() => preloader.remove(), 450);
    };
    if (document.readyState === 'complete') hidePreloader();
    else window.addEventListener('load', hidePreloader);
    setTimeout(hidePreloader, 2500);
  }

  /**
   * One rAF-throttled, passive scroll loop for everything that reacts to scrolling
   */
  const scrollTasks = [];
  let ticking = false;
  const onScroll = () => {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(() => {
      scrollTasks.forEach(fn => fn());
      ticking = false;
    });
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll, { passive: true });
  window.addEventListener('load', onScroll);

  /**
   * Sticky header (header keeps its height, so nothing jumps when it sticks)
   */
  const selectHeader = document.querySelector('#header');
  if (selectHeader) {
    const headerOffset = selectHeader.offsetTop;
    const nextElement = selectHeader.nextElementSibling;
    scrollTasks.push(() => {
      const stuck = window.scrollY >= headerOffset;
      selectHeader.classList.toggle('sticked', stuck);
      if (nextElement) nextElement.classList.toggle('sticked-header-offset', stuck);
    });
  }

  /**
   * Scroll progress bar
   */
  const bar = document.createElement('div');
  bar.className = 'scroll-progress';
  bar.setAttribute('aria-hidden', 'true');
  document.body.appendChild(bar);
  scrollTasks.push(() => {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    bar.style.transform = 'scaleX(' + (max > 0 ? Math.min(1, window.scrollY / max) : 0) + ')';
  });

  /**
   * Navbar links active state on scroll (only for in-page section links)
   */
  const navbarlinks = Array.from(document.querySelectorAll('#navbar a')).filter(link => {
    if (!link.hash || link.classList.contains('getstarted')) return false;
    const samePage = !link.pathname || link.pathname === window.location.pathname ||
      (link.pathname.endsWith('/index.html') && /\/$|\/index\.html$/.test(window.location.pathname));
    return samePage && document.querySelector(link.hash);
  });
  if (navbarlinks.length) {
    scrollTasks.push(() => {
      const position = window.scrollY + 200;
      navbarlinks.forEach(link => {
        const section = document.querySelector(link.hash);
        if (!section) return;
        const inside = position >= section.offsetTop && position <= (section.offsetTop + section.offsetHeight);
        link.classList.toggle('active', inside);
      });
    });
  }

  /**
   * Mobile nav toggle (click + keyboard + Esc)
   */
  const mobileNavShow = document.querySelector('.mobile-nav-show');
  const mobileNavHide = document.querySelector('.mobile-nav-hide');

  function mobileNavToggle() {
    if (!mobileNavShow || !mobileNavHide) return;
    const open = document.body.classList.toggle('mobile-nav-active');
    mobileNavShow.classList.toggle('d-none', open);
    mobileNavHide.classList.toggle('d-none', !open);
    mobileNavShow.setAttribute('aria-expanded', String(open));
  }

  document.querySelectorAll('.mobile-nav-toggle').forEach(el => {
    el.addEventListener('click', event => {
      event.preventDefault();
      mobileNavToggle();
    });
    el.addEventListener('keydown', event => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        mobileNavToggle();
      }
    });
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && document.body.classList.contains('mobile-nav-active')) mobileNavToggle();
  });
  document.querySelectorAll('#navbar a').forEach(link => {
    link.addEventListener('click', () => {
      if (document.body.classList.contains('mobile-nav-active')) mobileNavToggle();
    });
  });

  /**
   * Lightbox
   */
  if (typeof GLightbox === 'function') {
    GLightbox({ selector: '.glightbox' });
  }

  /**
   * Scroll top button
   */
  const scrollTop = document.querySelector('.scroll-top');
  if (scrollTop) {
    scrollTasks.push(() => scrollTop.classList.toggle('active', window.scrollY > 100));
    scrollTop.addEventListener('click', event => {
      event.preventDefault();
      window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
    });
  }

  /**
   * Counters
   */
  if (typeof PureCounter === 'function' && document.querySelector('.purecounter')) {
    new PureCounter();
  }

  /**
   * Swipers – loop/autoplay only when there are enough slides to make it meaningful
   */
  function initSwiper(el, options) {
    if (typeof Swiper !== 'function') return null;
    const slides = el.querySelectorAll('.swiper-slide').length;
    const pagination = el.querySelector('.swiper-pagination');
    const config = Object.assign({ speed: 600 }, options);
    if (pagination) config.pagination = { el: pagination, type: 'bullets', clickable: true };
    const wanted = typeof config.minSlidesForLoop === 'number' ? config.minSlidesForLoop : 2;
    delete config.minSlidesForLoop;
    const canLoop = slides >= wanted;
    config.loop = !!config.loop && canLoop;
    if (!canLoop || reduceMotion) config.autoplay = false;
    if (slides <= 1) {
      el.querySelectorAll('.swiper-button-next, .swiper-button-prev, .swiper-pagination').forEach(n => { n.style.display = 'none'; });
      config.allowTouchMove = false;
    } else if (el.querySelector('.swiper-button-next')) {
      config.navigation = {
        nextEl: el.querySelector('.swiper-button-next'),
        prevEl: el.querySelector('.swiper-button-prev')
      };
    }
    return new Swiper(el, config);
  }

  document.querySelectorAll('.clients-slider').forEach(el => initSwiper(el, {
    speed: 500,
    loop: true,
    minSlidesForLoop: 8,
    autoplay: { delay: 3500, disableOnInteraction: false, pauseOnMouseEnter: true },
    slidesPerView: 2,
    spaceBetween: 24,
    breakpoints: {
      480: { slidesPerView: 3, spaceBetween: 32 },
      640: { slidesPerView: 4, spaceBetween: 40 },
      992: { slidesPerView: 6, spaceBetween: 48 }
    }
  }));

  document.querySelectorAll('.slides-1').forEach(el => initSwiper(el, {
    speed: 600,
    loop: true,
    autoplay: { delay: 5000, disableOnInteraction: true, pauseOnMouseEnter: true },
    slidesPerView: 1,
    a11y: { enabled: true }
  }));

  document.querySelectorAll('.slides-3').forEach(el => initSwiper(el, {
    speed: 600,
    loop: true,
    minSlidesForLoop: 4,
    autoplay: { delay: 6000, disableOnInteraction: false, pauseOnMouseEnter: true },
    rewind: true,
    slidesPerView: 1,
    spaceBetween: 24,
    breakpoints: {
      768: { slidesPerView: 2 },
      1200: { slidesPerView: 3 }
    }
  }));

  /**
   * Products – Isotope filter (keyboard accessible)
   */
  const portfolioIsotope = document.querySelector('.portfolio-isotope');
  if (portfolioIsotope && typeof Isotope === 'function') {
    const layout = portfolioIsotope.getAttribute('data-portfolio-layout') || 'fitRows';
    const sort = portfolioIsotope.getAttribute('data-portfolio-sort') || 'original-order';
    const initialFilter = portfolioIsotope.getAttribute('data-portfolio-filter') || '*';

    window.addEventListener('load', () => {
      const iso = new Isotope(document.querySelector('.portfolio-container'), {
        itemSelector: '.portfolio-item',
        layoutMode: layout,
        filter: initialFilter,
        sortBy: sort,
        transitionDuration: reduceMotion ? 0 : '0.45s'
      });

      const filters = portfolioIsotope.querySelectorAll('.portfolio-flters li');
      const qInput = document.getElementById('product-q');
      const countEl = document.getElementById('product-count');
      const emptyEl = document.getElementById('product-empty');
      const items = Array.from(portfolioIsotope.querySelectorAll('.portfolio-item'));
      const state = { cat: initialFilter, q: '' };
      const extra = {};          // full specification wording per product, loaded on the first search
      let extraLoaded = false;
      const blob = el => (el.getAttribute('data-search') || '') + ' ' + (extra[el.getAttribute('data-key')] || '');
      const matches = el => (state.cat === '*' || el.matches(state.cat)) &&
        (!state.q || state.q.split(/\s+/).every(w => blob(el).indexOf(w) !== -1));
      const loadExtra = () => {
        if (extraLoaded || !(window.SATS && window.SATS.products)) return;
        extraLoaded = true;
        window.SATS.products().then(list => { list.forEach(p => { extra[p.key] = (p.text || '').toLowerCase(); }); refresh(); }).catch(() => {});
      };
      const refresh = () => {
        iso.arrange({ filter: function (itemElem) { return matches(itemElem); } });
        const n = items.filter(matches).length;
        if (countEl) countEl.textContent = n + (n === 1 ? ' product' : ' products');
        if (emptyEl) emptyEl.hidden = n !== 0;
        if (typeof AOS !== 'undefined') setTimeout(() => AOS.refresh(), 500);
      };
      const apply = el => {
        const current = portfolioIsotope.querySelector('.portfolio-flters .filter-active');
        if (current) { current.classList.remove('filter-active'); current.setAttribute('aria-pressed', 'false'); }
        el.classList.add('filter-active');
        el.setAttribute('aria-pressed', 'true');
        state.cat = el.getAttribute('data-filter');
        refresh();
      };
      filters.forEach(el => {
        el.addEventListener('click', () => apply(el));
        el.addEventListener('keydown', event => {
          if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); apply(el); }
        });
      });
      if (qInput) {
        let timer;
        qInput.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(() => { state.q = qInput.value.trim().toLowerCase(); if (state.q) loadExtra(); refresh(); }, 120); });
      }
      const reset = document.getElementById('product-reset');
      if (reset) reset.addEventListener('click', () => { if (qInput) qInput.value = ''; state.q = ''; apply(filters[0]); qInput && qInput.focus(); });
    });
  }

  /**
   * Animation on scroll – if the library is missing, never leave content hidden
   */
  const initAOS = () => {
    if (typeof AOS === 'undefined') {
      document.querySelectorAll('[data-aos]').forEach(el => el.removeAttribute('data-aos'));
      return;
    }
    AOS.init({
      duration: 700,
      easing: 'ease-out-cubic',
      once: true,
      mirror: false,
      offset: 60,
      disable: () => reduceMotion
    });
  };
  if (document.readyState === 'complete') initAOS();
  else window.addEventListener('load', initAOS);

});

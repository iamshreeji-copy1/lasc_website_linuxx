/**
 * SATs v2 – product page interactions (no dependencies):
 * sticky section tabs with scroll-spy · count-up stats · specification search + cards/table view · range explorer.
 */
(function () {
  'use strict';
  var root = document.documentElement;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var reduced = function () { return root.getAttribute('data-motion') === 'reduced'; };

  /* ---------------------------------------------------- tabs + scroll-spy */
  var tabs = $$('.pd-tabs a');
  if (tabs.length) {
    var targets = tabs.map(function (a) { return document.querySelector(a.getAttribute('href')); });
    var list = $('.pd-tabs ul'), ticking = false;
    var spy = function () {
      ticking = false;
      var y = window.scrollY + 330, cur = 0;
      targets.forEach(function (s, i) { if (s && s.getBoundingClientRect().top + window.scrollY <= y) cur = i; });
      if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4) cur = targets.length - 1;
      tabs.forEach(function (a, i) {
        var on = i === cur;
        a.classList.toggle('active', on);
        if (on) { a.setAttribute('aria-current', 'true'); if (list && list.scrollWidth > list.clientWidth) list.scrollLeft = a.offsetLeft - 24; } else { a.removeAttribute('aria-current'); }
      });
    };
    window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(spy); } }, { passive: true });
    window.addEventListener('resize', spy, { passive: true });
    spy();
  }

  /* ------------------------------------------------------- count-up stats */
  var fmt = function (n, dec) { return n.toLocaleString('en-US', { minimumFractionDigits: dec, maximumFractionDigits: dec }).replace('-', '−'); };
  var nums = $$('.pd-stat .num');
  function run(el) {
    var end = parseFloat(el.getAttribute('data-count')), dec = parseInt(el.getAttribute('data-dec') || '0', 10);
    if (isNaN(end) || reduced()) { el.textContent = fmt(end, dec); return; }
    var t0 = null, dur = 1200;
    (function step(t) {
      if (t0 === null) t0 = t;
      var p = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - p, 3);
      el.textContent = fmt(end * e, dec);
      if (p < 1) requestAnimationFrame(step); else el.textContent = fmt(end, dec);
    })(performance.now());
  }
  if (nums.length) {
    if ('IntersectionObserver' in window && !reduced()) {
      nums.forEach(function (n) { n.textContent = fmt(0, parseInt(n.getAttribute('data-dec') || '0', 10)); });
      var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { run(e.target); io.unobserve(e.target); } }); }, { threshold: .6 });
      nums.forEach(function (n) { io.observe(n); });
    }
  }

  /* ----------------------------------------- specification search + view */
  var VIEW_KEY = 'sats-spec-view';
  $$('.pd-specs').forEach(function (sec) {
    var input = $('.pd-search input', sec), count = $('.pd-count', sec), grid = $('.pd-spec-grid', sec), wrap = $('.pd-table-wrap', sec), empty = $('.pd-empty', sec);
    var btns = $$('.pd-view button', sec), total = parseInt(sec.getAttribute('data-total') || '0', 10);
    var cards = $$('.pd-spec', sec), rows = $$('tbody tr', sec);
    function setView(v) {
      grid.hidden = v === 'table'; wrap.hidden = v !== 'table';
      btns.forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-view') === v)); });
      try { localStorage.setItem(VIEW_KEY, v); } catch (e) {}
    }
    function filter() {
      var q = (input ? input.value : '').trim().toLowerCase(), shown = 0;
      cards.forEach(function (c, i) {
        var hit = !q || (c.getAttribute('data-search') || '').indexOf(q) !== -1;
        c.hidden = !hit; if (rows[i]) rows[i].hidden = !hit; if (hit) shown++;
      });
      if (count) count.textContent = q ? shown + ' of ' + total + ' specifications' : total + ' specifications';
      if (empty) empty.hidden = shown !== 0;
    }
    if (input) input.addEventListener('input', filter);
    btns.forEach(function (b) { b.addEventListener('click', function () { setView(b.getAttribute('data-view')); }); });
    var saved = null; try { saved = localStorage.getItem(VIEW_KEY); } catch (e) {}
    if (btns.length && (saved === 'table' || saved === 'cards')) setView(saved);
  });

  /* --------------------------------------------------------- range explorer */
  $$('.pd-range').forEach(function (box) {
    var cfg; try { cfg = JSON.parse(box.getAttribute('data-range')); } catch (e) { return; }
    var input = $('input[type=range]', box), val = $('.pd-range-val span', box), zone = $('.pd-range-zone-text', box), eta = $('.pd-range-eta', box);
    var AMB = 25;
    function mins(m) {
      if (m < 1) return '&lt; 1 min';
      if (m < 60) return '≈ ' + (m < 10 ? (Math.round(m * 10) / 10) : Math.round(m)) + ' min';
      var h = Math.floor(m / 60), r = Math.round(m - h * 60);
      return '≈ ' + h + ' h' + (r ? ' ' + r + ' min' : '');
    }
    function update() {
      var v = parseInt(input.value, 10);
      val.textContent = String(v).replace('-', '−');
      input.setAttribute('aria-valuetext', val.textContent + ' degrees Celsius');
      box.style.setProperty('--p', 'calc(11px + (100% - 22px) * ' + ((v - cfg.min) / (cfg.max - cfg.min)).toFixed(4) + ')');
      var z = cfg.zones[cfg.zones.length - 1][1];
      for (var i = 0; i < cfg.zones.length; i++) { if (v <= cfg.zones[i][0]) { z = cfg.zones[i][1]; break; } }
      zone.textContent = z; zone.classList.toggle('warn', v > cfg.std_max);
      var t = '';
      if (v === AMB) t = 'At ambient (25 °C)';
      else if (v > AMB && cfg.heat) t = 'Heating from 25 °C: <b>' + mins((v - AMB) / cfg.heat) + '</b> at ' + cfg.heat + ' °C/min';
      else if (v < AMB && cfg.cool) t = 'Cooling from 25 °C: <b>' + mins((AMB - v) / cfg.cool) + '</b> at ' + cfg.cool + ' °C/min';
      eta.innerHTML = t;
    }
    input.addEventListener('input', update);
    update();
    /* a gentle one-time sweep when the explorer first scrolls into view, so people notice it is interactive */
    if ('IntersectionObserver' in window && !reduced()) {
      var start = parseInt(input.value, 10), swept = false;
      new IntersectionObserver(function (es, ob) {
        if (!es[0].isIntersecting || swept) return; swept = true; ob.disconnect();
        var t0 = null, target = cfg.std_max;
        (function step(t) {
          if (t0 === null) t0 = t;
          var p = Math.min(1, (t - t0) / 1800);
          input.value = Math.round(start + (target - start) * Math.sin(p * Math.PI));   // start -> end of standard range -> start
          update();
          if (p < 1) requestAnimationFrame(step); else { input.value = start; update(); }
        })(performance.now());
      }, { threshold: .7 }).observe(box);
    }
  });
})();

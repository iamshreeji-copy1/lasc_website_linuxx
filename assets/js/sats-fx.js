/**
 * SATs v2 – "SATs Live" effects (no dependencies).
 * Theme toggle · circuit-trace canvas · interactive wafer map · typing line · word-reveal headings ·
 * 3D tilt · magnetic buttons · cursor glow.  Every effect checks the motion setting first.
 */
(function () {
  'use strict';
  var root = document.documentElement;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var reduced = function () { return root.getAttribute('data-motion') === 'reduced'; };
  var finePointer = window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var rand = function (a, b) { return a + Math.random() * (b - a); };

  /* public hook (used by the accessibility panel in a later phase) */
  window.SATS = window.SATS || {};
  window.SATS.setMotion = function (on) {
    root.setAttribute('data-motion', on ? 'full' : 'reduced');
    try { localStorage.setItem('sats-motion', on ? 'on' : 'off'); } catch (e) {}
  };

  /* ------------------------------------------------------------ theme (switched from the accessibility panel) */
  function applyTheme(t) {
    root.setAttribute('data-theme', t); root.setAttribute('data-bs-theme', t);
    var meta = $('meta[name="theme-color"]'); if (meta) meta.setAttribute('content', t === 'dark' ? '#03312b' : '#008374');
  }
  applyTheme(root.getAttribute('data-theme') || 'dark');
  window.SATS.toggleTheme = function () {
    var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    try { localStorage.setItem('sats-theme', next); } catch (e) {}
    return next;
  };

  /* --------------------------------------------------- word-reveal headings */
  function splitWords(el) {
    if (el.getAttribute('data-split')) return;
    el.setAttribute('data-split', '1');
    el.setAttribute('aria-label', el.textContent.replace(/\s+/g, ' ').trim());
    var idx = 0;
    (function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(function (p) {
            if (!p) return;
            if (/^\s+$/.test(p)) { frag.appendChild(document.createTextNode(' ')); return; }
            var w = document.createElement('span'); w.className = 'sw'; w.setAttribute('aria-hidden', 'true');
            var s = document.createElement('span'); s.style.setProperty('--i', idx++); s.textContent = p;
            w.appendChild(s); frag.appendChild(w);
          });
          n.parentNode.replaceChild(frag, n);
        } else if (n.nodeType === 1) { walk(n); }
      });
    })(el);
  }
  var heads = $$('.section-header h2, .hero h1, .pd-section > h2, .pd-summary h2, .pd-cta h2, .breadcrumbs .page-header h1');
  heads.forEach(splitWords);
  if (reduced() || !('IntersectionObserver' in window)) {
    heads.forEach(function (h) { h.classList.add('in-view'); });
  } else {
    var ho = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in-view'); ho.unobserve(e.target); } });
    }, { threshold: .35, rootMargin: '0px 0px -8% 0px' });
    heads.forEach(function (h) { if (h.closest('.hero') || h.closest('.breadcrumbs')) { setTimeout(function () { h.classList.add('in-view'); }, 350); } else { ho.observe(h); } });
  }

  /* -------------------------------------------------------------- typing line */
  $$('[data-typed]').forEach(function (el) {
    var words; try { words = JSON.parse(el.getAttribute('data-words')); } catch (e) { words = []; }
    if (!words.length) return;
    var w = 0, c = 0, del = false, running = false;
    function tick() {
      if (reduced()) { running = false; el.textContent = words[0]; return; }
      running = true;
      var word = words[w];
      if (!del) { c++; el.textContent = word.slice(0, c); if (c === word.length) { del = true; return setTimeout(tick, 1500); } return setTimeout(tick, 70); }
      c--; el.textContent = word.slice(0, c);
      if (c === 0) { del = false; w = (w + 1) % words.length; return setTimeout(tick, 350); }
      setTimeout(tick, 32);
    }
    el._typedStart = function () { if (!running && !reduced()) { w = 0; c = 0; del = false; tick(); } };
    if (reduced()) { el.textContent = words[0]; return; }
    tick();
  });

  /* ------------------------------------------------- shared canvas lifecycle */
  var loops = [];
  function makeLoop(canvas, draw) {
    var raf = 0, visible = false, last = 0;
    function frame(t) {
      raf = 0;
      if (!visible || document.hidden) return;
      var dt = Math.min(0.05, (t - last) / 1000 || 0.016); last = t;
      draw(dt, t / 1000);
      if (!reduced()) raf = requestAnimationFrame(frame);
    }
    function start() { if (!raf && visible) { last = performance.now(); raf = requestAnimationFrame(frame); } }
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) { visible = es[0].isIntersecting; if (visible) { reduced() ? draw(0, 0) : start(); } }, { threshold: 0 }).observe(canvas);
    } else { visible = true; start(); }
    document.addEventListener('visibilitychange', start);
    var api = { start: start, redraw: function () { draw(0, 0); } };
    loops.push(api);
    return api;
  }
  function fit(canvas) {
    var r = canvas.getBoundingClientRect(), dpr = Math.min(2, window.devicePixelRatio || 1);
    canvas.width = Math.max(1, Math.round(r.width * dpr)); canvas.height = Math.max(1, Math.round(r.height * dpr));
    var ctx = canvas.getContext('2d'); ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return { ctx: ctx, w: r.width, h: r.height };
  }
  function onResize(fn) { var t; window.addEventListener('resize', function () { clearTimeout(t); t = setTimeout(fn, 180); }, { passive: true }); }

  /* ------------------------------------------- circuit traces (hero + banners) */
  $$('canvas.fx-circuit').forEach(function (canvas) {
    var ctx, W, H, paths = [], GRID = 44;
    var DIRS = [[1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1]];
    function build() {
      var s = fit(canvas); ctx = s.ctx; W = s.w; H = s.h; paths = [];
      var n = Math.max(8, Math.round(W * H / 42000));
      for (var i = 0; i < n; i++) {
        var x = Math.round(rand(0, W) / GRID) * GRID, y = Math.round(rand(0, H) / GRID) * GRID, d = Math.floor(rand(0, 8));
        var pts = [[x, y]], segs = Math.floor(rand(3, 7));
        for (var k = 0; k < segs; k++) {
          var len = GRID * Math.floor(rand(1, 4)) * (DIRS[d][0] && DIRS[d][1] ? 0.7 : 1);
          x += DIRS[d][0] * len; y += DIRS[d][1] * len; pts.push([x, y]);
          d = (d + (Math.random() < .5 ? 1 : 7)) % 8;
        }
        var cum = [0], total = 0;
        for (var j = 1; j < pts.length; j++) { total += Math.hypot(pts[j][0] - pts[j - 1][0], pts[j][1] - pts[j - 1][1]); cum.push(total); }
        paths.push({ pts: pts, cum: cum, total: total, pos: rand(0, total), speed: rand(50, 130), hot: Math.random() < .35 });
      }
    }
    function at(p, dist) {
      dist = ((dist % p.total) + p.total) % p.total;
      for (var j = 1; j < p.cum.length; j++) if (dist <= p.cum[j]) {
        var t = (dist - p.cum[j - 1]) / (p.cum[j] - p.cum[j - 1]);
        return [p.pts[j - 1][0] + (p.pts[j][0] - p.pts[j - 1][0]) * t, p.pts[j - 1][1] + (p.pts[j][1] - p.pts[j - 1][1]) * t];
      }
      return p.pts[p.pts.length - 1];
    }
    function draw(dt) {
      ctx.clearRect(0, 0, W, H);
      ctx.lineWidth = 1.3; ctx.lineJoin = 'round'; ctx.strokeStyle = 'rgba(255,255,255,.085)';
      paths.forEach(function (p) {
        ctx.beginPath(); p.pts.forEach(function (q, i) { i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); }); ctx.stroke();
        [p.pts[0], p.pts[p.pts.length - 1]].forEach(function (q) { ctx.beginPath(); ctx.arc(q[0], q[1], 3.2, 0, 6.283); ctx.stroke(); });
      });
      if (reduced()) return;
      paths.forEach(function (p) {
        p.pos += p.speed * dt;
        for (var k = 0; k < 9; k++) {
          var q = at(p, p.pos - k * 7), a = (1 - k / 9);
          ctx.fillStyle = p.hot ? 'rgba(255,138,115,' + (a * .85) + ')' : 'rgba(180,255,244,' + (a * .7) + ')';
          ctx.beginPath(); ctx.arc(q[0], q[1], 2.4 * a + .6, 0, 6.283); ctx.fill();
        }
      });
    }
    build(); var loop = makeLoop(canvas, draw); onResize(function () { build(); loop.redraw(); });
  });

  /* ---------------------------------------------------- interactive wafer map */
  var wcan = $('#wafer');
  if (wcan) {
    var ctx2, S, R, cx, cy, dies = [], beam = 0, phase = 0, hoverDie = null, label = $('#wafer-label');
    function buildWafer() {
      var s = fit(wcan); ctx2 = s.ctx; S = s.w; R = S * 0.44; cx = S / 2; cy = S / 2; dies = [];
      var dw = S / 23, dh = dw * 1.12, cols = Math.ceil((R * 2) / dw), rows = Math.ceil((R * 2) / dh);
      for (var r = 0; r < rows; r++) for (var c = 0; c < cols; c++) {
        var x = cx - R + c * dw + 1, y = cy - R + r * dh + 1, ok = true;
        [[x, y], [x + dw - 2, y], [x, y + dh - 2], [x + dw - 2, y + dh - 2]].forEach(function (q) { if (Math.hypot(q[0] - cx, q[1] - cy) > R - 7) ok = false; });
        if (ok) dies.push({ x: x, y: y, w: dw - 2, h: dh - 2, c: c, r: r, fail: Math.random() < .08, tested: 0, flash: 0 });
      }
      beam = cy - R;
    }
    function drawWafer(dt, t) {
      ctx2.clearRect(0, 0, S, S);
      var g = ctx2.createRadialGradient(cx - R * .3, cy - R * .35, R * .1, cx, cy, R);
      g.addColorStop(0, 'rgba(210,255,248,.34)'); g.addColorStop(.7, 'rgba(120,230,215,.16)'); g.addColorStop(1, 'rgba(0,50,44,.35)');
      ctx2.save(); ctx2.beginPath(); ctx2.arc(cx, cy, R, 0, 6.283); ctx2.fillStyle = g; ctx2.fill();
      ctx2.lineWidth = 2; ctx2.strokeStyle = 'rgba(255,255,255,.55)'; ctx2.stroke();
      ctx2.beginPath(); ctx2.arc(cx, cy, R + 7, 0, 6.283); ctx2.lineWidth = 1; ctx2.strokeStyle = 'rgba(255,255,255,.18)'; ctx2.stroke();
      ctx2.globalCompositeOperation = 'destination-out'; ctx2.beginPath(); ctx2.arc(cx, cy + R + 1, R * .075, 0, 6.283); ctx2.fill();
      ctx2.restore();
      if (!reduced()) {
        beam += dt * S * .21;
        if (beam > cy + R + 20) { beam = cy - R - 20; phase++; document.dispatchEvent(new CustomEvent('sats:fx', { detail: { type: 'scan' } })); dies.forEach(function (d) { d.tested = 0; d.fail = Math.random() < .08; }); }
      } else { dies.forEach(function (d) { d.tested = 1; }); }
      dies.forEach(function (d) {
        if (!reduced() && d.tested === 0 && d.y + d.h / 2 < beam) { d.tested = 1; d.flash = 1; }
        d.flash = Math.max(0, d.flash - dt * 1.6);
        var hov = hoverDie === d;
        var fill = d.tested ? (d.fail ? 'rgba(248,90,64,' + (.78 + d.flash * .2) + ')' : 'rgba(150,255,236,' + (.26 + d.flash * .55) + ')') : 'rgba(255,255,255,.11)';
        ctx2.fillStyle = hov ? 'rgba(255,255,255,.95)' : fill; ctx2.fillRect(d.x, d.y, d.w, d.h);
      });
      if (!reduced()) {   // scanning beam
        var bg = ctx2.createLinearGradient(0, beam - 26, 0, beam + 3);
        bg.addColorStop(0, 'rgba(160,255,240,0)'); bg.addColorStop(1, 'rgba(190,255,246,.55)');
        ctx2.save(); ctx2.beginPath(); ctx2.arc(cx, cy, R + 4, 0, 6.283); ctx2.clip(); ctx2.fillStyle = bg; ctx2.fillRect(cx - R - 6, beam - 26, R * 2 + 12, 29);
        ctx2.fillStyle = 'rgba(255,255,255,.9)'; ctx2.fillRect(cx - R - 6, beam, R * 2 + 12, 1.6); ctx2.restore();
      }
      if (hoverDie) {   // probe crosshair on the hovered die
        var d = hoverDie, mx = d.x + d.w / 2, my = d.y + d.h / 2;
        ctx2.save(); ctx2.strokeStyle = 'rgba(255,255,255,.85)'; ctx2.lineWidth = 1; ctx2.setLineDash([4, 4]);
        ctx2.beginPath(); ctx2.moveTo(mx, cy - R); ctx2.lineTo(mx, cy + R); ctx2.moveTo(cx - R, my); ctx2.lineTo(cx + R, my); ctx2.stroke(); ctx2.restore();
      }
    }
    buildWafer();
    var wloop = makeLoop(wcan, drawWafer); onResize(function () { buildWafer(); wloop.redraw(); });
    var wrap = wcan.parentNode;
    wcan.addEventListener('pointermove', function (e) {
      var r = wcan.getBoundingClientRect(), x = (e.clientX - r.left) * (S / r.width), y = (e.clientY - r.top) * (S / r.height), found = null;
      for (var i = 0; i < dies.length; i++) { var d = dies[i]; if (x >= d.x && x <= d.x + d.w && y >= d.y && y <= d.y + d.h) { found = d; break; } }
      if (found && found !== hoverDie && found.tested) document.dispatchEvent(new CustomEvent('sats:fx', { detail: { type: 'die', fail: found.fail } }));
      hoverDie = found;
      if (label) label.textContent = found ? 'Die (' + found.c + ', ' + found.r + ') · ' + (found.tested ? (found.fail ? 'FAIL' : 'PASS') : 'queued') : 'Live wafer map · hover to probe a die';
      if (!reduced() && finePointer) { wrap.style.setProperty('--wy', ((x / S - .5) * 10).toFixed(2) + 'deg'); wrap.style.setProperty('--wx', ((.5 - y / S) * 10).toFixed(2) + 'deg'); }
      if (reduced()) wloop.redraw();
    });
    wcan.addEventListener('pointerleave', function () {
      hoverDie = null; wrap.style.setProperty('--wx', '0deg'); wrap.style.setProperty('--wy', '0deg');
      if (label) label.textContent = 'Live wafer map · hover to probe a die';
      if (reduced()) wloop.redraw();
    });
  }

  /* ----------------------------------- tilt · magnetic · cursor glow (pointer) */
  if (finePointer) {
    var TILT = '.services .service-item, .portfolio-card, .about-card, .pricing .pricing-item:not(.featured), .hero .icon-box, .pd-spec';
    var MAG = '.btn-get-started, .btn-sats, .cta-btn, .navbar .getstarted, .buy-btn';
    var tiltEl = null, magEl = null;
    function clear(el) { if (el) { el.style.transform = ''; el.classList.remove('is-tilting'); } }
    document.addEventListener('pointermove', function (e) {
      if (reduced()) { clear(tiltEl); clear(magEl); return; }
      var t = e.target.closest ? e.target.closest(TILT) : null;
      if (t !== tiltEl) { clear(tiltEl); tiltEl = t; }
      if (t) {
        var r = t.getBoundingClientRect(), px = (e.clientX - r.left) / r.width - .5, py = (e.clientY - r.top) / r.height - .5;
        t.classList.add('is-tilting');
        t.style.transform = 'perspective(900px) rotateX(' + (-py * 7).toFixed(2) + 'deg) rotateY(' + (px * 9).toFixed(2) + 'deg) translateY(-6px)';
      }
      var m = e.target.closest ? e.target.closest(MAG) : null;
      if (m !== magEl) { clear(magEl); magEl = m; }
      if (m) {
        var b = m.getBoundingClientRect();
        m.classList.add('is-tilting');
        m.style.transform = 'translate(' + (((e.clientX - (b.left + b.width / 2)) / b.width) * 12).toFixed(1) + 'px,' + (((e.clientY - (b.top + b.height / 2)) / b.height) * 10).toFixed(1) + 'px)';
      }
      var cta = e.target.closest ? e.target.closest('.call-to-action .container') : null;
      if (cta) { var cr = cta.getBoundingClientRect(); cta.style.setProperty('--mx', ((e.clientX - cr.left) / cr.width * 100).toFixed(1) + '%'); cta.style.setProperty('--my', ((e.clientY - cr.top) / cr.height * 100).toFixed(1) + '%'); }
    }, { passive: true });
    document.addEventListener('pointerleave', function () { clear(tiltEl); clear(magEl); tiltEl = magEl = null; });

    var glow = document.createElement('div'); glow.className = 'cursor-glow'; glow.setAttribute('aria-hidden', 'true'); document.body.appendChild(glow);
    var gx = 0, gy = 0, tx = 0, ty = 0, on = false;
    document.addEventListener('pointermove', function (e) { tx = e.clientX; ty = e.clientY; if (!on && !reduced()) { on = true; glow.classList.add('on'); gx = tx; gy = ty; } }, { passive: true });
    document.addEventListener('mouseleave', function () { on = false; glow.classList.remove('on'); });
    (function loop() {
      if (on && !reduced()) { gx += (tx - gx) * .14; gy += (ty - gy) * .14; glow.style.transform = 'translate(' + gx.toFixed(1) + 'px,' + gy.toFixed(1) + 'px)'; }
      requestAnimationFrame(loop);
    })();
  }

  /* ------------------------------------- react when animations are paused / resumed */
  new MutationObserver(function () {
    var off = reduced();
    loops.forEach(function (l) { off ? l.redraw() : l.start(); });
    $$('[data-typed]').forEach(function (el) { if (el._typedStart) { if (off) { try { el.textContent = JSON.parse(el.getAttribute('data-words'))[0]; } catch (e) {} } else el._typedStart(); } });
    $$('.swiper').forEach(function (n) {
      var sw = n.swiper; if (!sw || !sw.autoplay) return;
      if (off) sw.autoplay.stop(); else if (sw.params && sw.params.autoplay && sw.params.autoplay.delay) sw.autoplay.start();
    });
  }).observe(root, { attributes: true, attributeFilter: ['data-motion'] });
})();

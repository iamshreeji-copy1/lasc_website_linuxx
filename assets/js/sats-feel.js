/**
 * SATs v2 – synchronised sound + haptics for the animations (no dependencies, no audio files).
 *
 * One "score" (a list of notes with a start time) drives BOTH senses, so they always land together:
 *   - audio:   each note is a short synthesised tone (Web Audio), scheduled at its start time;
 *   - haptics: each note becomes a vibration burst at the same start time. The note's pitch sets the TEXTURE
 *              (high = fast light pulses, low = slow heavy pulses) and its strength sets the on/off duty,
 *              so different interactions never feel the same.
 * Rhythms are composed per animation: counters tick along their easing curve, the wafer scan is a rising run,
 * the temperature slider changes texture with the value, the footer heart beats "lub-dub" in time with its animation.
 *
 * Rules: silent until the visitor's first touch/click; Sound and Vibration switches live in the Accessibility panel;
 * vibration is off for reduced-motion users. (Vibration works on Android Chrome/Firefox; iPhones and desktops ignore it.)
 */
(function () {
  'use strict';
  var root = document.documentElement, KEY = 'sats-a11y';
  var on = { sound: true, haptics: true };
  try { var d = JSON.parse(localStorage.getItem(KEY) || '{}'); if (d.sound !== undefined) on.sound = !!d.sound; if (d.haptics !== undefined) on.haptics = !!d.haptics; } catch (e) {}
  document.addEventListener('sats:fb-change', function (e) { on.sound = !!e.detail.sound; on.haptics = !!e.detail.haptics; });

  var gestured = false;
  ['pointerdown', 'keydown', 'touchend'].forEach(function (ev) { window.addEventListener(ev, function () { gestured = true; }, { passive: true, capture: true }); });
  var active = function () { return navigator.userActivation ? navigator.userActivation.hasBeenActive : gestured; };
  var reduced = function () { return root.getAttribute('data-motion') === 'reduced'; };
  var clamp = function (v, a, b) { return Math.max(a, Math.min(b, v)); };

  /* ------------------------------------------------------------------ audio */
  var ctx = null, master = null;
  function ac() {
    if (!on.sound || !active()) return null;
    if (!ctx) {
      var C = window.AudioContext || window.webkitAudioContext; if (!C) return null;
      try {
        ctx = new C(); master = ctx.createGain(); master.gain.value = .14;
        var comp = ctx.createDynamicsCompressor(); master.connect(comp); comp.connect(ctx.destination);
      } catch (e) { ctx = null; return null; }
    }
    if (ctx.state === 'suspended') ctx.resume();
    return ctx;
  }
  function tone(n, c) {
    var o = c.createOscillator(), g = c.createGain(), t = c.currentTime + n.at / 1000, dur = n.d / 1000;
    o.type = n.type || 'sine'; o.frequency.setValueAtTime(n.f, t);
    if (n.slide) o.frequency.exponentialRampToValueAtTime(n.slide, t + dur);
    g.gain.setValueAtTime(.0001, t); g.gain.exponentialRampToValueAtTime(n.v || .4, t + .008); g.gain.exponentialRampToValueAtTime(.0001, t + dur);
    o.connect(g); g.connect(master); o.start(t); o.stop(t + dur + .03);
  }

  /* ---------------------------------------------------------------- haptics */
  /* texture of one note: pulse period from pitch, on/off duty from strength, length from the note's duration */
  function burst(n) {
    var f = n.slide ? (n.f + n.slide) / 2 : n.f;
    var period = f > 1500 ? 8 : f > 900 ? 12 : f > 500 ? 18 : f > 250 ? 26 : 38;           // ms per pulse  (≈ 125 Hz … 26 Hz feel)
    var h = clamp(n.h !== undefined ? n.h : (n.v || .4) * 1.5, .15, 1);
    var on_ = Math.max(2, Math.round(period * (.28 + .5 * h)));                              // stronger = longer "on"
    var off = Math.max(2, period - on_);
    var total = clamp(n.d * (.35 + .3 * h), on_, 44);
    var count = Math.max(1, Math.round(total / period)), out = [];
    for (var i = 0; i < count; i++) { out.push(on_); if (i < count - 1) out.push(off); }
    return out;
  }
  /* turn a score into ONE vibration pattern whose bursts start exactly when the notes start */
  function pattern(notes) {
    var list = notes.slice().sort(function (a, b) { return a.at - b.at; }), p = [], cursor = 0;   // cursor = when the last burst ended
    list.forEach(function (n, i) {
      var b = burst(n), len = b.reduce(function (sum, x) { return sum + x; }, 0);
      var start = Math.max(n.at, cursor + (i ? 4 : 0)), gap = Math.round(start - cursor);
      if (i === 0) { if (gap > 0) p.push(0, gap); }          // leading pause = "vibrate 0 ms, then wait"
      else p.push(gap);                                      // pause between the previous burst and this one
      p = p.concat(b); cursor = start + len;
    });
    return p.slice(0, 98);
  }
  function vib(p) {
    if (!on.haptics || reduced() || !navigator.vibrate || !active() || !p.length) return;
    try { navigator.vibrate(p); } catch (e) {}
  }

  /* ---------------------------------------------------------- the one entry */
  function play(notes) {
    var c = ac();
    if (c) notes.forEach(function (n) { if (!n.silent) tone(n, c); });
    vib(pattern(notes));
  }
  var N = function (f, at, d, v, o) { var n = { f: f, at: at, d: d, v: v }; for (var k in (o || {})) n[k] = o[k]; return n; };

  /* ------------------------------------------------------------ the sounds-with-rhythm */
  var lastTap = 0;
  var TAPS = {
    button: function () { return [N(1400, 0, 45, .5, { type: 'triangle', slide: 900 })]; },                      // light, fast pulses
    chip:   function () { return [N(980, 0, 55, .42, { type: 'triangle', slide: 760 }), N(1300, 45, 40, .25)]; },// "ta-tick" two-step
    card:   function () { return [N(430, 0, 95, .4, { slide: 300, h: .8 })]; },                                  // soft heavy thud
    grab:   function () { return [N(300, 0, 70, .3, { type: 'sine', slide: 380, h: .9 })]; }                     // slider grab: low, firm
  };
  function tap(kind) {
    var now = Date.now(); if (now - lastTap < 60) return; lastTap = now;
    play((TAPS[kind] || TAPS.button)());
  }
  function tick(t) { t = clamp(t, 0, 1); play([N(700 + 1100 * t, 0, 28, .16, { type: 'square', h: .3 + .5 * (1 - t) })]); }   // pitch rises, feel gets finer
  function warn()  { play([N(160, 0, 120, .4, { type: 'sawtooth', slide: 100 }), N(150, 150, 120, .4, { type: 'sawtooth', slide: 90 }), N(120, 310, 200, .45, { type: 'sawtooth', slide: 70 })]); } // triple thud
  function dieOk()   { play([N(1760, 0, 50, .3, { h: .25 })]); }
  function dieFail() { play([N(150, 0, 150, .4, { type: 'sawtooth', slide: 90, h: .95 }), N(120, 190, 150, .35, { type: 'sawtooth', slide: 80, h: .8 })]); }
  function swOn()  { play([N(660, 0, 80, .5, { h: .6 }), N(990, 85, 110, .5, { h: .4 })]); }                  // ta-DA, rising
  function swOff() { play([N(990, 0, 80, .45, { h: .4 }), N(660, 85, 110, .45, { h: .6 })]); }                // falling
  function popUp()   { play([N(520, 0, 90, .6, { slide: 880, h: .7 }), N(1040, 75, 80, .3, { h: .35 })]); }
  function popDown() { play([N(880, 0, 90, .5, { slide: 440, h: .5 })]); }
  function complete() { play([N(880, 0, 220, .5, { h: .7 }), N(1318, 90, 300, .45, { h: .5 }), N(1760, 190, 260, .3, { h: .3 })]); }   // 3-step ascending
  function chime()    { play([N(660, 0, 350, .3, { h: .7 }), N(990, 130, 450, .25, { h: .45 })]); }
  var scanned = false;
  function scan() {                                                                                           // rising run, strength grows with pitch
    if (scanned) return; scanned = true;
    var s = []; for (var i = 0; i < 9; i++) s.push(N(380 + i * 150, i * 62, 40, .12 + i * .02, { h: .25 + i * .08 }));
    play(s);
  }
  /* counter: ticks follow the easing curve (fast at first, slowing as it settles), then a closing chord */
  var counted = false;
  function count(dur) {
    if (counted) return; counted = true; dur = dur || 1200;
    var s = [], steps = 12;
    for (var i = 1; i <= steps; i++) {
      var t = 1 - Math.pow(1 - i / steps, 1 / 3);                                // inverse of easeOutCubic: when the value passes i/12
      s.push(N(620 + i * 85, Math.round(t * dur) - 20, 26, .1, { type: 'square', h: .75 - i * .04 }));
    }
    s.push(N(880, dur + 40, 220, .45, { h: .8 }), N(1318, dur + 130, 300, .4, { h: .55 }));
    play(s);
  }
  /* heart in the footer: "lub-dub" at the exact moments of its CSS animation (beats at 15% and 45% of 1.4 s) */
  var hearted = new WeakSet();
  function heart(el) {
    if (hearted.has(el) || reduced() || !active()) return; hearted.add(el);
    var cycle = 1400, now = 0;
    try { var a = el.getAnimations && el.getAnimations()[0]; now = a ? (a.currentTime % cycle) : 0; } catch (e) {}
    var s = [], beats = 0;                                          // the next six upcoming beats (3 loops), in order, none duplicated
    for (var k = 0; k < 4 && beats < 6; k++) [210, 630].forEach(function (b, j) {
      var at = k * cycle + b - now;
      if (at >= 0 && beats < 6) { s.push(N(j ? 70 : 90, Math.round(at), j ? 140 : 170, j ? .32 : .42, { slide: j ? 55 : 70, h: j ? .6 : .9 })); beats++; }
    });
    play(s);
  }
  window.SATS = window.SATS || {};
  window.SATS.feel = { tap: tap, complete: complete, chime: chime, count: count, play: play, pattern: pattern };

  /* ----------------------------------------------------------- what triggers what */
  var CARDS = '.portfolio-card, .service-item, .pd-spec, .pd-stat, .about-card, .icon-box, .pricing-item';
  var CHIPS = '.portfolio-flters li, .pd-tabs a, .accordion-button, summary, .pd-view button';
  document.addEventListener('pointerdown', function (e) {
    if (e.button > 0 || !e.target.closest) return;
    var t = e.target;
    if (t.closest('[data-enq], [role="switch"]')) return;                       // these get their own rhythm on click
    if (t.closest('input[type="range"]')) return tap('grab');
    if (t.closest(CHIPS)) return tap('chip');
    if (t.closest(CARDS)) return tap('card');                                  // cards are links too, so test them before plain buttons
    if (t.closest('a[href], button, [role="button"]')) return tap('button');
  }, { passive: true, capture: true });

  document.addEventListener('click', function (e) {
    if (!e.target.closest) return;
    var sw = e.target.closest('[role="switch"]');
    if (sw) { setTimeout(function () { sw.getAttribute('aria-checked') === 'true' ? swOn() : swOff(); }, 0); return; }
    var q = e.target.closest('[data-enq]');
    if (q) { setTimeout(function () { q.getAttribute('aria-pressed') === 'true' ? popUp() : popDown(); }, 0); return; }
    if (e.target.closest('.enq-actions [data-act="wa"], .enq-actions [data-act="mail"]')) complete();
  }, true);

  document.addEventListener('sats:fx', function (e) {
    var d = e.detail || {};
    if (d.type === 'step') tick(d.t); else if (d.type === 'warn') warn();
    else if (d.type === 'die') d.fail ? dieFail() : dieOk();
    else if (d.type === 'count') count(d.dur); else if (d.type === 'complete') complete(); else if (d.type === 'scan') scan();
  });

  if ('IntersectionObserver' in window) {
    var co = new IntersectionObserver(function (es) {                              // home-page counters (PureCounter runs for 1 s)
      es.forEach(function (en) { if (en.isIntersecting) { co.unobserve(en.target); count(1000); } });
    }, { threshold: .7 });
    var first = document.querySelector('.stats-counter .purecounter'); if (first) co.observe(first);

    var lastChime = 0, so = new IntersectionObserver(function (es) {               // soft chime when a key section arrives
      es.forEach(function (en) {
        if (!en.isIntersecting) return; so.unobserve(en.target);
        if (Date.now() - lastChime > 2500) { lastChime = Date.now(); chime(); }
      });
    }, { threshold: .6 });
    Array.prototype.forEach.call(document.querySelectorAll('.call-to-action .container, .pd-cta, .li-card'), function (n) { so.observe(n); });

    var ho = new IntersectionObserver(function (es) {                              // heartbeat in step with the heart animation
      es.forEach(function (en) { if (en.isIntersecting) { ho.unobserve(en.target); heart(en.target); } });
    }, { threshold: 1 });
    Array.prototype.forEach.call(document.querySelectorAll('.heart'), function (n) { ho.observe(n); });
  }
})();

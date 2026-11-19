/**
 * SATs v2 – sound + haptics for the animations (no dependencies, no audio files).
 *  - Sounds are synthesised with the Web Audio API: short, quiet, and only after the visitor's first touch/click.
 *  - Vibration uses navigator.vibrate (Android Chrome/Firefox; not iPhone/desktop). "High frequency" = a rapid train of micro-pulses.
 *  - Switches live in the Accessibility panel (sound / vibration). Vibration is also off for reduced-motion users.
 *  - Triggers: touching buttons/cards/chips/tabs, switches, enquiry add/remove, the wafer dies, the temperature slider,
 *    counters finishing, and a soft chime when key sections arrive.
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
  function tone(freq, delay, dur, type, vol, slideTo) {
    var c = ac(); if (!c) return;
    var o = c.createOscillator(), g = c.createGain(), t = c.currentTime + (delay || 0);
    o.type = type || 'sine'; o.frequency.setValueAtTime(freq, t);
    if (slideTo) o.frequency.exponentialRampToValueAtTime(slideTo, t + dur);
    g.gain.setValueAtTime(.0001, t); g.gain.exponentialRampToValueAtTime(vol || .5, t + .008); g.gain.exponentialRampToValueAtTime(.0001, t + dur);
    o.connect(g); g.connect(master); o.start(t); o.stop(t + dur + .03);
  }

  /* ---------------------------------------------------------------- haptics */
  function buzz(pulses) {            // high-frequency buzz: n micro-pulses of 5 ms on / 5 ms off
    var p = []; for (var i = 0; i < pulses; i++) p.push(5, 5); return p;
  }
  function vib(pattern) {
    if (!on.haptics || reduced() || !navigator.vibrate || !active()) return;
    try { navigator.vibrate(pattern); } catch (e) {}
  }

  /* ----------------------------------------------------------------- events */
  var lastTap = 0;
  function tap()      { var n = Date.now(); if (n - lastTap < 60) return; lastTap = n; tone(1400, 0, .045, 'triangle', .5, 900); vib(buzz(3)); }
  function tick(t)    { tone(700 + 1100 * Math.max(0, Math.min(1, t)), 0, .03, 'square', .16); vib([6]); }
  function popUp()    { tone(520, 0, .09, 'sine', .6, 880); tone(1040, .07, .08, 'sine', .3); vib(buzz(5)); }
  function popDown()  { tone(880, 0, .09, 'sine', .5, 440); vib(buzz(3)); }
  function swOn()     { tone(660, 0, .08, 'sine', .5); tone(990, .07, .1, 'sine', .5); vib(buzz(4)); }
  function swOff()    { tone(990, 0, .08, 'sine', .45); tone(660, .07, .1, 'sine', .45); vib(buzz(3)); }
  function dieOk()    { tone(1760, 0, .05, 'sine', .32); vib([4, 4, 4]); }
  function dieFail()  { tone(150, 0, .16, 'sawtooth', .4, 90); vib([25, 30, 25]); }
  function complete() { tone(880, 0, .22, 'sine', .5); tone(1318, .09, .3, 'sine', .45); vib(buzz(10)); }
  function chime()    { tone(660, 0, .35, 'sine', .3); tone(990, .12, .45, 'sine', .25); vib(buzz(6)); }
  var scanned = false;
  function scan()     { if (scanned) return; scanned = true; tone(300, 0, .55, 'sine', .2, 1200); vib(buzz(8)); }
  window.SATS = window.SATS || {};
  window.SATS.feel = { tap: tap, complete: complete, chime: chime };

  /* touching interactive things */
  var TAP = 'a[href], button, [role="button"], .portfolio-flters li, .accordion-button, summary, input[type="range"], .portfolio-card, .service-item, .pd-spec, .pd-stat, .about-card, .icon-box, .pricing-item';
  document.addEventListener('pointerdown', function (e) {
    if (e.button > 0 || !e.target.closest) return;
    var el = e.target.closest(TAP); if (!el) return;
    if (el.closest('[data-enq], [role="switch"]')) return;           // these get their own sound on click
    tap();
  }, { passive: true, capture: true });

  document.addEventListener('click', function (e) {
    if (!e.target.closest) return;
    var sw = e.target.closest('[role="switch"]');
    if (sw) { setTimeout(function () { sw.getAttribute('aria-checked') === 'true' ? swOn() : swOff(); }, 0); return; }
    var q = e.target.closest('[data-enq]');
    if (q) { setTimeout(function () { q.getAttribute('aria-pressed') === 'true' ? popUp() : popDown(); }, 0); return; }
    if (e.target.closest('.enq-actions [data-act="wa"], .enq-actions [data-act="mail"]')) complete();
  }, true);

  /* animation milestones reported by the other scripts */
  document.addEventListener('sats:fx', function (e) {
    var d = e.detail || {};
    if (d.type === 'step') tick(d.t); else if (d.type === 'warn') dieFail();
    else if (d.type === 'die') d.fail ? dieFail() : dieOk();
    else if (d.type === 'complete') complete(); else if (d.type === 'scan') scan();
  });

  /* counters on the home page finishing (PureCounter runs ~1s) */
  if ('IntersectionObserver' in window) {
    var co = new IntersectionObserver(function (es) {
      es.forEach(function (en) { if (en.isIntersecting) { co.unobserve(en.target); setTimeout(complete, 1300); } });
    }, { threshold: .7 });
    var first = document.querySelector('.stats-counter .purecounter'); if (first) co.observe(first);

    /* soft chime when a key section arrives (once each) */
    var lastChime = 0;
    var so = new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        if (!en.isIntersecting) return; so.unobserve(en.target);
        if (Date.now() - lastChime > 2500) { lastChime = Date.now(); chime(); }
      });
    }, { threshold: .6 });
    Array.prototype.forEach.call(document.querySelectorAll('.call-to-action .container, .crafted .container, .pd-cta, .li-card'), function (n) { so.observe(n); });
  }
})();

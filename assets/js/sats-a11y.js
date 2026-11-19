/**
 * SATs v2 – accessibility panel (no dependencies).
 * Text size · dark theme · high contrast · readable font · spacing · highlight links · big cursor ·
 * reading guide · pause animations · read aloud.   Settings are saved on the device (localStorage).
 * Early attributes (zoom/contrast/font/...) are applied by the tiny inline script in <head> to avoid a flash.
 */
(function () {
  'use strict';
  var root = document.documentElement, KEY = 'sats-a11y';
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var ZOOMS = [100, 115, 130, 150];
  var state = { zoom: 0, contrast: false, font: false, spacing: false, links: false, cursor: false, guide: false, sound: true, haptics: true };

  try { var saved = JSON.parse(localStorage.getItem(KEY) || '{}'); Object.keys(state).forEach(function (k) { if (saved[k] !== undefined) state[k] = saved[k]; }); } catch (e) {}
  function save() { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} }
  var motionOff = function () { return root.getAttribute('data-motion') === 'reduced'; };
  var themeDark = function () { return root.getAttribute('data-theme') === 'dark'; };

  /* ----------------------------------------------------- apply to the page */
  var guideEl = null, live = null;
  function announce(msg) { if (live) { live.textContent = ''; setTimeout(function () { live.textContent = msg; }, 30); } }
  function setAttr(name, on, val) { if (on) root.setAttribute(name, val || 'on'); else root.removeAttribute(name); }

  function apply() {
    setAttr('data-a11y-zoom', state.zoom > 0, String(state.zoom));
    setAttr('data-contrast', state.contrast, 'high');
    setAttr('data-a11y-font', state.font, 'readable');
    setAttr('data-a11y-spacing', state.spacing);
    setAttr('data-a11y-links', state.links);
    setAttr('data-a11y-cursor', state.cursor, 'big');
    if (state.font) loadFont();
    guide(state.guide);
    document.dispatchEvent(new CustomEvent('sats:fb-change', { detail: { sound: state.sound, haptics: state.haptics } }));
  }
  function loadFont() {
    if ($('#a11y-font')) return;
    var l = document.createElement('link'); l.id = 'a11y-font'; l.rel = 'stylesheet';
    l.href = 'https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&display=swap';
    document.head.appendChild(l);
  }
  function guide(on) {
    if (on && !guideEl) {
      guideEl = document.createElement('div'); guideEl.className = 'a11y-guide'; guideEl.setAttribute('aria-hidden', 'true');
      guideEl.style.top = Math.round(window.innerHeight / 2 - 30) + 'px'; document.body.appendChild(guideEl);
      var mv = function (e) { var y = e.touches ? e.touches[0].clientY : e.clientY; guideEl.style.top = Math.round(y - 30) + 'px'; };
      document.addEventListener('mousemove', mv, { passive: true }); document.addEventListener('touchmove', mv, { passive: true });
      guideEl._off = function () { document.removeEventListener('mousemove', mv); document.removeEventListener('touchmove', mv); };
    } else if (!on && guideEl) { guideEl._off(); guideEl.remove(); guideEl = null; }
  }

  /* ---------------------------------------------------------- read aloud */
  var synth = window.speechSynthesis, speaking = false;
  function pageText() {
    var sel = window.getSelection && String(window.getSelection()).trim();
    if (sel) return sel;
    var m = $('main') || document.body, clone = m.cloneNode(true);
    $$('script,style,canvas,svg,.pd-tabs,.pd-toolbar,.pd-table-wrap,.enq,.qs,button', clone).forEach(function (n) { n.remove(); });
    return clone.textContent.replace(/\s+/g, ' ').trim();
  }
  function speak() {
    if (!synth) return;
    stopSpeak();
    var text = pageText(); if (!text) return;
    var chunks = text.match(/[^.!?]+[.!?]*\s*/g) || [text], buf = '', parts = [];
    chunks.forEach(function (c) { if ((buf + c).length > 220) { if (buf) parts.push(buf); buf = c; } else buf += c; }); if (buf) parts.push(buf);
    speaking = true; sync();
    parts.forEach(function (t, i) {
      var u = new SpeechSynthesisUtterance(t); u.lang = document.documentElement.lang || 'en'; u.rate = .95;
      if (i === parts.length - 1) u.onend = function () { speaking = false; sync(); };
      u.onerror = function () { speaking = false; sync(); };
      synth.speak(u);
    });
  }
  function stopSpeak() { if (synth) synth.cancel(); speaking = false; }
  window.addEventListener('beforeunload', stopSpeak);

  /* --------------------------------------------------------------- panel */
  var btn, panel, rows = {};
  function sw(k, icon, label, hint) {
    return '<button type="button" class="a11y-sw" role="switch" aria-checked="false" data-k="' + k + '"><i class="bi ' + icon + '" aria-hidden="true"></i>' +
      '<span class="a11y-lab"><b>' + label + '</b>' + (hint ? '<small>' + hint + '</small>' : '') + '</span><span class="a11y-knob" aria-hidden="true"></span></button>';
  }
  function build() {
    btn = document.createElement('button'); btn.type = 'button'; btn.className = 'a11y-btn'; btn.setAttribute('aria-haspopup', 'dialog'); btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-label', 'Accessibility options'); btn.innerHTML = '<i class="bi bi-universal-access" aria-hidden="true"></i><span class="a11y-btn-text">Accessibility</span>';
    document.body.appendChild(btn);

    live = document.createElement('div'); live.className = 'visually-hidden'; live.setAttribute('role', 'status'); live.setAttribute('aria-live', 'polite'); document.body.appendChild(live);

    panel = document.createElement('div'); panel.className = 'a11y-panel'; panel.hidden = true;
    panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-label', 'Accessibility options');
    panel.innerHTML =
      '<header><h2><i class="bi bi-universal-access" aria-hidden="true"></i> Accessibility</h2><button type="button" class="a11y-x" aria-label="Close accessibility options"><i class="bi bi-x-lg"></i></button></header>' +
      '<div class="a11y-body">' +
      '<div class="a11y-size" role="group" aria-label="Text size"><span class="a11y-lab"><b>Text size</b><small id="a11y-zoom-val">100%</small></span>' +
      '<div class="a11y-stepper"><button type="button" data-z="-1" aria-label="Decrease text size"><i class="bi bi-dash-lg"></i></button><button type="button" data-z="1" aria-label="Increase text size"><i class="bi bi-plus-lg"></i></button></div></div>' +
      sw('theme', 'bi-moon-stars-fill', 'Dark theme', 'Easier on the eyes in low light') +
      sw('contrast', 'bi-circle-half', 'High contrast', 'Black background, bold colours and borders') +
      sw('font', 'bi-type', 'Readable font', 'Atkinson Hyperlegible – designed for low vision') +
      sw('spacing', 'bi-arrows-collapse-vertical', 'More spacing', 'Wider letters, words and lines') +
      sw('links', 'bi-highlighter', 'Highlight links', 'Underline and mark every link') +
      sw('cursor', 'bi-cursor-fill', 'Big cursor', 'Larger mouse pointer') +
      sw('guide', 'bi-eye', 'Reading guide', 'A focus band follows your mouse') +
      sw('motion', 'bi-pause-circle', 'Pause animations', 'Stops moving effects and auto-play') +
      sw('sound', 'bi-music-note-beamed', 'Sound effects', 'Soft sounds when you touch or the animation reaches a point') +
      sw('haptics', 'bi-phone-vibrate', 'Vibration', 'Short buzzes on supported phones (Android)') +
      (synth ? sw('speak', 'bi-volume-up-fill', 'Read aloud', 'Reads the page, or the text you select') : '') +
      '</div><footer><button type="button" class="a11y-reset"><i class="bi bi-arrow-counterclockwise"></i> Reset all</button>' +
      '<span>Saved on this device. Press <kbd>Esc</kbd> to close.</span></footer>';
    document.body.appendChild(panel);
    $$('.a11y-sw', panel).forEach(function (b) { rows[b.getAttribute('data-k')] = b; });

    btn.addEventListener('click', function () { panel.hidden ? open() : close(); });
    $('.a11y-x', panel).addEventListener('click', close);
    panel.addEventListener('click', onClick);
    panel.addEventListener('keydown', function (e) {
      if (e.key === 'Tab') {
        var f = $$('button', panel).filter(function (b) { return b.offsetParent !== null; }); if (!f.length) return;
        var first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !panel.hidden) { e.preventDefault(); close(); } });
    document.addEventListener('mousedown', function (e) { if (!panel.hidden && !panel.contains(e.target) && !btn.contains(e.target)) close(true); });
    new MutationObserver(sync).observe(root, { attributes: true, attributeFilter: ['data-theme', 'data-motion'] });
  }

  function onClick(e) {
    var z = e.target.closest('[data-z]');
    if (z) {
      state.zoom = Math.max(0, Math.min(ZOOMS.length - 1, state.zoom + parseInt(z.getAttribute('data-z'), 10)));
      save(); apply(); sync(); announce('Text size ' + ZOOMS[state.zoom] + ' percent'); return;
    }
    if (e.target.closest('.a11y-reset')) { reset(); return; }
    var s = e.target.closest('.a11y-sw'); if (!s) return;
    var k = s.getAttribute('data-k');
    if (k === 'theme') { if (window.SATS && window.SATS.toggleTheme) window.SATS.toggleTheme(); }
    else if (k === 'motion') { window.SATS.setMotion(motionOff()); }
    else if (k === 'speak') { speaking ? stopSpeak() : speak(); sync(); return; }
    else { state[k] = !state[k]; save(); apply(); }
    sync();
    announce(s.querySelector('b').textContent + (s.getAttribute('aria-checked') === 'true' ? ' on' : ' off'));
  }

  function sync() {
    if (!panel) return;
    var on = {
      theme: themeDark(), contrast: state.contrast, font: state.font, spacing: state.spacing, links: state.links, cursor: state.cursor,
      guide: state.guide, motion: motionOff(), speak: speaking, sound: state.sound, haptics: state.haptics
    };
    Object.keys(rows).forEach(function (k) { rows[k].setAttribute('aria-checked', String(!!on[k])); });
    var v = $('#a11y-zoom-val', panel); if (v) v.textContent = ZOOMS[state.zoom] + '%';
    var dec = $('[data-z="-1"]', panel), inc = $('[data-z="1"]', panel);
    if (dec) dec.disabled = state.zoom === 0; if (inc) inc.disabled = state.zoom === ZOOMS.length - 1;
    var changed = state.zoom || state.contrast || state.font || state.spacing || state.links || state.cursor || state.guide || motionOff();
    btn.classList.toggle('active', !!changed);
  }
  function reset() {
    state = { zoom: 0, contrast: false, font: false, spacing: false, links: false, cursor: false, guide: false, sound: true, haptics: true };
    save(); apply(); stopSpeak();
    if (motionOff()) window.SATS.setMotion(true);
    sync(); announce('All accessibility settings reset');
  }
  function open() {
    panel.hidden = false; btn.setAttribute('aria-expanded', 'true');
    requestAnimationFrame(function () { panel.classList.add('show'); });
    var f = $('.a11y-sw', panel); if (f) f.focus();
  }
  function close(skipFocus) {
    if (!panel || panel.hidden) return;
    panel.classList.remove('show'); btn.setAttribute('aria-expanded', 'false');
    setTimeout(function () { panel.hidden = true; }, 200);
    if (skipFocus !== true) btn.focus();
  }

  build(); apply(); sync();
})();

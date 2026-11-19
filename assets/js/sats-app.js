/**
 * SATs v2 – site-wide app features (no dependencies), driven by assets/data/products.json:
 *   1. quick-search overlay   ( / or Ctrl+K or the header search button )
 *   2. enquiry basket         ( add products, then send ONE WhatsApp / email message )
 */
(function () {
  'use strict';
  var root = document.documentElement;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };

  /* ------------------------------------------------------------- data */
  var dataPromise = null;
  function loadProducts() {
    if (!dataPromise) {
      dataPromise = fetch('assets/data/products.json', { cache: 'no-cache' })
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
        .then(function (d) { window.SATS.contact = d.contact || {}; return d.products; });
    }
    return dataPromise;
  }
  window.SATS = window.SATS || {};
  window.SATS.products = loadProducts;

  /* ------------------------------------------------- quick-search overlay */
  var overlay, input, list, products = [], results = [], active = -1, lastFocus = null;

  function build() {
    overlay = document.createElement('div');
    overlay.className = 'qs'; overlay.hidden = true; overlay.setAttribute('role', 'dialog'); overlay.setAttribute('aria-modal', 'true'); overlay.setAttribute('aria-label', 'Search products');
    overlay.innerHTML =
      '<div class="qs-box">' +
      '<div class="qs-input"><i class="bi bi-search" aria-hidden="true"></i>' +
      '<input type="search" role="combobox" aria-expanded="true" aria-controls="qs-list" aria-autocomplete="list" autocomplete="off" placeholder="Search products & specifications…  e.g. vacuum, 1500 °C, battery" aria-label="Search products and specifications">' +
      '<button type="button" class="qs-close" aria-label="Close search">Esc</button></div>' +
      '<ul id="qs-list" class="qs-list" role="listbox" aria-label="Results"></ul>' +
      '<div class="qs-foot"><span><kbd>↑</kbd><kbd>↓</kbd> navigate</span><span><kbd>Enter</kbd> open</span><span><kbd>Esc</kbd> close</span></div>' +
      '</div>';
    document.body.appendChild(overlay);
    input = $('input', overlay); list = $('#qs-list', overlay);
    overlay.addEventListener('mousedown', function (e) { if (e.target === overlay) close(); });
    $('.qs-close', overlay).addEventListener('click', close);
    input.addEventListener('input', render);
    input.addEventListener('keydown', onKey);
    list.addEventListener('mousemove', function (e) {
      var li = e.target.closest('li[data-i]'); if (li) setActive(parseInt(li.getAttribute('data-i'), 10), false);
    });
    list.addEventListener('click', function (e) {
      if (e.target.closest('button')) { setTimeout(function () { input.focus(); }, 0); return; }
      var li = e.target.closest('li[data-i]'); if (li) go(parseInt(li.getAttribute('data-i'), 10));
    });
  }

  function score(p, tokens) {
    var name = (p.name + ' ' + p.title).toLowerCase(), kw = p.keywords.join(' ').toLowerCase(), sh = p.short.toLowerCase(), cat = p.catLabel.toLowerCase();
    var tx = p._tx || (p._tx = (p.text || '').toLowerCase());
    var total = 0;
    for (var i = 0; i < tokens.length; i++) {
      var t = tokens[i], s = 0;
      if (name.indexOf(t) !== -1) s += 6; if (cat.indexOf(t) !== -1) s += 2; if (kw.indexOf(t) !== -1) s += 3; if (sh.indexOf(t) !== -1) s += 2; if (tx.indexOf(t) !== -1) s += 1;
      if (!s) return 0; total += s;
    }
    return total;
  }
  function matchedTerm(p, tokens) {
    for (var k = 0; k < p.keywords.length; k++) {
      var low = p.keywords[k].toLowerCase();
      for (var i = 0; i < tokens.length; i++) if (low.indexOf(tokens[i]) !== -1) return p.keywords[k];
    }
    var tx = p._tx || '';
    for (var i2 = 0; i2 < tokens.length; i2++) {
      var at = tx.indexOf(tokens[i2]);
      if (at !== -1) {
        var from = Math.max(0, at - 38), to = Math.min(p.text.length, at + tokens[i2].length + 46);
        return (from > 0 ? '…' : '') + p.text.slice(from, to).trim() + (to < p.text.length ? '…' : '');
      }
    }
    return '';
  }
  function hl(text, tokens) {
    var out = esc(text);
    tokens.forEach(function (t) { if (t.length > 1) out = out.replace(new RegExp('(' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig'), '<mark>$1</mark>'); });
    return out;
  }

  function render() {
    var q = input.value.trim().toLowerCase(), tokens = q ? q.split(/\s+/) : [];
    results = products.map(function (p) { return { p: p, s: tokens.length ? score(p, tokens) : 1 }; })
      .filter(function (r) { return r.s > 0; }).sort(function (a, b) { return b.s - a.s; });
    if (!results.length) {
      list.innerHTML = '<li class="qs-empty" role="presentation">No product matches “' + esc(input.value.trim()) + '”. Try “probe”, “furnace”, “vacuum” or “battery”.</li>';
      active = -1; return;
    }
    list.innerHTML = results.map(function (r, i) {
      var p = r.p, term = tokens.length ? matchedTerm(p, tokens) : '';
      var thumb = p.image ? '<img src="' + esc(p.image) + '" alt="" loading="lazy" class="' + (p.fit === 'contain' ? 'contain' : '') + '">' : '<span class="qs-ph"><i class="bi bi-robot"></i></span>';
      return '<li role="option" id="qs-o' + i + '" data-i="' + i + '" aria-selected="false">' +
        '<a href="' + esc(encodeURI(p.url)) + '" tabindex="-1">' + thumb +
        '<span class="qs-txt"><strong>' + hl(p.name, tokens) + '</strong><small>' + hl(term ? (term.length < 60 && term.indexOf('…') === -1 && term.indexOf('|') === -1 ? 'Matches: ' + term : term) : p.short, tokens) + '</small></span>' +
        '<span class="qs-cat">' + esc(p.catLabel) + '</span></a>' +
        '<span class="qs-actions"><button type="button" class="enq-add small" data-enq="' + esc(p.key) + '" data-name="' + esc(p.name) + '" aria-pressed="false" aria-label="Add ' + esc(p.name) + ' to enquiry list" title="Add to enquiry list"><i class="bi bi-plus-lg"></i></button></span></li>';
    }).join('');
    setActive(0, false);
    document.dispatchEvent(new CustomEvent('sats:enq-refresh'));
  }

  function setActive(i, scroll) {
    var items = $$('li[data-i]', list); if (!items.length) { active = -1; return; }
    active = Math.max(0, Math.min(items.length - 1, i));
    items.forEach(function (li, n) { var on = n === active; li.classList.toggle('on', on); li.setAttribute('aria-selected', String(on)); });
    input.setAttribute('aria-activedescendant', 'qs-o' + active);
    if (scroll !== false) items[active].scrollIntoView({ block: 'nearest' });
  }
  function go(i) { var r = results[i]; if (r) window.location.href = encodeURI(r.p.url); }
  function onKey(e) {
    if (e.key === 'ArrowDown') { e.preventDefault(); setActive(active + 1); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); setActive(active - 1); }
    else if (e.key === 'Enter') { e.preventDefault(); if (active >= 0) go(active); }
    else if (e.key === 'Escape') { e.preventDefault(); close(); }
    else if (e.key === 'Tab') { e.preventDefault(); }   // keep focus inside the dialog
  }

  function open() {
    if (!overlay) build();
    lastFocus = document.activeElement;
    overlay.hidden = false; document.body.classList.add('qs-open');
    requestAnimationFrame(function () { overlay.classList.add('show'); });
    input.value = ''; input.focus();
    list.innerHTML = '<li class="qs-empty" role="presentation">Loading products…</li>';
    loadProducts().then(function (d) { products = d; render(); input.focus(); })
      .catch(function () { list.innerHTML = '<li class="qs-empty" role="presentation">Search needs the website to be served over http(s). Browse the Products section instead.</li>'; });
  }
  function close() {
    if (!overlay || overlay.hidden) return;
    overlay.classList.remove('show'); document.body.classList.remove('qs-open');
    setTimeout(function () { overlay.hidden = true; }, 180);
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  window.SATS.openSearch = open;
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && overlay && !overlay.hidden) { e.preventDefault(); close(); } });

  document.addEventListener('keydown', function (e) {
    var tag = (document.activeElement && document.activeElement.tagName) || '';
    var typing = /INPUT|TEXTAREA|SELECT/.test(tag) || (document.activeElement && document.activeElement.isContentEditable);
    if ((e.key === '/' && !typing && !e.ctrlKey && !e.metaKey) || ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k')) { e.preventDefault(); open(); }
  });
  $$('[data-open-search]').forEach(function (b) { b.addEventListener('click', open); });
})();

/* ================================================================ enquiry basket */
(function () {
  'use strict';
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };
  var KEY = 'sats-enquiry';
  var state = { items: [], name: '', org: '', notes: '' };      // items: [{key, name}]
  var panel, fab, lastFocus = null, catalog = {};

  function load() { try { var d = JSON.parse(localStorage.getItem(KEY) || '{}'); if (d && Array.isArray(d.items)) state = { items: d.items, name: d.name || '', org: d.org || '', notes: d.notes || '' }; } catch (e) {} }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} }
  function has(key) { return state.items.some(function (i) { return i.key === key; }); }
  function toggle(key, name) {
    if (has(key)) state.items = state.items.filter(function (i) { return i.key !== key; });
    else state.items.push({ key: key, name: name || key });
    save(); sync(true);
  }

  /* all "add" buttons on the page reflect the list */
  function refreshButtons() {
    $$('[data-enq]').forEach(function (b) {
      var on = has(b.getAttribute('data-enq')), name = b.getAttribute('data-name') || '';
      b.setAttribute('aria-pressed', String(on));
      b.classList.toggle('added', on);
      var ic = $('i', b), lab = $('.enq-label', b);
      if (ic) ic.className = 'bi ' + (b.classList.contains('btn-sats') ? (on ? 'bi-check-circle-fill' : 'bi-plus-circle') : (on ? 'bi-check2' : 'bi-plus-lg'));
      if (lab) lab.textContent = on ? 'Added to enquiry list' : 'Add to enquiry list';
      b.setAttribute('aria-label', (on ? 'Remove ' : 'Add ') + name + (on ? ' from' : ' to') + ' enquiry list');
      b.title = on ? 'Remove from enquiry list' : 'Add to enquiry list';
    });
  }
  function ensureFab() {
    if (fab) return fab;
    fab = document.createElement('button'); fab.type = 'button'; fab.className = 'enq-fab'; fab.setAttribute('aria-haspopup', 'dialog');
    fab.innerHTML = '<i class="bi bi-clipboard2-check" aria-hidden="true"></i><span class="enq-fab-text">Enquiry list</span><span class="enq-count" aria-hidden="true">0</span>';
    fab.addEventListener('click', openPanel); document.body.appendChild(fab); return fab;
  }
  function updateFab(pop) {
    var n = state.items.length; ensureFab();
    fab.hidden = n === 0;
    $('.enq-count', fab).textContent = String(n);
    fab.setAttribute('aria-label', 'Open enquiry list, ' + n + (n === 1 ? ' product' : ' products'));
    if (pop) { fab.classList.remove('pop'); void fab.offsetWidth; fab.classList.add('pop'); }
  }
  function sync(pop) { refreshButtons(); updateFab(pop); if (panel && !panel.hidden) renderPanel(); }

  /* ------------------------------------------------------------ message */
  function message() {
    var L = ['Hello SATs, I would like a quote / more details for:'];
    state.items.forEach(function (i, n) { L.push((n + 1) + '. ' + i.name); });
    L.push('');
    if (state.name) L.push('Name: ' + state.name);
    if (state.org) L.push('Organisation: ' + state.org);
    if (state.notes) L.push('Notes: ' + state.notes);
    L.push('Sent from the SATs website.');
    return L.join('\n');
  }

  /* -------------------------------------------------------------- panel */
  function buildPanel() {
    panel = document.createElement('div');
    panel.className = 'enq'; panel.hidden = true; panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-modal', 'true'); panel.setAttribute('aria-labelledby', 'enq-title');
    panel.innerHTML =
      '<div class="enq-panel"><header><h2 id="enq-title"><i class="bi bi-clipboard2-check" aria-hidden="true"></i> Your enquiry list</h2>' +
      '<button type="button" class="enq-x" aria-label="Close enquiry list"><i class="bi bi-x-lg"></i></button></header>' +
      '<div class="enq-body"><p class="enq-hint">Choose the products you are interested in, add your details, and send <b>one</b> message to the SATs team.</p>' +
      '<ul class="enq-items" aria-live="polite"></ul>' +
      '<div class="enq-form"><label>Your name<input type="text" data-f="name" autocomplete="name"></label>' +
      '<label>Organisation <small>(optional)</small><input type="text" data-f="org" autocomplete="organization"></label>' +
      '<label>Notes <small>(optional)</small><textarea rows="3" data-f="notes" placeholder="Samples, temperature range, quantity…"></textarea></label></div>' +
      '<details class="enq-preview"><summary>Preview message</summary><pre></pre></details></div>' +
      '<footer class="enq-actions"><a class="btn-sats btn-sats-wa" data-act="wa" target="_blank" rel="noopener noreferrer"><i class="bi bi-whatsapp"></i> Send on WhatsApp</a>' +
      '<a class="btn-sats btn-sats-primary" data-act="mail"><i class="bi bi-envelope-fill"></i> Send by email</a>' +
      '<div class="enq-small"><button type="button" class="btn-link-sats" data-act="copy"><i class="bi bi-clipboard"></i> Copy message</button>' +
      '<button type="button" class="btn-link-sats" data-act="clear"><i class="bi bi-trash3"></i> Clear list</button></div></footer></div>';
    document.body.appendChild(panel);
    panel.addEventListener('mousedown', function (e) { if (e.target === panel) closePanel(); });
    $('.enq-x', panel).addEventListener('click', closePanel);
    panel.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { e.preventDefault(); closePanel(); }
      if (e.key === 'Tab') {   // focus trap
        var f = $$('button:not([disabled]), a[href], input, textarea, summary', panel).filter(function (el) { return el.offsetParent !== null; });
        if (!f.length) return; var first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
    $$('[data-f]', panel).forEach(function (el) { el.addEventListener('input', function () { state[el.getAttribute('data-f')] = el.value; save(); links(); }); });
    panel.addEventListener('click', function (e) {
      var rm = e.target.closest('[data-remove]'); if (rm) { toggle(rm.getAttribute('data-remove')); return; }
      var act = e.target.closest('[data-act]'); if (!act) return;
      var a = act.getAttribute('data-act');
      if (a === 'clear') { state.items = []; save(); sync(false); }
      if (a === 'copy') {
        var done = function () { var o = act.innerHTML; act.innerHTML = '<i class="bi bi-check2"></i> Copied'; setTimeout(function () { act.innerHTML = o; }, 1600); };
        if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(message()).then(done);
        else { var ta = document.createElement('textarea'); ta.value = message(); document.body.appendChild(ta); ta.select(); try { document.execCommand('copy'); done(); } catch (er) {} ta.remove(); }
      }
    });
  }
  function links() {
    var c = window.SATS.contact || {}, msg = message();
    var wa = $('[data-act=wa]', panel), mail = $('[data-act=mail]', panel), n = state.items.length;
    wa.href = 'https://wa.me/' + (c.wa || '') + '?text=' + encodeURIComponent(msg);
    mail.href = 'mailto:' + (c.email || '') + '?subject=' + encodeURIComponent('Enquiry from SATs website (' + n + (n === 1 ? ' product' : ' products') + ')') + '&body=' + encodeURIComponent(msg);
    [wa, mail].forEach(function (a) { a.classList.toggle('disabled', !n); a.setAttribute('aria-disabled', String(!n)); });
    $('pre', panel).textContent = msg;
  }
  function renderPanel() {
    var ul = $('.enq-items', panel), n = state.items.length;
    ul.innerHTML = n ? state.items.map(function (i) {
      var c = catalog[i.key] || {}, thumb = c.image ? '<img src="' + esc(c.image) + '" alt="" class="' + (c.fit === 'contain' ? 'contain' : '') + '">' : '<span class="qs-ph"><i class="bi bi-robot"></i></span>';
      return '<li>' + thumb + '<span><strong>' + esc(i.name) + '</strong>' + (c.catLabel ? '<small>' + esc(c.catLabel) + '</small>' : '') + '</span>' +
        '<button type="button" class="enq-rm" data-remove="' + esc(i.key) + '" aria-label="Remove ' + esc(i.name) + '"><i class="bi bi-x-lg"></i></button></li>';
    }).join('') : '<li class="enq-empty">Your list is empty. Use the <i class="bi bi-plus-lg"></i> button on any product to add it.</li>';
    $$('[data-f]', panel).forEach(function (el) { if (document.activeElement !== el) el.value = state[el.getAttribute('data-f')] || ''; });
    $('.enq-actions', panel).classList.toggle('empty', !n);
    links();
    if (!panel.hidden && (!document.activeElement || document.activeElement === document.body)) { var x = $('.enq-x', panel); if (x) x.focus(); }
  }
  function openPanel() {
    if (!panel) buildPanel();
    lastFocus = document.activeElement; renderPanel();
    panel.hidden = false; document.body.classList.add('qs-open');
    requestAnimationFrame(function () { panel.classList.add('show'); });
    var f = $('[data-f=name]', panel); if (f) f.focus();
    if (window.SATS.products) window.SATS.products().then(function (list) { list.forEach(function (p) { catalog[p.key] = p; }); renderPanel(); links(); }).catch(function () {});
  }
  function closePanel() {
    if (!panel || panel.hidden) return;
    panel.classList.remove('show'); document.body.classList.remove('qs-open');
    setTimeout(function () { panel.hidden = true; }, 220);
    if (lastFocus && lastFocus.focus && document.contains(lastFocus)) lastFocus.focus();
  }
  window.SATS.openEnquiry = openPanel;
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && panel && !panel.hidden) { e.preventDefault(); closePanel(); } });

  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-enq]'); if (!b) return;
    e.preventDefault(); e.stopPropagation();
    toggle(b.getAttribute('data-enq'), b.getAttribute('data-name'));
  });
  document.addEventListener('sats:enq-refresh', refreshButtons);
  window.addEventListener('storage', function (e) { if (e.key === KEY) { load(); sync(false); } });

  load(); sync(false);
})();

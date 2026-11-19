/**
 * SATs v2 – LinkedIn corner (no dependencies).
 * Reads assets/data/linkedin-posts.json. With no posts, only the "Follow on LinkedIn" card is shown.
 * Posts are official LinkedIn embeds; they load only after the visitor clicks "Load LinkedIn posts" (privacy).
 */
(function () {
  'use strict';
  var wrap = document.getElementById('linkedin-posts'); if (!wrap) return;
  var row = wrap.parentNode, KEY = 'sats-linkedin', feed = document.getElementById('linkedin-feed');
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };

  fetch('assets/data/linkedin-posts.json', { cache: 'no-cache' }).then(function (r) { return r.json(); }).then(function (d) {
    var w = d.widget && /^(elfsight|sociablekit)$/.test(d.widget.provider || '') && /^[A-Za-z0-9_-]{4,64}$/.test(d.widget.id || '') ? d.widget : null;
    var posts = (d.posts || []).filter(function (p) { return /^https:\/\/www\.linkedin\.com\/embed\/feed\/update\//.test(p.embed || ''); });
    if (!w && !posts.length) return;                   // nothing to show: keep the profile card only
    row.classList.remove('no-posts'); wrap.hidden = false;
    var remembered = d.autoload !== false;             // default: show immediately, no click (set "autoload": false for a consent step)
    try { if (localStorage.getItem(KEY) === 'yes') remembered = true; } catch (e) {}
    var go = w ? function () { widget(w); } : function () { load(posts); };
    remembered ? go() : gate(posts.length || 1, go);
  }).catch(function () {});

  function gate(n, go) {
    feed.innerHTML = '<div class="li-gate"><i class="bi bi-shield-lock" aria-hidden="true"></i>' +
      '<p>Our latest LinkedIn posts load from LinkedIn’s servers, which may set cookies.</p>' +
      '<button type="button" class="btn-sats btn-sats-primary" id="li-load"><i class="bi bi-linkedin"></i> Load LinkedIn posts</button></div>';
    document.getElementById('li-load').addEventListener('click', function () {
      try { localStorage.setItem(KEY, 'yes'); } catch (e) {}
      go();
    });
  }
  function addScript(src) { if (document.querySelector('script[src="' + src + '"]')) return; var s = document.createElement('script'); s.src = src; s.async = true; document.body.appendChild(s); }
  function widget(w) {   // live feed from a widget service (account + widget id supplied by the site owner)
    if (w.provider === 'elfsight') { feed.innerHTML = '<div class="elfsight-app-' + w.id + '" data-elfsight-app-lazy></div>'; addScript('https://static.elfsight.com/platform/platform.js'); }
    else { feed.innerHTML = '<div class="sk-ww-linkedin-page-posts" data-embed-id="' + w.id + '"></div>'; addScript('https://widgets.sociablekit.com/linkedin-page-posts/widget.js'); }
  }
  function load(posts) {
    feed.innerHTML = '<div class="li-track" tabindex="0" role="region" aria-label="LinkedIn posts">' + posts.map(function (p, i) {
      return '<div class="li-slide"><iframe src="' + esc(p.embed) + '" title="' + esc(p.title || ('SATs LinkedIn post ' + (i + 1))) + '" loading="lazy" allowfullscreen></iframe></div>';
    }).join('') + '</div>' +
      (posts.length > 1 ? '<div class="li-nav"><button type="button" data-d="-1" aria-label="Previous post"><i class="bi bi-chevron-left"></i></button>' +
        '<button type="button" data-d="1" aria-label="Next post"><i class="bi bi-chevron-right"></i></button></div>' : '');
    var track = feed.querySelector('.li-track');
    feed.querySelectorAll('.li-nav button').forEach(function (b) {
      b.addEventListener('click', function () {
        var step = (track.querySelector('.li-slide') || { offsetWidth: 360 }).offsetWidth + 16;
        track.scrollBy({ left: step * parseInt(b.getAttribute('data-d'), 10), behavior: document.documentElement.getAttribute('data-motion') === 'reduced' ? 'auto' : 'smooth' });
      });
    });
  }
})();

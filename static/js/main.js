/* ==========================================================================
   Grace & Truth Community Church — site behaviour
   Vanilla JS, no build step. Bootstrap 5 handles offcanvas / modal / accordion.
   ========================================================================== */
(function () {
  'use strict';

  /* ------------------------------------------------------------------
     Reveal on scroll
     ------------------------------------------------------------------ */
  function initReveal() {
    var items = document.querySelectorAll('.reveal');
    if (!items.length) return;

    var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced || !('IntersectionObserver' in window)) {
      items.forEach(function (el) { el.classList.add('is-visible'); });
      return;
    }

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        io.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });

    items.forEach(function (el, i) {
      el.style.transitionDelay = Math.min(i % 4, 3) * 70 + 'ms';
      io.observe(el);
    });
  }

  /* ------------------------------------------------------------------
     Filter chip groups
     A group is any [data-filter-group="name"] container of
     [data-filter="value"] buttons. Items live in
     [data-filter-target="name"] and carry data-tags="a b c".
     ------------------------------------------------------------------ */
  function initFilters() {
    document.querySelectorAll('[data-filter-group]').forEach(function (group) {
      var name = group.dataset.filterGroup;
      var pool = document.querySelectorAll('[data-filter-target="' + name + '"] [data-tags]');
      var empty = document.querySelector('[data-filter-empty="' + name + '"]');

      group.addEventListener('click', function (ev) {
        var btn = ev.target.closest('[data-filter]');
        if (!btn) return;

        group.querySelectorAll('[data-filter]').forEach(function (b) {
          b.classList.toggle('is-active', b === btn);
          b.setAttribute('aria-pressed', b === btn ? 'true' : 'false');
        });

        var want = btn.dataset.filter;
        var shown = 0;

        pool.forEach(function (item) {
          var tags = (item.dataset.tags || '').split(/\s+/);
          var match = want === 'all' || tags.indexOf(want) !== -1;
          var host = item.closest('[data-filter-item]') || item;
          host.hidden = !match;
          if (match) shown++;
        });

        if (empty) empty.hidden = shown !== 0;
      });
    });
  }

  /* ------------------------------------------------------------------
     Search box filtering (sermon library, events)
     ------------------------------------------------------------------ */
  function initSearch() {
    document.querySelectorAll('[data-search-target]').forEach(function (input) {
      var name = input.dataset.searchTarget;
      var pool = document.querySelectorAll('[data-filter-target="' + name + '"] [data-tags]');
      var empty = document.querySelector('[data-filter-empty="' + name + '"]');

      input.addEventListener('input', function () {
        var q = input.value.trim().toLowerCase();
        var shown = 0;

        pool.forEach(function (item) {
          var host = item.closest('[data-filter-item]') || item;
          var hay = (item.textContent || '').toLowerCase();
          var match = !q || hay.indexOf(q) !== -1;
          host.hidden = !match;
          if (match) shown++;
        });

        if (empty) empty.hidden = shown !== 0;
      });
    });
  }

  /* ------------------------------------------------------------------
     Demo media players — toggle icon + progress, no real audio wired up
     ------------------------------------------------------------------ */
  function initPlayers() {
    document.querySelectorAll('[data-player]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var icon = btn.querySelector('.material-symbols-outlined');
        var playing = btn.dataset.playing === 'true';
        btn.dataset.playing = playing ? 'false' : 'true';
        if (icon) icon.textContent = playing ? 'play_arrow' : 'pause';
        btn.setAttribute('aria-label', playing ? 'Play' : 'Pause');
      });
    });
  }

  /* ------------------------------------------------------------------
     Forms — no backend on a static site, so confirm politely in place.
     Swap the body of handle() for a real POST when hosting is chosen.
     ------------------------------------------------------------------ */
  function initForms() {
    document.querySelectorAll('form[data-demo-form]').forEach(function (form) {
      form.addEventListener('submit', function (ev) {
        ev.preventDefault();

        if (!form.checkValidity()) {
          form.classList.add('was-validated');
          return;
        }

        var note = form.querySelector('[data-form-note]');
        var message = form.dataset.demoForm ||
          'Thank you — your message has been received. A member of our team will reply shortly.';

        if (note) {
          note.textContent = message;
          note.hidden = false;
          note.setAttribute('role', 'status');
        }

        form.reset();
        form.classList.remove('was-validated');

        var modalEl = form.closest('.modal');
        if (modalEl && window.bootstrap) {
          window.setTimeout(function () {
            var inst = window.bootstrap.Modal.getInstance(modalEl);
            if (inst) inst.hide();
            if (note) note.hidden = true;
          }, 2200);
        }
      });
    });
  }

  /* ------------------------------------------------------------------
     Header shadow once the page scrolls away from the top
     ------------------------------------------------------------------ */
  function initHeaderShadow() {
    var header = document.querySelector('.site-header');
    if (!header) return;

    var tick = function () {
      header.style.boxShadow = window.scrollY > 8
        ? '0 10px 30px -18px rgba(30, 58, 47, .45)'
        : 'none';
    };

    tick();
    window.addEventListener('scroll', tick, { passive: true });
  }

  /* ------------------------------------------------------------------
     Current year in the footer
     ------------------------------------------------------------------ */
  function initYear() {
    document.querySelectorAll('[data-year]').forEach(function (el) {
      el.textContent = new Date().getFullYear();
    });
  }


  /* ------------------------------------------------------------------
     Gallery lightbox — opens the full photo in a modal
     ------------------------------------------------------------------ */
  function initLightbox() {
    var modalEl = document.getElementById('lightboxModal');
    if (!modalEl || !window.bootstrap) return;

    var imgEl = modalEl.querySelector('[data-lightbox-img]');
    var capEl = modalEl.querySelector('[data-lightbox-caption]');

    document.querySelectorAll('[data-lightbox]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var thumb = btn.querySelector('img');
        imgEl.src = btn.getAttribute('data-lightbox') || (thumb && thumb.src) || '';
        imgEl.alt = (thumb && thumb.alt) || '';
        if (capEl) capEl.textContent = btn.getAttribute('data-caption') || '';
        window.bootstrap.Modal.getOrCreateInstance(modalEl).show();
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initReveal();
    initFilters();
    initSearch();
    initPlayers();
    initForms();
    initLightbox();
    initHeaderShadow();
    initYear();
  });
})();

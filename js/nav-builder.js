'use strict';
/* ══════════════════════════════════════════════════
   NAV BUILDER — data-driven navigation from nav.json
   Renders desktop nav-links, mobile drawer, and
   handles dropdown toggle + hamburger menu.
   ══════════════════════════════════════════════════ */
(function () {
  const CURRENT_PAGE = location.pathname.split('/').pop() || 'index.html';

  function isActive(href) { return href === CURRENT_PAGE; }
  function isGroupActive(children) { return children.some(c => isActive(c.href)); }
  function label(item) { return item.zh; } // default; i18n.js will override via data-i18n

  /* ── Desktop nav-links (<ul>) ── */
  function buildDesktopNav(items) {
    const ul = document.querySelector('.nav-links');
    if (!ul) return;
    ul.innerHTML = '';

    items.forEach(item => {
      const li = document.createElement('li');

      if (item.children) {
        // Dropdown group
        li.className = 'nav-dropdown';
        const trigger = document.createElement('a');
        trigger.href = item.children[0].href;
        trigger.className = 'nav-dropdown-trigger' + (isGroupActive(item.children) ? ' active' : '');
        trigger.setAttribute('data-i18n', item.i18n);
        trigger.textContent = label(item) + ' ▾';

        const subUl = document.createElement('ul');
        subUl.className = 'nav-dropdown-menu';
        item.children.forEach(child => {
          const subLi = document.createElement('li');
          const a = document.createElement('a');
          a.href = child.href;
          a.setAttribute('data-i18n', child.i18n);
          a.textContent = label(child);
          if (isActive(child.href)) a.className = 'active';
          subLi.appendChild(a);
          subUl.appendChild(subLi);
        });

        li.appendChild(trigger);
        li.appendChild(subUl);
      } else {
        // Simple link
        const a = document.createElement('a');
        a.href = item.href;
        a.setAttribute('data-i18n', item.i18n);
        a.textContent = label(item);
        if (isActive(item.href)) a.className = 'active';
        li.appendChild(a);
      }

      ul.appendChild(li);
    });
  }

  /* ── Mobile drawer ── */
  function buildDrawerNav(items) {
    const drawer = document.getElementById('nav-drawer');
    if (!drawer) return;

    // Keep the close button, remove everything else
    const closeBtn = drawer.querySelector('.nav-drawer-close');
    drawer.innerHTML = '';
    if (closeBtn) drawer.appendChild(closeBtn);

    items.forEach(item => {
      if (item.children) {
        const group = document.createElement('div');
        group.className = 'nav-drawer-group';
        const lbl = document.createElement('span');
        lbl.className = 'nav-drawer-group-label';
        lbl.setAttribute('data-i18n', item.i18n);
        lbl.textContent = label(item);
        group.appendChild(lbl);

        item.children.forEach(child => {
          const a = document.createElement('a');
          a.href = child.href;
          a.className = 'nav-drawer-sub' + (isActive(child.href) ? ' active' : '');
          a.setAttribute('data-i18n', child.i18n);
          a.textContent = label(child);
          group.appendChild(a);
        });
        drawer.appendChild(group);
      } else {
        const a = document.createElement('a');
        a.href = item.href;
        a.setAttribute('data-i18n', item.i18n);
        a.textContent = label(item);
        if (isActive(item.href)) a.className = 'active';
        drawer.appendChild(a);
      }
    });
  }

  /* ── Dropdown click toggle ── */
  function initDropdownToggle() {
    document.querySelectorAll('.nav-dropdown-trigger').forEach(trigger => {
      trigger.addEventListener('click', e => {
        e.preventDefault();
        e.stopPropagation();
        const dd = trigger.closest('.nav-dropdown');
        const wasOpen = dd.classList.contains('open');
        document.querySelectorAll('.nav-dropdown.open').forEach(d => d.classList.remove('open'));
        if (!wasOpen) dd.classList.add('open');
      });
    });
    document.addEventListener('click', e => {
      if (!e.target.closest('.nav-dropdown')) {
        document.querySelectorAll('.nav-dropdown.open').forEach(d => d.classList.remove('open'));
      }
    });
  }

  /* ── Hamburger menu ── */
  function initHamburger() {
    const hamburger = document.getElementById('nav-hamburger');
    const drawer = document.getElementById('nav-drawer');
    const overlay = document.getElementById('nav-overlay');
    const closeBtn = document.getElementById('nav-drawer-close');
    if (!hamburger || !drawer || !overlay) return;

    function openDrawer() {
      hamburger.classList.add('open');
      drawer.classList.add('open');
      overlay.classList.add('open');
      document.body.style.overflow = 'hidden';
    }
    function closeDrawer() {
      hamburger.classList.remove('open');
      drawer.classList.remove('open');
      overlay.classList.remove('open');
      document.body.style.overflow = '';
    }

    hamburger.addEventListener('click', () =>
      drawer.classList.contains('open') ? closeDrawer() : openDrawer()
    );
    overlay.addEventListener('click', closeDrawer);
    if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
    drawer.querySelectorAll('a').forEach(a => a.addEventListener('click', closeDrawer));
  }

  /* ── Re-apply i18n after nav build ── */
  function refreshI18n() {
    if (typeof window.applyI18n === 'function') {
      window.applyI18n();
    }
  }

  /* ════════════════════════════════
     FULL-SITE SEARCH (Fuse.js)
  ════════════════════════════════ */
  let _fuse = null;
  let _searchIndex = null;
  let _fuseLoading = false;

  function getLang() { return localStorage.getItem('mib-lang') || 'zh'; }

  function getTypeLabel(type) {
    const lang = getLang();
    const map = {
      diary:      lang === 'zh' ? '任务日志' : 'Diary',
      experiment: lang === 'zh' ? '实验'     : 'Experiment',
      article:    lang === 'zh' ? '文章'     : 'Article'
    };
    return map[type] || type;
  }

  async function loadFuse() {
    if (_fuse) return _fuse;
    if (_fuseLoading) return null;
    _fuseLoading = true;

    // Load Fuse.js from CDN
    await new Promise((resolve, reject) => {
      if (window.Fuse) return resolve();
      const s = document.createElement('script');
      s.src = 'https://cdn.jsdelivr.net/npm/fuse.js@7.0.0/dist/fuse.min.js';
      s.onload = resolve;
      s.onerror = reject;
      document.head.appendChild(s);
    });

    // Load search index
    const resp = await fetch('data/search-index.json?v=' + Date.now());
    _searchIndex = await resp.json();

    const lang = getLang();
    const titleKey = lang === 'zh' ? 'title_zh' : 'title_en';
    const contentKey = lang === 'zh' ? 'content_zh' : 'content_en';

    _fuse = new Fuse(_searchIndex, {
      keys: [
        { name: titleKey, weight: 2 },
        { name: contentKey, weight: 1 },
        { name: 'tags', weight: 1.5 },
        { name: 'codename', weight: 1 }
      ],
      threshold: 0.35,
      includeMatches: true,
      minMatchCharLength: 2
    });

    _fuseLoading = false;
    return _fuse;
  }

  function createSearchModal() {
    // Overlay
    const overlay = document.createElement('div');
    overlay.className = 'search-overlay';
    overlay.id = 'search-overlay';

    const lang = getLang();
    const placeholder = lang === 'zh'
      ? '搜索日记、实验、文章...'
      : 'Search diary, experiments, articles...';

    overlay.innerHTML = `
      <div class="search-container">
        <div class="search-input-wrap">
          <span class="search-input-icon">🔍</span>
          <input class="search-input" id="search-input" type="text"
            placeholder="${placeholder}" autocomplete="off" />
          <span class="search-kbd">ESC</span>
        </div>
        <div class="search-results" id="search-results">
          <div class="search-empty">
            <span class="icon">🔍</span>
            ${lang === 'zh' ? '输入关键词开始搜索' : 'Type to search'}
          </div>
        </div>
        <div class="search-footer">POWERED BY FUSE.JS · AGENT J SEARCH</div>
      </div>
    `;

    document.body.appendChild(overlay);

    const input = document.getElementById('search-input');
    const results = document.getElementById('search-results');

    // Close on overlay click
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) closeSearch();
    });

    // ESC to close
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && overlay.classList.contains('open')) {
        closeSearch();
      }
    });

    // Debounced search
    let _timer = null;
    input.addEventListener('input', () => {
      clearTimeout(_timer);
      _timer = setTimeout(() => doSearch(input.value.trim()), 200);
    });

    return overlay;
  }

  async function doSearch(query) {
    const results = document.getElementById('search-results');
    if (!results) return;
    const lang = getLang();

    if (!query || query.length < 2) {
      results.innerHTML = `<div class="search-empty"><span class="icon">🔍</span>${lang === 'zh' ? '输入关键词开始搜索' : 'Type to search'}</div>`;
      return;
    }

    const fuse = await loadFuse();
    if (!fuse) {
      results.innerHTML = `<div class="search-empty"><span class="icon">⚠️</span>${lang === 'zh' ? '搜索索引加载中...' : 'Loading search index...'}</div>`;
      return;
    }

    const titleKey = lang === 'zh' ? 'title_zh' : 'title_en';
    const contentKey = lang === 'zh' ? 'content_zh' : 'content_en';
    const hits = fuse.search(query, { limit: 15 });

    if (hits.length === 0) {
      results.innerHTML = `<div class="search-empty"><span class="icon">💭</span>${lang === 'zh' ? '未找到相关内容' : 'No results found'}</div>`;
      return;
    }

    let html = '';
    hits.forEach(hit => {
      const item = hit.item;
      const title = item[titleKey] || item.title_zh || '';
      const content = item[contentKey] || item.content_zh || '';
      const snippet = content.length > 120 ? content.substring(0, 120) + '…' : content;
      const codename = item.codename ? `[${item.codename}] ` : '';

      html += `<a class="search-result-item" href="${item.url}">
        <div class="search-result-top">
          <span class="search-result-type ${item.type}">${getTypeLabel(item.type)}</span>
          <span class="search-result-date">${item.date || ''}</span>
        </div>
        <div class="search-result-title">${codename}${title}</div>
        ${snippet ? `<div class="search-result-snippet">${snippet}</div>` : ''}
      </a>`;
    });

    results.innerHTML = html;
  }

  function openSearch() {
    let overlay = document.getElementById('search-overlay');
    if (!overlay) overlay = createSearchModal();
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
    setTimeout(() => {
      const input = document.getElementById('search-input');
      if (input) input.focus();
    }, 100);
    // Preload Fuse
    loadFuse();
  }

  function closeSearch() {
    const overlay = document.getElementById('search-overlay');
    if (overlay) {
      overlay.classList.remove('open');
      document.body.style.overflow = '';
      const input = document.getElementById('search-input');
      if (input) { input.value = ''; }
      const results = document.getElementById('search-results');
      const lang = getLang();
      if (results) results.innerHTML = `<div class="search-empty"><span class="icon">🔍</span>${lang === 'zh' ? '输入关键词开始搜索' : 'Type to search'}</div>`;
    }
  }

  // Expose globally
  window.openSearch = openSearch;
  window.closeSearch = closeSearch;

  function initSearchButton() {
    // Add search button to nav (before lang-toggle)
    const langBtn = document.getElementById('lang-toggle');
    if (!langBtn) return;

    const btn = document.createElement('button');
    btn.className = 'nav-search-btn';
    btn.id = 'nav-search-btn';
    const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
    btn.innerHTML = `🔍 <span class="search-hint">${isMac ? '⌘K' : 'Ctrl+K'}</span>`;
    btn.addEventListener('click', openSearch);
    langBtn.parentNode.insertBefore(btn, langBtn);

    // Cmd/Ctrl+K shortcut
    document.addEventListener('keydown', (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        openSearch();
      }
    });
  }

  /* ── Init ── */
  async function init() {
    try {
      const resp = await fetch('data/nav.json');
      if (!resp.ok) throw new Error('nav.json ' + resp.status);
      const items = await resp.json();

      buildDesktopNav(items);
      buildDrawerNav(items);
      initDropdownToggle();
      initHamburger();
      initSearchButton();
      refreshI18n();
    } catch (err) {
      console.warn('[nav-builder] Failed to load nav.json, using static fallback:', err);
      // Static nav in HTML serves as fallback — just init interactions
      initDropdownToggle();
      initHamburger();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

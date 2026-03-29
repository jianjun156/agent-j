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

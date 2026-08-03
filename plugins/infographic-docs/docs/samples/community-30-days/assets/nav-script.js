/* ============================================================
   infographic-docs · shared client script
   ----------------------------------------------------------
   Copy this file into <output-dir>/assets/nav-script.js
   and reference it from each page via:
     <script src="assets/nav-script.js"></script>

   Provides four behaviors, all opt-in via DOM markers:

   1. Fade-up on scroll
        Any element with class .fade-up animates into view when
        it intersects the viewport. Add .stagger-1 ... .stagger-5
        for delays.

   2. Interactive shadcn-style tabs
        Any element with [data-tabs] and children with
        [data-tab-target] switches matching tabpanels by id.

   3. Copy snippet buttons
        Any button with [data-copy-target] copies the textContent
        of the matching element id.

   4. Active page-nav dot
        If a <nav class="page-nav"> exists with <a href="#id">
        children, the dot matching the currently-visible
        <section class="page" id="..."> or
        <section class="sg-section" id="..."> gets .active.
   ============================================================ */

(function () {
  'use strict';

  // --- Lucide icons ---------------------------------------------
  if (window.lucide && typeof window.lucide.createIcons === 'function') {
    window.lucide.createIcons();
  }

  // --- Fade-up on scroll -----------------------------------------
  var fadeEls = document.querySelectorAll('.fade-up');
  if (fadeEls.length && 'IntersectionObserver' in window) {
    var fadeObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add('visible');
          fadeObserver.unobserve(e.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -10% 0px' });
    fadeEls.forEach(function (el) { fadeObserver.observe(el); });
  } else {
    // No IO support: just show everything.
    fadeEls.forEach(function (el) { el.classList.add('visible'); });
  }

  // --- Interactive primitive tabs -------------------------------
  var tabGroups = document.querySelectorAll('[data-tabs]');
  tabGroups.forEach(function (group) {
    var triggers = Array.prototype.slice.call(group.querySelectorAll('[role="tab"][data-tab-target]'));
    var panels = Array.prototype.slice.call(group.querySelectorAll('[role="tabpanel"]'));
    if (!triggers.length || !panels.length) return;

    function activateTab(trigger, shouldFocus) {
      var targetId = trigger.getAttribute('data-tab-target');
      triggers.forEach(function (tab) {
        var isActive = tab === trigger;
        tab.classList.toggle('active', isActive);
        tab.setAttribute('aria-selected', isActive ? 'true' : 'false');
        tab.setAttribute('tabindex', isActive ? '0' : '-1');
      });
      panels.forEach(function (panel) {
        var isActive = panel.id === targetId;
        panel.classList.toggle('active', isActive);
        panel.hidden = !isActive;
      });
      if (shouldFocus) trigger.focus();
    }

    triggers.forEach(function (trigger, index) {
      trigger.addEventListener('click', function () {
        activateTab(trigger, false);
      });
      trigger.addEventListener('keydown', function (event) {
        var nextIndex = index;
        if (event.key === 'ArrowRight') nextIndex = (index + 1) % triggers.length;
        if (event.key === 'ArrowLeft') nextIndex = (index - 1 + triggers.length) % triggers.length;
        if (event.key === 'Home') nextIndex = 0;
        if (event.key === 'End') nextIndex = triggers.length - 1;
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          activateTab(trigger, false);
          return;
        }
        if (nextIndex !== index) {
          event.preventDefault();
          activateTab(triggers[nextIndex], true);
        }
      });
    });
  });

  // --- Copy snippet buttons --------------------------------------
  var copyButtons = document.querySelectorAll('[data-copy-target]');
  copyButtons.forEach(function (button) {
    var defaultLabel = button.textContent.trim();
    button.addEventListener('click', function () {
      var target = document.getElementById(button.getAttribute('data-copy-target'));
      if (!target) return;
      var text = target.textContent;

      function markCopied() {
        button.dataset.copied = 'true';
        button.lastChild.nodeValue = ' Copied';
        window.setTimeout(function () {
          button.dataset.copied = 'false';
          button.lastChild.nodeValue = ' ' + defaultLabel.replace(/^.*Copy$/, 'Copy');
        }, 1400);
      }

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(markCopied).catch(function () {});
      } else {
        var textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.setAttribute('readonly', '');
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        try {
          document.execCommand('copy');
          markCopied();
        } catch (err) {}
        document.body.removeChild(textarea);
      }
    });
  });

  // --- Active page-nav dot ---------------------------------------
  var pageNav = document.querySelector('.page-nav');
  if (pageNav && 'IntersectionObserver' in window) {
    var pages = document.querySelectorAll('section.page[id], section.sg-section[id]');
    var navLinks = pageNav.querySelectorAll('a[href^="#"]');
    if (pages.length && navLinks.length) {
      var navObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            navLinks.forEach(function (l) { l.classList.remove('active'); });
            var id = e.target.id;
            var link = pageNav.querySelector('a[href="#' + id + '"]');
            if (link) link.classList.add('active');
          }
        });
      }, { threshold: 0.5 });
      pages.forEach(function (p) { navObserver.observe(p); });
    }
  }
})();

/* ============================================
   core_v2.js — Woosdom Command Center v2
   Theme toggle, clock, department collapse
   ============================================ */

(function () {
  'use strict';

  // ── Theme Toggle ──
  var toggle = document.getElementById('theme-toggle');
  if (toggle) {
    var saved = localStorage.getItem('woosdom-theme');
    if (saved === 'light') {
      document.body.classList.replace('dark', 'light');
    }
    toggle.addEventListener('click', function () {
      var isLight = document.body.classList.contains('light');
      if (isLight) {
        document.body.classList.replace('light', 'dark');
        localStorage.setItem('woosdom-theme', 'dark');
      } else {
        document.body.classList.replace('dark', 'light');
        localStorage.setItem('woosdom-theme', 'light');
      }
    });
  }

  // ── Header Clock ──
  var clock = document.getElementById('header-clock');
  if (clock) {
    function updateClock() {
      var now = new Date();
      var h = String(now.getHours()).padStart(2, '0');
      var m = String(now.getMinutes()).padStart(2, '0');
      var s = String(now.getSeconds()).padStart(2, '0');
      clock.textContent = now.toISOString().slice(0, 10) + ' ' + h + ':' + m + ':' + s;
    }
    updateClock();
    setInterval(updateClock, 1000);
  }
})();

// ── Department Toggle (global for inline onclick) ──
function toggleDept(headerEl) {
  var group = headerEl.parentElement;
  group.classList.toggle('dept-group--collapsed');
}

// ─── core.js — Dashboard shared utilities ────────────────────────────────────

// ── Dashboard panel registry (used by pixel-agents and future panels) ─────────
var Dashboard = {
  data: {},
  panels: {},
  init: function(initialData) {
    this.data = initialData || {};
    this.render();
  },
  update: function(newData) {
    this.data = newData;
    this.render();
  },
  render: function() {
    var ids = Object.keys(this.panels);
    for (var i = 0; i < ids.length; i++) {
      var p = this.panels[ids[i]];
      try { if (p.render) p.render(this.data); }
      catch(e) { console.error('[Dashboard] panel ' + ids[i] + ' render failed:', e); }
    }
  },
  registerPanel: function(id, module) {
    module.id = id;
    this.panels[id] = module;
  }
};

// Collapsible section toggle
function toggleSection(id) {
  const el = document.getElementById(id);
  const arrow = document.getElementById(id + '-arrow');
  if (!el) return;
  const isHidden = el.classList.contains('hidden');
  el.classList.toggle('hidden');
  if (arrow) arrow.textContent = isHidden ? '▲' : '▼';
}

// Briefing toggle
function toggleBriefing() {
  const body = document.getElementById('briefing-body');
  const btn  = document.getElementById('briefing-toggle');
  if (body.style.display === 'none') {
    body.style.display = '';
    btn.textContent = '▲ 접기';
  } else {
    body.style.display = 'none';
    btn.textContent = '▼ 브리핑 보기';
  }
}

// Completed items toggle
function toggleCompl(id) {
  const el  = document.getElementById(id);
  const btn = el.previousElementSibling;
  const isHidden = el.classList.contains('hidden');
  el.classList.toggle('hidden');
  btn.textContent = isHidden
    ? '▲ 접기'
    : `✅ 완료 항목 보기 (${el.querySelectorAll('li').length})`;
}

// More completed toggle
function toggleMore() {
  const container = document.getElementById('hidden-completed');
  const btn = document.getElementById('more-btn');
  const items = container.querySelectorAll('.hidden-item');
  const showing = btn.dataset.showing === 'true';
  items.forEach(el => { el.style.display = showing ? 'none' : ''; });
  btn.dataset.showing = showing ? 'false' : 'true';
  const count = items.length;
  btn.textContent = showing ? `▼ ${count}개 더 보기` : '▲ 접기';
}

// Milestone axis filter
function filterMilestones(axis) {
  document.querySelectorAll('.axis-card').forEach(c => c.classList.remove('active'));
  const items = document.querySelectorAll('.ms-item');
  if (axis === 'all') {
    items.forEach(el => el.classList.remove('filtered-out'));
    return;
  }
  document.querySelectorAll('.axis-card').forEach(c => {
    const nameEl = c.querySelector('.axis-name');
    if (nameEl && nameEl.textContent.trim() === axis) c.classList.add('active');
  });
  items.forEach(el => {
    if (el.dataset.axis === axis) {
      el.classList.remove('filtered-out');
    } else {
      el.classList.add('filtered-out');
    }
  });
}

// Theme toggle
function toggleTheme() {
  const body = document.body;
  const btn = document.getElementById('theme-toggle');
  const isLight = body.classList.toggle('light');
  btn.textContent = isLight ? '☀️' : '🌙';
}

// Domain / Section filter
document.addEventListener('DOMContentLoaded', function() {
  let activeDomain  = 'all';
  let activeSection = 'all';

  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const domain  = this.dataset.domain;
      const section = this.dataset.section;
      if (domain !== undefined) {
        activeDomain = domain;
        document.querySelectorAll('[data-domain].filter-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
      }
      if (section !== undefined) {
        activeSection = section;
        document.querySelectorAll('[data-section].filter-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
      }
      applyFilters();
    });
  });

  function applyFilters() {
    // Filter project cards
    document.querySelectorAll('.project-card').forEach(card => {
      const dm = activeDomain  === 'all' || card.dataset.domain  === activeDomain;
      const sm = activeSection === 'all' || card.dataset.section === activeSection;
      card.style.display = (dm && sm) ? '' : 'none';
    });
    // Filter standalone task cards
    document.querySelectorAll('.task-card').forEach(card => {
      const dm = activeDomain  === 'all' || card.dataset.domain  === activeDomain;
      const sm = activeSection === 'all' || card.dataset.section === activeSection;
      card.style.display = (dm && sm) ? '' : 'none';
    });
  }
});

// ── PyWebView window.state realtime listener (Phase 3) ───────────────────────
// When desktop.py pushes window.state.dashboard_data, Dashboard.update() is called
// so registered panels (pixel-agents etc.) can refresh without a full page reload.
if (window.pywebview !== undefined) {
  window.addEventListener('pywebviewready', function() {
    var state = window.pywebview && window.pywebview.state;
    if (!state) return;
    state.addEventListener('change', function(e) {
      if (e.detail && e.detail.key === 'dashboard_data') {
        var newData = state.dashboard_data;
        if (newData) {
          Dashboard.update(newData);
          console.log('[Dashboard] state update received at', new Date().toLocaleTimeString());
        }
      }
    });
    console.log('[Dashboard] window.state listener registered');
  });
}

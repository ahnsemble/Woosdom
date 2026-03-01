// ─── launcher.js — Quick Launcher API bridge ──────────────────────────────────

async function launchApp(method) {
  if (typeof window.pywebview === 'undefined' || !window.pywebview.api) {
    showToast('⚠️ PyWebView API 없음 (브라우저 미지원)', false);
    return;
  }
  try {
    const result = await window.pywebview.api[method]();
    showToast(result, false);
  } catch(e) {
    showToast('❌ 오류: ' + e, true);
  }
}

async function launchEngineWatch() {
  const btn = document.getElementById('ql-engine-btn');
  if (btn) { btn.textContent = '⏳ 스캔 중...'; btn.disabled = true; }
  if (typeof window.pywebview === 'undefined' || !window.pywebview.api) {
    showToast('⚠️ PyWebView API 없음', false);
    if (btn) { btn.textContent = '🔍 Engine Watch'; btn.disabled = false; }
    return;
  }
  try {
    const result = await window.pywebview.api.run_engine_watch();
    showToast(result, result.startsWith('❌'));
  } catch(e) {
    showToast('❌ Engine Watch 오류: ' + e, true);
  } finally {
    if (btn) { btn.textContent = '🔍 Engine Watch'; btn.disabled = false; }
  }
}

async function launchBackup() {
  const btn = document.getElementById('ql-backup-btn');
  if (btn) { btn.textContent = '⏳ 백업 중...'; btn.disabled = true; }
  if (typeof window.pywebview === 'undefined' || !window.pywebview.api) {
    showToast('⚠️ PyWebView API 없음', false);
    if (btn) { btn.textContent = '💾 Backup'; btn.disabled = false; }
    return;
  }
  try {
    const result = await window.pywebview.api.run_backup();
    showToast(result, false);
  } catch(e) {
    showToast('❌ 백업 실패: ' + e, true);
  } finally {
    if (btn) { btn.textContent = '💾 Backup'; btn.disabled = false; }
  }
}

function showToast(msg, isError) {
  const existing = document.querySelector('.ql-toast');
  if (existing) existing.remove();
  const toast = document.createElement('div');
  toast.className = 'ql-toast' + (isError ? ' error' : '');
  toast.textContent = msg;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 4200);
}

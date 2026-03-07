#!/usr/bin/env python3
"""
watcher.py — Obsidian 볼트 파일 감시 + 증분 인덱싱

사용법:
    python watcher.py
"""

import time
import os
import threading
from pathlib import Path

import chromadb
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import config
from indexer import index_file, delete_file_chunks, _chroma, _col

# ─── 디바운서 ────────────────────────────────────────────────────────────────

class _Debouncer:
    """파일 이벤트 디바운스 처리 (N초 내 중복 이벤트 무시)"""
    def __init__(self, delay: float = config.WATCH_DEBOUNCE):
        self._delay = delay
        self._timers: dict[str, threading.Timer] = {}
        self._lock = threading.Lock()

    def call(self, key: str, fn, *args):
        with self._lock:
            if key in self._timers:
                self._timers[key].cancel()
            t = threading.Timer(self._delay, fn, args)
            self._timers[key] = t
            t.start()


_debouncer = _Debouncer()


# ─── 이벤트 핸들러 ───────────────────────────────────────────────────────────

class VaultEventHandler(FileSystemEventHandler):
    def __init__(self, vault_root: str):
        self._vault_root = vault_root

    def _is_md(self, path: str) -> bool:
        return path.endswith(".md")

    def _in_excluded(self, path: str) -> bool:
        rel = os.path.relpath(path, self._vault_root)
        parts = Path(rel).parts
        for part in parts:
            if part in config.EXCLUDE_DIRS:
                return True
        return False

    def on_modified(self, event):
        if event.is_directory:
            return
        if not self._is_md(event.src_path) or self._in_excluded(event.src_path):
            return
        _debouncer.call(event.src_path, self._reindex_file, event.src_path)

    def on_created(self, event):
        self.on_modified(event)

    def on_deleted(self, event):
        if event.is_directory or not self._is_md(event.src_path) or self._in_excluded(event.src_path):
            return
        rel = os.path.relpath(event.src_path, self._vault_root)
        _debouncer.call(event.src_path, self._delete_file, rel, event.src_path)

    def on_moved(self, event):
        # 이전 경로 삭제 + 새 경로 인덱싱
        if event.is_directory:
            return
        if self._is_md(event.src_path) and not self._in_excluded(event.src_path):
            rel_src = os.path.relpath(event.src_path, self._vault_root)
            _debouncer.call(event.src_path, self._delete_file, rel_src, event.src_path)
        if self._is_md(event.dest_path) and not self._in_excluded(event.dest_path):
            _debouncer.call(event.dest_path, self._reindex_file, event.dest_path)

    def _reindex_file(self, abs_path: str):
        rel = os.path.relpath(abs_path, self._vault_root)
        print(f"[WATCH] 파일 변경 감지: {rel}")

        # 기존 청크 삭제
        n_deleted = delete_file_chunks(rel)
        if n_deleted:
            print(f"[WATCH]   → 기존 청크 삭제: {n_deleted}개")

        # 재인덱싱
        result = index_file(abs_path, self._vault_root)
        if result == 0:
            print(f"[WATCH]   → 청크 없음 (스킵)")
            return

        from indexer import embed_batch, _get_col
        ids, texts, metas = result
        if not ids:
            return

        embs = embed_batch(texts)
        col = _get_col()
        col.upsert(ids=ids, embeddings=embs, documents=texts, metadatas=metas)
        print(f"[WATCH]   → 재인덱싱 완료: {len(ids)}개 청크")

    def _delete_file(self, rel_path: str, abs_path: str):
        print(f"[WATCH] 파일 삭제: {rel_path}")
        n = delete_file_chunks(rel_path)
        print(f"[WATCH]   → ChromaDB 청크 삭제: {n}개")


# ─── 메인 ────────────────────────────────────────────────────────────────────

def watch(vault_root: str = config.VAULT_ROOT):
    print(f"[WATCH] 파일 감시 시작: {vault_root}")
    print(f"[WATCH] 디바운스: {config.WATCH_DEBOUNCE}초")

    handler = VaultEventHandler(vault_root)
    observer = Observer()
    observer.schedule(handler, vault_root, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[WATCH] 종료 중...")
        observer.stop()
    observer.join()
    print("[WATCH] 종료 완료")


if __name__ == "__main__":
    watch()

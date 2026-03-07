#!/usr/bin/env python3
"""
indexer.py — Obsidian 볼트 → ChromaDB 벡터 인덱싱

사용법:
    python indexer.py
"""

import os
import re
import time
import yaml
import tiktoken
from datetime import datetime
from pathlib import Path
from typing import Optional

import chromadb
from google import genai

import config

# ─── 클라이언트 초기화 ───────────────────────────────────────────────────────
_client = genai.Client(api_key=config.GEMINI_API_KEY)
_enc = tiktoken.get_encoding("cl100k_base")

_chroma = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)
_col = _chroma.get_or_create_collection(
    name=config.COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"},
)


def _get_col():
    """현재 ChromaDB 컬렉션 반환 (watcher.py 등 외부에서 참조용)"""
    global _col
    return _col


# ─── 유틸 ────────────────────────────────────────────────────────────────────

def count_tokens(text: str) -> int:
    return len(_enc.encode(text))


def truncate_tokens(text: str, max_tokens: int) -> str:
    toks = _enc.encode(text)
    return _enc.decode(toks[:max_tokens])


def extract_frontmatter(text: str) -> tuple[dict, str]:
    """YAML frontmatter 추출. (frontmatter_dict, body) 반환"""
    fm: dict = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            try:
                fm = yaml.safe_load(text[3:end]) or {}
            except Exception:
                fm = {}
            text = text[end + 4:].lstrip("\n")
    return fm, text


def extract_backlinks(text: str) -> list[str]:
    """[[링크텍스트]] 또는 [[파일명|표시텍스트]] 에서 링크명 추출"""
    raw = re.findall(r"\[\[([^\]]+)\]\]", text)
    links = []
    for r in raw:
        links.append(r.split("|")[0].strip())
    return list(dict.fromkeys(links))  # 순서 유지 중복 제거


def detect_domain(rel_path: str) -> str:
    """볼트 내 상대경로에서 도메인 추출.
    Archive 하위 경로에 도메인 힌트가 있으면 해당 도메인으로 분류."""
    parts = Path(rel_path).parts
    if len(parts) >= 2:
        top = parts[0]
        if top == "01_Domains" and len(parts) >= 3:
            return parts[1]
        if top == "04_Archive" and len(parts) >= 3:
            # 04_Archive/finance_phases/ → Finance, etc.
            sub = parts[1].lower()
            archive_domain_hints = {
                "finance": "Finance", "finance_phases": "Finance",
                "health": "Health", "career": "Career",
                "research": "Research",
            }
            for hint, domain in archive_domain_hints.items():
                if hint in sub:
                    return domain
            return "Archive"
        if top == "02_Projects" and len(parts) >= 3:
            return "Projects"
        domain_map = {
            "00_System": "System",
            "01_Domains": "Domains",
            "02_Projects": "Projects",
            "03_Journal": "Journal",
            "04_Archive": "Archive",
        }
        return domain_map.get(top, top)
    return "Root"


# ─── 청킹 ────────────────────────────────────────────────────────────────────

def chunk_text(
    text: str,
    source_file: str,
    chunk_size: int = config.CHUNK_SIZE,
    overlap: int = config.CHUNK_OVERLAP,
) -> list[dict]:
    """
    텍스트를 청킹.
    H2 헤더 > H3 헤더 > 빈 줄 > 토큰 기준 분할.
    상위 헤더 컨텍스트를 각 청크 앞에 prepend.
    """
    lines = text.split("\n")
    sections: list[tuple[list[str], str]] = []  # (header_stack, section_text)
    header_stack: list[str] = []
    current_lines: list[str] = []

    for line in lines:
        h2 = re.match(r"^## (.+)", line)
        h3 = re.match(r"^### (.+)", line)
        if h2:
            if current_lines:
                sections.append((list(header_stack), "\n".join(current_lines)))
            header_stack = [h2.group(0)]
            current_lines = [line]
        elif h3:
            if current_lines:
                sections.append((list(header_stack), "\n".join(current_lines)))
            # H3는 H2 스택 유지
            h2_headers = [h for h in header_stack if h.startswith("## ")]
            header_stack = h2_headers + [h3.group(0)]
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((list(header_stack), "\n".join(current_lines)))

    chunks = []
    file_stem = Path(source_file).stem

    for h_stack, sec_text in sections:
        # 상위 헤더 컨텍스트 prefix
        context = f"[{file_stem}] " + " > ".join(h.lstrip("#").strip() for h in h_stack) if h_stack else f"[{file_stem}]"
        full_text = f"{context}\n\n{sec_text.strip()}" if sec_text.strip() else ""
        if not full_text.strip():
            continue

        # 토큰 수 기준으로 청크 분할
        tokens = _enc.encode(full_text)
        start = 0
        while start < len(tokens):
            end = min(start + chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text_str = _enc.decode(chunk_tokens)
            chunks.append({
                "text": chunk_text_str,
                "headers": [h.lstrip("#").strip() for h in h_stack],
            })
            if end >= len(tokens):
                break
            start = end - overlap

    return chunks


# ─── 스캔 ────────────────────────────────────────────────────────────────────

def scan_vault(vault_root: str) -> list[str]:
    """볼트 내 .md 파일 절대경로 목록 반환"""
    md_files = []
    for root, dirs, files in os.walk(vault_root):
        # 제외 디렉토리 처리
        dirs[:] = [d for d in dirs if d not in config.EXCLUDE_DIRS]
        for fname in files:
            if fname.endswith(".md"):
                md_files.append(os.path.join(root, fname))
    return md_files


# ─── 임베딩 ─────────────────────────────────────────────────────────────────

def embed_batch(texts: list[str], max_retries: int = 5) -> list[list[float]]:
    """Gemini API로 배치 임베딩 반환 (rate limit 자동 재시도)"""
    for attempt in range(max_retries):
        try:
            result = _client.models.embed_content(
                model=config.EMBEDDING_MODEL,
                contents=texts,
                config={"output_dimensionality": config.EMBEDDING_DIMENSIONS},
            )
            return [e.values for e in result.embeddings]
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                wait = 60 * (attempt + 1)  # 60s, 120s, 180s ...
                print(f"  [RATE] 분당 한도 초과 — {wait}초 대기 후 재시도 ({attempt+1}/{max_retries})")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError(f"embed_batch: {max_retries}회 재시도 후에도 실패")


# ─── 파일 인덱싱 ────────────────────────────────────────────────────────────

def index_file(abs_path: str, vault_root: str) -> int:
    """단일 .md 파일을 인덱싱. 추가된 청크 수 반환."""
    rel_path = os.path.relpath(abs_path, vault_root)

    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception as e:
        print(f"  [WARN] 읽기 실패 {rel_path}: {e}")
        return 0

    fm, body = extract_frontmatter(raw)
    backlinks = extract_backlinks(raw)
    domain = detect_domain(rel_path)
    tags = fm.get("tags", []) or []
    if isinstance(tags, str):
        tags = [tags]
    last_modified = datetime.fromtimestamp(os.path.getmtime(abs_path)).isoformat()

    chunks = chunk_text(body, rel_path)
    total = len(chunks)
    if total == 0:
        return 0

    ids, texts, metadatas = [], [], []
    for i, ch in enumerate(chunks):
        doc_id = f"{rel_path}::chunk_{i}"
        ids.append(doc_id)
        texts.append(ch["text"])
        metadatas.append({
            "source_file": rel_path,
            "domain": domain,
            "headers": " | ".join(ch["headers"]) if ch["headers"] else "",
            "has_backlinks": len(backlinks) > 0,
            "backlinks": ", ".join(backlinks[:20]),  # ChromaDB는 list 미지원 → str
            "frontmatter_tags": ", ".join([str(t) for t in tags[:10]]),
            "last_modified": last_modified,
            "chunk_index": i,
            "total_chunks": total,
        })

    return ids, texts, metadatas


def delete_file_chunks(rel_path: str) -> int:
    """특정 파일의 모든 청크를 ChromaDB에서 삭제. 삭제 수 반환."""
    prefix = f"{rel_path}::chunk_"
    # ChromaDB: where 필터로 source_file 매칭
    try:
        existing = _col.get(where={"source_file": {"$eq": rel_path}})
        if existing["ids"]:
            _col.delete(ids=existing["ids"])
            return len(existing["ids"])
    except Exception:
        pass
    return 0


# ─── 메인 인덱싱 ──────────────────────────────────────────────────────────────

def run_full_index(vault_root: str = config.VAULT_ROOT) -> dict:
    """전체 볼트 인덱싱 실행. 통계 dict 반환."""
    t0 = time.time()
    print(f"[INDEX] 스캔 시작: {vault_root}")

    md_files = scan_vault(vault_root)
    print(f"[INDEX] 파일 발견: {len(md_files)}개 .md")

    all_ids, all_texts, all_metas = [], [], []

    for fp in md_files:
        result = index_file(fp, vault_root)
        if result == 0:
            continue
        ids, texts, metas = result
        all_ids.extend(ids)
        all_texts.extend(texts)
        all_metas.extend(metas)

    total_chunks = len(all_ids)
    print(f"[INDEX] 청킹 완료: 총 {total_chunks}개 청크")

    if total_chunks == 0:
        print("[INDEX] 청크 없음. 종료.")
        return {"files": len(md_files), "chunks": 0, "elapsed": time.time() - t0}

    # 기존 컬렉션 초기화 후 새로 저장
    _chroma.delete_collection(config.COLLECTION_NAME)
    global _col
    _col = _chroma.get_or_create_collection(
        name=config.COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # 임베딩 배치 처리
    batch_size = config.EMBED_BATCH_SIZE
    n_batches = (total_chunks + batch_size - 1) // batch_size
    all_embeddings = []

    for i in range(n_batches):
        batch_texts = all_texts[i * batch_size: (i + 1) * batch_size]
        print(f"[INDEX] 임베딩 진행: {min((i+1)*batch_size, total_chunks)}/{total_chunks} (배치 {i+1}/{n_batches})")
        embs = embed_batch(batch_texts)
        all_embeddings.extend(embs)
        # rate limit 방지: 배치 간 2초 딜레이
        if i < n_batches - 1:
            time.sleep(2)

    # ChromaDB 저장 (배치)
    for i in range(n_batches):
        s = i * batch_size
        e = min((i + 1) * batch_size, total_chunks)
        _col.upsert(
            ids=all_ids[s:e],
            embeddings=all_embeddings[s:e],
            documents=all_texts[s:e],
            metadatas=all_metas[s:e],
        )

    elapsed = time.time() - t0
    print(f"[INDEX] ChromaDB 저장 완료: {total_chunks} documents in '{config.COLLECTION_NAME}'")
    print(f"[INDEX] 소요 시간: {elapsed:.0f}초")

    return {"files": len(md_files), "chunks": total_chunks, "elapsed": elapsed}


if __name__ == "__main__":
    run_full_index()

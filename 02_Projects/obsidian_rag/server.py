#!/usr/bin/env python3
"""
server.py — FastAPI 시맨틱 검색 서버

사용법:
    uvicorn server:app --host 0.0.0.0 --port 8100
    또는: python server.py
"""

import time
import os
from datetime import datetime
from typing import Optional

import chromadb
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from pydantic import BaseModel

import config

# ─── 클라이언트 초기화 ───────────────────────────────────────────────────────
_client = genai.Client(api_key=config.GEMINI_API_KEY)
_chroma = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)


def _get_collection():
    return _chroma.get_or_create_collection(
        name=config.COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


app = FastAPI(
    title="Woosdom Obsidian RAG",
    description="Obsidian 볼트 시맨틱 검색 API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── 스키마 ──────────────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str
    n_results: int = 5
    domain_filter: Optional[str] = None
    include_metadata: bool = True


class SearchResult(BaseModel):
    content: str
    source_file: str
    domain: str
    headers: list[str]
    backlinks: list[str]
    similarity_score: float
    last_modified: str


class SearchResponse(BaseModel):
    results: list[SearchResult]
    total_results: int
    query_time_ms: float


class StatsResponse(BaseModel):
    total_documents: int
    total_files: int
    domains: dict
    last_indexed: Optional[str]
    chroma_db_size_mb: float


# ─── 엔드포인트 ──────────────────────────────────────────────────────────────

@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest):
    t0 = time.time()

    # 쿼리 임베딩
    try:
        emb_resp = _client.models.embed_content(
            model=config.EMBEDDING_MODEL,
            contents=[req.query],
            config={"output_dimensionality": config.EMBEDDING_DIMENSIONS},
        )
        query_emb = emb_resp.embeddings[0].values
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"임베딩 오류: {e}")

    # ChromaDB 검색
    col = _get_collection()
    where_filter = None
    if req.domain_filter:
        where_filter = {"domain": {"$eq": req.domain_filter}}

    try:
        results = col.query(
            query_embeddings=[query_emb],
            n_results=min(req.n_results, col.count() or 1),
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 오류: {e}")

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    search_results = []
    for doc, meta, dist in zip(docs, metas, dists):
        # cosine distance → similarity (1 - dist)
        score = round(1.0 - dist, 4)
        headers_str = meta.get("headers", "")
        headers_list = [h.strip() for h in headers_str.split("|") if h.strip()] if headers_str else []
        backlinks_str = meta.get("backlinks", "")
        backlinks_list = [b.strip() for b in backlinks_str.split(",") if b.strip()] if backlinks_str else []

        search_results.append(SearchResult(
            content=doc,
            source_file=meta.get("source_file", ""),
            domain=meta.get("domain", ""),
            headers=headers_list,
            backlinks=backlinks_list,
            similarity_score=score,
            last_modified=meta.get("last_modified", ""),
        ))

    elapsed_ms = round((time.time() - t0) * 1000, 1)
    return SearchResponse(
        results=search_results,
        total_results=len(search_results),
        query_time_ms=elapsed_ms,
    )


@app.get("/stats", response_model=StatsResponse)
def stats():
    col = _get_collection()
    total_docs = col.count()

    domains: dict = {}
    files_seen: set = set()
    last_modified = None

    if total_docs > 0:
        try:
            all_data = col.get(include=["metadatas"], limit=total_docs)
            for meta in all_data["metadatas"]:
                d = meta.get("domain", "Unknown")
                domains[d] = domains.get(d, 0) + 1
                files_seen.add(meta.get("source_file", ""))
                lm = meta.get("last_modified", "")
                if lm and (not last_modified or lm > last_modified):
                    last_modified = lm
        except Exception:
            pass

    # ChromaDB 디렉토리 크기
    db_size_mb = 0.0
    if os.path.isdir(config.CHROMA_DB_PATH):
        total_bytes = sum(
            os.path.getsize(os.path.join(r, f))
            for r, _, fs in os.walk(config.CHROMA_DB_PATH)
            for f in fs
        )
        db_size_mb = round(total_bytes / (1024 * 1024), 2)

    return StatsResponse(
        total_documents=total_docs,
        total_files=len(files_seen),
        domains=domains,
        last_indexed=last_modified,
        chroma_db_size_mb=db_size_mb,
    )


@app.post("/reindex")
def reindex(background_tasks: BackgroundTasks):
    """전체 재인덱싱 트리거 (백그라운드 실행)"""
    def _do_reindex():
        from indexer import run_full_index
        run_full_index()

    background_tasks.add_task(_do_reindex)
    return {"status": "started", "message": "재인덱싱 백그라운드에서 시작됨"}


@app.get("/health")
def health():
    col = _get_collection()
    return {"status": "ok", "indexed_documents": col.count()}


@app.get("/")
def root():
    return {"service": "Woosdom Obsidian RAG", "status": "ok", "port": config.SERVER_PORT}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host=config.SERVER_HOST, port=config.SERVER_PORT, reload=False)

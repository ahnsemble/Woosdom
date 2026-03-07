#!/usr/bin/env python3
"""
test_search.py — 검색 품질 테스트

사용법:
    python test_search.py
    또는 (서버 통해): 서버 실행 후 python test_search.py --api
"""

import argparse
import time
import requests
import chromadb
from google import genai

import config

TEST_QUERIES = [
    {"query": "SPMO 모니터링 결정",             "expected_domain": "Finance"},
    {"query": "Phase 20 검산 결과",             "expected_domain": "Finance"},
    {"query": "Project Crossy 로드맵",          "expected_domain": None},
    {"query": "Mission Control 대시보드",        "expected_domain": None},
    {"query": "3자 회의 규칙",                   "expected_domain": "Finance"},
    {"query": "영앤리치 Protocol",               "expected_domain": None},
    {"query": "Defensive DCA 폐기 이유",         "expected_domain": "Finance"},
    {"query": "TLT 비중 축소 근거",              "expected_domain": "Finance"},
    {"query": "brain_directive 버전",            "expected_domain": None},
    {"query": "Big 3 Total 운동 목표",           "expected_domain": "Health"},
]


def _search_direct(query: str, n: int = 3) -> list[dict]:
    """ChromaDB 직접 검색 (서버 없이)"""
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    chroma = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)
    col = chroma.get_or_create_collection(config.COLLECTION_NAME)

    if col.count() == 0:
        return []

    emb = client.models.embed_content(
        model=config.EMBEDDING_MODEL,
        contents=[query],
        config={"output_dimensionality": config.EMBEDDING_DIMENSIONS},
    )
    q_vec = emb.embeddings[0].values

    res = col.query(
        query_embeddings=[q_vec],
        n_results=min(n, col.count()),
        include=["documents", "metadatas", "distances"],
    )

    results = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        results.append({
            "content": doc,
            "source_file": meta.get("source_file", ""),
            "domain": meta.get("domain", ""),
            "score": round(1.0 - dist, 4),
        })
    return results


def _search_api(query: str, n: int = 3, api_url: str = f"http://localhost:{config.SERVER_PORT}") -> list[dict]:
    """API 서버를 통한 검색"""
    resp = requests.post(f"{api_url}/search", json={"query": query, "n_results": n}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return [
        {
            "content": r["content"],
            "source_file": r["source_file"],
            "domain": r["domain"],
            "score": r["similarity_score"],
        }
        for r in data["results"]
    ]


def run_tests(use_api: bool = False):
    print("=" * 70)
    print("Obsidian RAG 검색 품질 테스트")
    print("=" * 70)

    passed = 0
    total = len(TEST_QUERIES)

    for i, tc in enumerate(TEST_QUERIES, 1):
        query = tc["query"]
        expected_domain = tc["expected_domain"]

        print(f"\n[{i:02d}/{total}] 쿼리: {query}")
        if expected_domain:
            print(f"       기대 도메인: {expected_domain}")

        t0 = time.time()
        try:
            if use_api:
                results = _search_api(query, n=3)
            else:
                results = _search_direct(query, n=3)
        except Exception as e:
            print(f"       ❌ 검색 오류: {e}")
            continue

        elapsed_ms = round((time.time() - t0) * 1000, 0)

        if not results:
            print(f"       ❌ 결과 없음 ({elapsed_ms}ms)")
            continue

        # 결과 출력
        for j, r in enumerate(results, 1):
            snippet = r["content"].replace("\n", " ").strip()[:100]
            domain_match = "✅" if (expected_domain is None or r["domain"] == expected_domain) else "⚠️"
            print(f"       #{j} [{r['score']:.3f}] {domain_match} [{r['domain']}] {r['source_file']}")
            print(f"          {snippet}...")

        # 성공 판단: top-3 중 하나라도 expected_domain 일치 (none이면 무조건 통과)
        if expected_domain is None:
            ok = True
        else:
            ok = any(r["domain"] == expected_domain for r in results)

        if ok:
            passed += 1
            print(f"       → PASS ({elapsed_ms}ms)")
        else:
            print(f"       → FAIL — 기대 도메인 '{expected_domain}' 미포함 ({elapsed_ms}ms)")

    print("\n" + "=" * 70)
    print(f"결과: {passed}/{total} PASS  ({passed/total*100:.0f}%)")
    if passed >= 8:
        print("🎉 성공 기준 달성 (8/10 이상)")
    else:
        print("⚠️  성공 기준 미달 — 청킹 전략 및 메타데이터 튜닝 권장")
    print("=" * 70)

    return passed, total


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", action="store_true", help="API 서버를 통해 검색 (기본: 직접 ChromaDB)")
    args = parser.parse_args()
    run_tests(use_api=args.api)

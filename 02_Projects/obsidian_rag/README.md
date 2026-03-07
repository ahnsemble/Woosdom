# Obsidian RAG 파이프라인

Obsidian 볼트(`Woosdom_Brain`)를 ChromaDB에 벡터 인덱싱하고 시맨틱 검색 API를 제공합니다.

## 구성 요소

| 파일 | 역할 |
|------|------|
| `config.py` | 경로/모델/포트 설정 |
| `indexer.py` | 볼트 스캔 → 청킹 → 임베딩 → ChromaDB 저장 |
| `server.py` | FastAPI 검색 서버 (포트 8100) |
| `watcher.py` | 파일 변경 감지 → 증분 재인덱싱 |
| `test_search.py` | 검색 품질 테스트 (10개 쿼리) |

## 빠른 시작

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 전체 볼트 인덱싱 (최초 1회, 5~30분 소요)
export OPENAI_API_KEY="sk-..."
python indexer.py

# 3. 검색 품질 테스트
python test_search.py

# 4. API 서버 시작
uvicorn server:app --host 0.0.0.0 --port 8100

# 5. 파일 감시 (별도 터미널)
python watcher.py
```

## API 엔드포인트

### POST /search
```json
{ "query": "SPMO 모니터링 결정", "n_results": 5, "domain_filter": "Finance" }
```

### GET /stats
인덱싱 현황 (총 문서 수, 도메인별 분포, DB 크기)

### POST /reindex
전체 재인덱싱 트리거 (백그라운드 실행)

## 청킹 전략

- H2/H3 헤더 기준 섹션 분할
- 상위 헤더 컨텍스트를 청크 앞에 prepend (`[파일명] > 헤더`)
- 최대 500 tokens, 50 tokens 오버랩
- 메타데이터: domain, headers, backlinks, frontmatter_tags, last_modified

## 성공 기준

- [ ] 전체 볼트 인덱싱 에러 0
- [ ] 10개 테스트 쿼리 중 8개 이상 top-3에 관련 결과 포함
- [ ] /search 응답 100ms 이내
- [ ] watcher.py 증분 인덱싱 동작 확인

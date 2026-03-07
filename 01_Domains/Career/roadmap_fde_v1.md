---
created: "2026-03-07"
source: "Anthropic Labor Market PDF (2026-03-05) + Brain 분석"
tags: [career, fde, roadmap, ai-labor-market]
---

# FDE 커리어 로드맵 v1.0

*근거: Anthropic "Labor market impacts of AI" (Massenkoff & McCrory, 2026-03-05)*

---

## 핵심 인사이트 (PDF 기반)

1. **Architecture & Engineering**: 이론적 AI 커버리지 ~60%, 실제 관측 커버리지 ~20%. 이 갭 = FDE 기회 창.
2. **Software Developers**: observed exposure 높지만 BLS +15% 성장 전망 → augmentation 효과.
3. **22-25세 채용 14% 둔화** (exposed 직종) → 도메인 경험 프리미엄 상승.
4. **"Observed Exposure" 자동화 vs 증강 구분** → FDE = 대체를 만드는 쪽 (대체되는 쪽 아님).

---

## Phase A: 실적 축적 (2026 Q2~Q3, ~6개월)

**목표:** 무영건축 내 AI 자동화 실적 3건

### 타겟 1: 법규 검토 자동화 PoC (P1 — 즉시 착수)
- 입력: 프로젝트 기본정보 (용도, 면적, 층수, 높이, 용도지역)
- 처리: LLM + 건축법 RAG → 적합/부적합 1차 판정
- 출력: 체크리스트 (조항, 기준값, 설계값, 판정, 근거)
- Go/No-Go: 실제 프로젝트 1건 적용, 수동 대비 50%+ 시간 단축, 오탐 0건
- 예상: 2~3주

### 타겟 2: BIM 코디네이션 리포트 자동화 (P2)
- Revit API + LLM으로 간섭 체크 결과 자동 요약 + 우선순위화
- 예상: 3~4주

### 타겟 3: 설계 대안 비교 자동화 (P3)
- 면적표, 법규 적합성, 비용 예측 동시 비교 도구
- 예상: 4~6주

---

## Phase B: 포지셔닝 (2026 Q3~Q4)

**목표:** AEC 소프트웨어 기업 FDE/SA 포지션 3곳+ 타겟

### 타겟 기업 우선순위
1. **Autodesk** (Revit, Forma, ACS) — AEC AI 최적극
2. **Trimble** (Tekla, SketchUp) — 한국 지사
3. **Nemetschek Group** (Graphisoft, Vectorworks, Bluebeam) — 리모트 확대
4. **AEC 스타트업** (Hypar, TestFit, Swapp) — FDE 영향력 극대화

### 면접 킬러 피치
"Architecture & Engineering의 이론적 AI 커버리지는 60%인데 실제 채택은 20%입니다. 저는 이 격차를 좁히기 위해 실제로 법규 자동화, BIM 코디네이션, 설계 비교 도구를 구현한 사람입니다."

---

## Phase C: FDE 입성 + SaaS 시드 발견 (2027 H1)

- 고객사 페인 포인트 1차 소스 수집
- 반복 문제 = SaaS MVP 후보
- Woosdom 인프라 활용 프로토타입

---

## Phase D: AEC SaaS MVP (2027 H2~2028)

- FIRE 사업소득 목표: 월 +200만원
- 타겟: Phase C에서 발견한 반복 페인 포인트 자동화 SaaS

---

## 리스크 매트릭스

| 리스크 | 확률 | 영향 | 대응 |
|--------|------|------|------|
| 건축 AI 채택 영구 정체 | L | H | Autodesk 등 투자 방향이 반증. 최악 시 AI 컨설팅 전환 |
| FDE 포지션 확보 실패 | M | H | Phase A 실적 + Woosdom으로 프리랜스 컨설팅부터 |
| 기회 창 예상보다 빠르게 닫힘 | M | M | Phase A 가속 (법규 PoC 2주 내 완료) |
| Hexagonal 불균형 (기술 올인) | M | M | 주말 1일 운동/가정 보장. 수요일 Active Recovery 유지 |

---

## Hexagonal 정합성 점검

| 축 | 영향 | 판정 |
|----|------|------|
| 체력 | 변화 없음 | ✅ |
| 가정 | 변화 없음 | ✅ |
| 기술 | 핵심 성장 축 | ✅ |
| 재산 | FIRE 사업소득 경로 확보 | ✅ |

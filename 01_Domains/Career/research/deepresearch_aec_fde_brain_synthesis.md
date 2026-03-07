# AEC FDE/SA 전환 역량 — Brain 종합 판정 리포트
*Date: 2026-02-22*
*Sources: Gemini 3.1 Pro 딥리서치 + GPT-5.2 딥리서치 → Brain 교차검증*
*Domain: Career (영앤리치 Protocol)*

---

## 결론

**도달 가능. 타이밍 양호.** CS 학위 부재는 블로커가 아님. 단, 코어 엔진 개발이 아닌 **시스템 통합/오케스트레이션** 영역에 집중해야 하며, "건축을 아는 엔지니어"라는 교차점이 최대 무기.

---

## 1. 양 엔진 합의점 (High Confidence)

- **최대 무기:** AEC 도메인 지식 (5년 실무) — 갭 0, 최대 경쟁 우위
- **최대 갭:** 클라우드 인프라 (AWS/Docker/CI-CD) + 프로덕션 배포 경험
- **포트폴리오 원칙:** 기술 나열 ✕ → 비즈니스 ROI 중심 서술 ○ ("법규 검토 공수 주당 15시간 단축")
- **한국 시장:** AEC 버티컬 FDE는 부재. 글로벌 기업 한국지사(Autodesk Korea) 또는 유사 직무(솔루션 엔지니어, 프리세일즈)로 우회 진입
- **FDE 시장 폭증:** 2024→2025 채용 공고 1,165% 증가, AI 에이전트 프로덕션 배포 수요 급등

## 2. 엔진 간 차이점 + Brain 판정

| 쟁점 | Gemini | GPT | Brain 판정 |
|------|--------|-----|-----------|
| C# 중요도 | 강력 권장 (Revit API 필수 관문) | 강력 권장 (BIM 확장/레거시) | **강력 권장이나 Phase 2로 후순위.** pyRevit + IfcOpenShell로 첫 포트폴리오 가능 |
| 우선순위 1번 | 클라우드 배포 + API 연동 | API/통합 + 고객 대면 패키지 | **GPT 채택.** 기술과 고객 대면 동시 필요 |
| 한국 FDE 존재 | "거의 없다" | "채널톡 등에서 사용 중" | **GPT 채택.** 다만 AEC 버티컬은 양쪽 다 확인 불가 |
| TypeScript/React | 강력 권장 | 후순위 (4번) | **GPT 채택.** 18개월 내 Python+클라우드+API 집중. 프론트는 Streamlit으로 충분 |
| 18개월 Phase | Phase 1: 클라우드 / Phase 2: C# / Phase 3: AI | 6m: 데모세트 / 12m: 배포운영 / 18m: 엔터프라이즈 | **GPT 프레임 채택.** 산출물 기준이라 검증 가능 |

## 3. Brain 보정 (환각/과장 체크)

**Gemini 보정:**
- "클라우드 시장 1조 달러 돌파" — 출처 불명. 과장 가능성. 논지에 영향 없음
- ServiceNow FDSA "15년 경력" — 우성님 타겟과 거리 먼 시니어급. 참고만
- "DistilBERT를 라우터로" — 2026 기준 구식. 무시

**GPT 보정:**
- 채용 공고 URL/수치 구체적 — 신뢰도 높음
- 한국딥러닝 FDE 연봉 4,000~7,001만원 — AEC 특화 아님. 직접 비교 주의
- Higharc 건축가→SWE 전환 사례 — 서사적 참고용

---

## 4. 확정 우선순위 (임팩트 × 학습가능성)

| 순위 | 역량 클러스터 | 이유 |
|------|-------------|------|
| **1** | API 설계/통합 (REST, OAuth, webhooks) + FastAPI | Autodesk/Procore/Clearstory 공통 필수. 가장 빠른 "서비스 가능 엔지니어" 증명 |
| **2** | 클라우드 배포 (AWS/Docker/CI-CD) | 로컬→프로덕션 갭 핵심 레버리지. 1번과 동시 진행 |
| **3** | 고객 대면 산출물 (데모 영상, 워크숍 진행안, 기술 문서, ADR) | SA/SE 면접 당락 결정 요소 |
| **4** | LLM/에이전트 고도화 (RAG eval, guardrails, 모니터링) | 기존 Woosdom 경험 위에 엔터프라이즈급 신뢰성 |
| **5** | SQL + 데이터 파이프라인 (ETL, 품질) | Bentley SA급 요구사항. 기초 SQL은 빠르게 습득 가능 |
| **6** | C# / Revit API 플러그인 | Phase 2부터. pyRevit으로 시작 → 점진적 전환 |

---

## 5. 확정 포트폴리오 프로젝트 (3개)

### 프로젝트 1: AEC 법규/시방서 RAG + Multi-Agent 검토 시스템
(Gemini P1 + GPT A 통합)
- BIM 메타데이터 추출 → Vector DB → Router Agent + Code Agent + Model Agent
- eval 세트 50문항 + hallucination 방어
- **산출물:** 데모 영상 + 워크숍 진행안 + 아키텍처 다이어그램 + API 문서
- **클라우드 배포 필수** (AWS Lambda 또는 EC2)

### 프로젝트 2: AEC 플랫폼 통합 — RFI/Change Order 이벤트 자동화 파이프라인
(Gemini P2 + GPT B 통합)
- ACC/Procore API → Webhook → AWS Lambda → LLM 요약 + 위험도 분류 → Slack/Teams
- OAuth + ETL + 운영 로그/재처리
- **산출물:** 설치/운영 문서 + 고객 온보딩 가이드 + 장애 대응 문서

### 프로젝트 3: IFC 헤드리스 데이터 추출 + ISO 19650 품질 점검 대시보드
(Gemini P3 + GPT C 통합)
- IfcOpenShell → PostgreSQL → 품질 점검(네이밍, 메타데이터 필수항목) → 웹 대시보드(Streamlit)
- Docker 컨테이너화
- **산출물:** 전/후 비교 리포트 + 표준화 이행 성과 메트릭

---

## 6. 확정 마일스톤

| 시점 | 목표 | 핵심 산출물 |
|------|------|-----------|
| **~6개월** | "데모 세트 완성" — 프로젝트 1 완료 + 클라우드 배포 + 고객 대면 문서 세트 | 라이브 API 엔드포인트, 데모 영상(5~8분), 아키텍처 다이어그램, 워크숍 진행안 |
| **~12개월** | "운영 증명" — 프로젝트 2 완료 + Docker/CI-CD + 모니터링 | 배포 스크립트, eval 대시보드, 장애 시나리오 문서, 프로젝트 1 운영 이력 |
| **~18개월** | "엔터프라이즈 확장" — 프로젝트 3 완료 + C#/Revit API 기초 + 지원 시작 | ISO 19650 점검기, 영문 포트폴리오 사이트, 글로벌 5곳+ 지원 |

---

## 7. Pre-Mortem (양 엔진 종합)

| 순위 | 실패 원인 | 방어책 |
|------|----------|--------|
| **1** | 프로토타입만 있고 운영/보안/표준화 부재 → 엔터프라이즈 신뢰 획득 실패 | 모든 프로젝트에 Docker + CI/CD + 로깅 + Auth 기본 포함 |
| **2** | AEC 도메인 강점이 "제품 가치"로 번역 안 됨 (고객 대면 산출물 부족) | 데모 영상 + 워크숍 진행안 + ADR을 프로젝트 1부터 필수 산출물로 |
| **3** | FDE vs SA vs SWE 목표 흔들려 학습/포트폴리오 분산 | **한 문장 고정:** "AEC 고객의 데이터 통합 문제를 AI+클라우드로 해결하고 배포까지 마감하는 FDE" |

---

## 8. 즉시 실행 액션

1. **GitHub 리포 정리** — 현재 흩어진 Python 스크립트/Woosdom 코드를 단일 리포로 통합 + 영문 README
2. **FastAPI "Hello World" 클라우드 배포** — 건축 관련 간단한 계산 API를 AWS/Render에 띄워서 전체 사이클 1회 경험
3. **직무 정의 한 문장 확정** — "AEC 고객의 데이터 통합 문제를 AI+클라우드로 해결하고 배포까지 마감하는 FDE"

---

## 참조 파일
- Gemini 원본: `/01_Domains/Career/research/deepresearch_aec_fde_gemini.md`
- GPT 원본: `/01_Domains/Career/research/deepresearch_aec_fde_gpt.md`
- Career MOC: `/01_Domains/Career/MOC.md`

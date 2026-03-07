# Woosdom Agent Index -- AG 참조용
*기준: .claude/agents/ (CC 네이티브 정본)*
*updated: 2026-03-06*

---

## 빠른 선발 가이드

| 주제 키워드 | 투입 에이전트 | 엔진 |
|-------------|--------------|------|
| 코드/빌드/구현/개발/버그/배포 | eng-foreman | claude_code |
| 구현해/코드 작성/기능 추가/리팩토링 | eng-engineer | claude_code |
| 리뷰/코드 리뷰/PR | eng-critic | claude_code |
| 버그/에러/안 돼/실패/크래시/디버깅 | eng-debugger | claude_code |
| 커밋/푸시/브랜치/머지/태그 | eng-gitops | claude_code |
| 폴더 생성/파일 이동/볼트 구조/링크 깨짐 | eng-vault-keeper | claude_code |
| 계산/시뮬레이션/백테스트/Monte Carlo/FV/MDD | cmp-compute-lead | codex |
| 드리프트/리밸런싱/포트폴리오 점검/자산배분 | fin-portfolio-analyst | brain_direct |
| 계산/FV/드리프트 계산/시뮬레이션 실행/샤프 비율 | fin-quant | codex |
| 시세/매크로/금리/시장 상황/VIX/CPI/FOMC | fin-market-scout | antigravity |
| 백테스트/Monte Carlo/Bootstrap/스트레스 테스트 | fin-backtester | codex |
| FIRE/은퇴/경제적 자유/인출 전략 | fin-fire-planner | codex |
| 세금/TLH/양도세/종합과세/절세/ISA/IRP/증여 | fin-tax-optimizer | brain_direct |
| 조사/리서치/알아봐/비교/트렌드/분석해 | res-scout-lead | antigravity |
| 검색/찾아봐/웹에서/최신 정보 | res-web-scout | antigravity |
| 기술 비교/아키텍처/스택 추천/프레임워크 | res-architect | antigravity |
| 심층 조사/논문/학술/근거/deep research | res-deep-researcher | antigravity |
| 실험/PoC/되는지 확인/벤치마크/테스트해봐 | res-experimenter | claude_code |
| 콘텐츠/발행/캘린더/브랜딩/LinkedIn/GitHub 홍보 | cre-content-strategist | brain_direct |
| 문서/README/블로그/글/작성/이력서/소개문 | cre-writer | brain_direct |
| 디자인/UI/레이아웃/색상/컴포넌트/픽셀아트 | cre-designer | brain_direct |
| 프롬프트/시스템 프롬프트/GPT 만들기/GPT Store | cre-prompt-engineer | brain_direct |
| 커리어/이직/FDE/로드맵/영앤리치/면접 | car-strategist | brain_direct |
| 스킬/역량/자격증/배우고/레벨 | car-skill-tracker | claude_code |
| 네트워킹/LinkedIn/밋업/커뮤니티/인맥/DM | car-network-builder | brain_direct |
| 균형/4축/라이프/번아웃/밸런스/육각형 | life-integrator | brain_direct |
| 운동/체력/스쿼트/벤치/데드/복싱/Big 3/디로드 | life-health-coach | brain_direct |
| 가정/관계/가족/파트너/워라밸 | life-relationship-advisor | brain_direct |
| 복합 작업/동시에/팀 간 협업/전체 계획 | cmd-orchestrator | brain_direct |
| 위임/실행해/CC한테/Codex한테/AG한테/보내 | cmd-dispatcher | claude_code |
| 메모리 업데이트/active_context/세션 마무리/기록해 | cmd-memory-keeper | claude_code |
| 감사/주간 리포트/비용 확인/규칙 위반/이상 감지 | cmd-auditor | brain_direct |

---

## 부서별 에이전트 상세

### Command Division (cmd) -- 4 agents

| id | tier | engine/model | role | delegates_to |
|----|------|-------------|------|-------------|
| cmd-orchestrator | T2 | brain_direct / opus-4.6 | 복합 작업 분해, 다부서 협업 오케스트레이션 | cmd-dispatcher, eng-foreman, cmp-compute-lead, res-scout-lead |
| cmd-dispatcher | T1 | claude_code / haiku-4.5 | 작업-엔진 매칭, to_[engine].md 라우팅 | -- (파일 작성만) |
| cmd-memory-keeper | T1 | claude_code / haiku-4.5 | Hot/Warm/Cold 메모리 관리, active_context 유지 | -- |
| cmd-auditor | T3 | brain_direct / opus-4.6 | 주간 감사, 비용 추적, 규칙 위반 감지 | -- |

**Hard Rules 요약:**
- cmd-orchestrator: 직접 코드 작성 금지, 단일 엔진 작업에 투입 금지
- cmd-dispatcher: 확신도 70% 미만 자의적 선택 금지, 혼합 작업 단일 엔진 금지
- cmd-memory-keeper: active_context 500tok 초과 금지, Rolling 5 엄수
- cmd-auditor: 감사 대상 파일 수정 금지, 주관적 판단 최소화

### Engineering Division (eng) -- 6 agents

| id | tier | engine/model | role | delegates_to |
|----|------|-------------|------|-------------|
| eng-foreman | T1 | claude_code / sonnet-4.5 | CC팀 팀장, 서브에이전트 체이닝 | eng-engineer, eng-critic, eng-gitops, eng-debugger, eng-vault-keeper |
| eng-engineer | T1 | claude_code / sonnet-4.5 | 코드 작성/수정 실행자 | -- |
| eng-critic | T1 | claude_code / sonnet-4.5 | 코드 리뷰, PASS/FAIL 판정 | -- |
| eng-gitops | T1 | claude_code / haiku-4.5 | 커밋, 브랜치, 머지 관리 | -- |
| eng-debugger | T2 | claude_code / sonnet-4.5 | 4-Phase 체계적 디버깅 | eng-engineer (수정 위임) |
| eng-vault-keeper | T1 | claude_code / haiku-4.5 | 볼트 구조/링크 무결성/파일 컨벤션 관리 | -- |

**Hard Rules 요약:**
- eng-foreman: 금융 파일 수정 감지 즉시 STOP, main 직접 push 금지
- eng-engineer: 금융 파일 수정 감지 즉시 STOP, 테스트 없는 코드 제출 금지
- eng-critic: 코드 직접 수정 금지, 테스트 없는 코드 approve 금지
- eng-gitops: Critic approve 없이 커밋 금지, main 직접 커밋 금지
- eng-debugger: 코드 직접 수정 금지, 증상만 가리는 핫픽스 금지
- eng-vault-keeper: 파일 내용 수정 금지, 고아 파일 자의적 삭제 금지

### Compute Division (cmp) -- 4 agents

| id | tier | engine/model | role | delegates_to |
|----|------|-------------|------|-------------|
| cmp-compute-lead | T1 | codex / gpt-5.3-extra-high | 연산 총괄, 파이프라인 설계 | cmp-sandbox-runner, cmp-data-wrangler, cmp-parallel-coordinator |
| cmp-data-wrangler | T2 | codex / gpt-5.3-medium | 데이터 전처리/변환/정제 | -- |
| cmp-parallel-coordinator | T2 | codex / gpt-5.3-medium | 병렬 연산 분배/수집/합산 | cmp-sandbox-runner |
| cmp-sandbox-runner | T2 | codex / gpt-5.3-medium | 격리 환경 코드 실행 | -- |

**Hard Rules 요약:**
- cmp-compute-lead: Rules.md/portfolio.json 수정 금지, 파라미터 누락 시 가정 금지
- cmp-data-wrangler: 원본 데이터 덮어쓰기 금지, 전처리 이력 미기록 금지
- cmp-parallel-coordinator: 의존성 불확실 시 병렬 금지, 동시 에이전트 최대 3개
- cmp-sandbox-runner: 수신 코드 수정 금지, 파괴적 명령 실행 금지

### Finance Division (fin) -- 6 agents

| id | tier | engine/model | role | delegates_to |
|----|------|-------------|------|-------------|
| fin-portfolio-analyst | T1 | brain_direct / opus-4.6 | 드리프트 분석, 리밸런싱, ETF 교체 판단 | fin-quant, fin-market-scout, fin-backtester, fin-tax-optimizer |
| fin-quant | T2 | codex / gpt-5.3 | FV 계산, 드리프트 계산, 시뮬레이션 실행 | -- |
| fin-market-scout | T2 | antigravity / gemini-3.1-pro | 시세/매크로/금리/VIX/CPI/FOMC 데이터 수집 | res-web-scout, res-deep-researcher |
| fin-backtester | T3 | codex / gpt-5.3 | Monte Carlo, Bootstrap, 스트레스 테스트 | fin-quant |
| fin-fire-planner | T3 | codex / gpt-5.3 | FIRE 역산, 인출 전략, 은퇴 시뮬레이션 | fin-backtester, fin-quant, fin-market-scout |
| fin-tax-optimizer | T3 | brain_direct / opus-4.6 | TLH, 양도세, 절세, ISA/IRP 전략 | fin-quant, fin-market-scout |

**Hard Rules 요약:**
- fin-portfolio-analyst: LLM 수학 연산 금지, 매매 판단 직접 금지
- fin-quant: LLM 자체 수학 연산 금지, 수식 로직 자율 변경 금지
- fin-market-scout: 데이터에 판단/해석 금지, 출처 없는 데이터 전달 금지
- fin-backtester: MDD -40% 방어 로직 변경 금지, LLM 자체 시뮬레이션 금지
- fin-fire-planner: LLM 자체 시뮬레이션 금지, MDD 방어 로직 변경 금지
- fin-tax-optimizer: 탈세 조언 금지, 단정적 세무 자문 금지

### Research Division (res) -- 5 agents

| id | tier | engine/model | role | delegates_to |
|----|------|-------------|------|-------------|
| res-scout-lead | T1 | antigravity / gemini-3.1-pro | 리서치 설계, MECE 분해, 팀 오케스트레이션 | res-web-scout, res-architect, res-experimenter, res-deep-researcher |
| res-web-scout | T2 | antigravity / gemini-3.1-pro | 웹 OSINT, 검색 최적화, 실시간 정보 수집 | -- |
| res-architect | T2 | antigravity / gemini-3.1-pro | 기술 스택 평가, Trade-off 분석 | res-web-scout, res-experimenter |
| res-deep-researcher | T3 | antigravity / gemini-3.1-pro | 학술 논문, 심층 조사, Gemini Deep Research | res-web-scout |
| res-experimenter | T2 | claude_code / sonnet-4.5 | PoC, 벤치마크, 가설 검증 | -- |

**Hard Rules 요약:**
- res-scout-lead: 코드 작성 금지, 상충 정보 임의 한쪽 선택 금지
- res-web-scout: 출처 없는 정보 전달 금지, 2차 인용을 원본으로 위장 금지
- res-architect: 평가 기준 없이 비교 금지, 코드 수정 금지
- res-deep-researcher: AI 생성 요약 원본 확인 없이 전달 금지, 환각 논문 전달 금지
- res-experimenter: 프로덕션 코드 수정 금지, 가설 없이 실험 시작 금지

### Creative Division (cre) -- 4 agents

| id | tier | engine/model | role | delegates_to |
|----|------|-------------|------|-------------|
| cre-content-strategist | T2 | brain_direct / opus-4.6 | 콘텐츠 기획, 발행 캘린더, 브랜딩 | cre-writer, cre-designer, cre-prompt-engineer |
| cre-writer | T2 | brain_direct / opus-4.6 | 문서/블로그/이력서 작성 | -- |
| cre-designer | T2 | brain_direct / opus-4.6 | UI/레이아웃/픽셀아트 디자인 | -- |
| cre-prompt-engineer | T2 | brain_direct / opus-4.6 | 시스템 프롬프트/GPT Store 프롬프트 설계 | res-experimenter |

**Hard Rules 요약:**
- cre-content-strategist: 금융 파일 접근 금지, 목적 없는 콘텐츠 기획 금지
- cre-writer: 금융 파일 접근 금지, 대상 독자 미확인 시 작성 보류
- cre-designer: 금융 파일 접근 금지, 코드 직접 구현 금지
- cre-prompt-engineer: brain_directive 직접 수정 금지, 프롬프트 인젝션 방어 미포함 시 전달 금지

### Career Division (car) -- 3 agents

| id | tier | engine/model | role | delegates_to |
|----|------|-------------|------|-------------|
| car-strategist | T1 | brain_direct / opus-4.6 | 커리어 전략, FDE 로드맵, Hexagonal 진단 | car-skill-tracker, car-network-builder, cre-writer, cre-content-strategist |
| car-skill-tracker | T3 | claude_code / haiku-4.5 | 스킬 레벨 추적, 자격증 관리 | -- |
| car-network-builder | T3 | brain_direct / sonnet-4.5 | LinkedIn/밋업/커뮤니티 네트워킹 | cre-writer, res-web-scout |

**Hard Rules 요약:**
- car-strategist: 금융 파일 접근 금지, 이직 권고 시 반드시 FIRE+Hexagonal+Pre-Mortem 포함
- car-skill-tracker: 증거 없이 레벨 상향 금지
- car-network-builder: 사용자 동의 없는 외부 접촉 금지

### Life Division (life) -- 3 agents

| id | tier | engine/model | role | delegates_to |
|----|------|-------------|------|-------------|
| life-integrator | T1 | brain_direct / opus-4.6 | 4축 균형 진단, 밸런스 점수 산출 | -- |
| life-health-coach | T2 | brain_direct / opus-4.6 | Big 3 + 복싱 트레이닝, 커팅/벌크 관리 | -- |
| life-relationship-advisor | T2 | brain_direct / opus-4.6 | 가정/파트너/워라밸 상담 | -- |

**Hard Rules 요약:**
- life-integrator: 금융 파일 수정 금지, 점수는 추정치임을 항상 명시
- life-health-coach: training_protocol 직접 수정 금지, 의학적 진단 금지
- life-relationship-advisor: 민감 정보 로그 기록 금지, 관계 진단/판정 금지

### Operations Division (ops) -- 4 agents

| id | tier | engine/model | role | delegates_to |
|----|------|-------------|------|-------------|
| ops-infra-manager | T2 | claude_code / sonnet-4.5 | 인프라 관리, 디스크/네트워크/서비스 모니터링 | -- |
| ops-scheduler | T3 | claude_code / haiku-4.5 | cron/LaunchAgent 스케줄 관리 | -- |
| ops-health-monitor | T3 | claude_code / haiku-4.5 | 시스템 헬스체크, 이상 감지 | -- |
| ops-backup-guard | T3 | claude_code / haiku-4.5 | git/볼트 백업 무결성 확인 | -- |

**Hard Rules 요약:**
- ops-infra-manager: 디스크 자율 삭제 금지, 파괴적 명령 금지
- ops-scheduler: 시간대 미지정 시 KST 기본, 동시 트리거 3개 초과 시 순차 실행
- ops-health-monitor: 직접 수리/복구 금지
- ops-backup-guard: 원본 파일 수정 금지, 백업 자율 삭제 금지

---

## 엔진별 분류

### brain_direct -- 13 agents
Brain(claude.ai Opus 4.6)이 직접 실행. 전략 판단, 상담, 콘텐츠.

| id | department |
|----|-----------|
| cmd-auditor | Command |
| cmd-orchestrator | Command |
| fin-portfolio-analyst | Finance |
| fin-tax-optimizer | Finance |
| cre-content-strategist | Creative |
| cre-writer | Creative |
| cre-designer | Creative |
| cre-prompt-engineer | Creative |
| car-strategist | Career |
| car-network-builder | Career |
| life-integrator | Life |
| life-health-coach | Life |
| life-relationship-advisor | Life |

### claude_code (CC 위임) -- 14 agents
Claude Code에서 실행. 코드, 볼트, 운영.

| id | department |
|----|-----------|
| cmd-dispatcher | Command |
| cmd-memory-keeper | Command |
| eng-foreman | Engineering |
| eng-engineer | Engineering |
| eng-critic | Engineering |
| eng-gitops | Engineering |
| eng-debugger | Engineering |
| eng-vault-keeper | Engineering |
| car-skill-tracker | Career |
| res-experimenter | Research |
| ops-infra-manager | Operations |
| ops-scheduler | Operations |
| ops-health-monitor | Operations |
| ops-backup-guard | Operations |

### codex (Codex 위임) -- 7 agents
GPT-5.3-Codex에서 실행. 대규모 연산, 시뮬레이션.

| id | department |
|----|-----------|
| cmp-compute-lead | Compute |
| cmp-data-wrangler | Compute |
| cmp-parallel-coordinator | Compute |
| cmp-sandbox-runner | Compute |
| fin-backtester | Finance |
| fin-fire-planner | Finance |
| fin-quant | Finance |

### antigravity (Gemini 실행) -- 5 agents
Gemini 3.1 Pro에서 실행. 리서치, 검색, 시장 데이터.

| id | department |
|----|-----------|
| res-scout-lead | Research |
| res-web-scout | Research |
| res-architect | Research |
| res-deep-researcher | Research |
| fin-market-scout | Finance |

---

## 에이전트 간 협력 패턴

### 패턴 1: Brain -> Orchestrator -> 다부서 체이닝
```
Brain (전략 판단)
  -> cmd-orchestrator (작업 분해)
    -> cmd-dispatcher (엔진 라우팅)
    -> eng-foreman (코드 작업)
    -> cmp-compute-lead (연산 작업)
    -> res-scout-lead (리서치)
```

### 패턴 2: Engineering 파이프라인
```
eng-foreman
  -> eng-engineer (구현)
  -> eng-critic (리뷰: PASS/FAIL)
  -> eng-gitops (커밋)
  -> eng-vault-keeper (볼트 업데이트)
  ** FAIL시: eng-engineer 재작업 (최대 2회) -> Brain 에스컬레이션
```

### 패턴 3: Finance 분석 파이프라인
```
fin-portfolio-analyst (분석 설계)
  -> fin-quant (수치 계산)
  -> fin-market-scout (시장 데이터) -> res-web-scout/res-deep-researcher
  -> fin-backtester (시뮬레이션) -> fin-quant
  -> fin-tax-optimizer (세금 최적화) -> fin-quant
```

### 패턴 4: Research 파이프라인
```
res-scout-lead (리서치 설계)
  -> res-web-scout (웹 검색)
  -> res-architect (기술 평가) -> res-web-scout, res-experimenter
  -> res-deep-researcher (심층 조사) -> res-web-scout
  -> res-experimenter (PoC/벤치마크)
```

### 패턴 5: Career + Creative 크로스부서
```
car-strategist (커리어 전략)
  -> car-skill-tracker (스킬 추적)
  -> car-network-builder (네트워킹) -> cre-writer, res-web-scout
  -> cre-writer (이력서/소개문)
  -> cre-content-strategist (브랜딩) -> cre-writer, cre-designer, cre-prompt-engineer
```

### 패턴 6: FIRE 시뮬레이션 풀스택
```
Brain (FIRE 질문)
  -> fin-fire-planner (시나리오 설계)
    -> fin-quant (FV/인출 계산)
    -> fin-backtester (Monte Carlo) -> fin-quant
    -> fin-market-scout (매크로 데이터) -> res-web-scout
  -> fin-portfolio-analyst (결과 해석)
  -> Brain (최종 판단)
```

---

## 통계

| 항목 | 수치 |
|------|------|
| 총 에이전트 | 39 |
| 부서 수 | 9 |
| brain_direct | 13 (33%) |
| claude_code | 14 (36%) |
| codex | 7 (18%) |
| antigravity | 5 (13%) |
| T1 | 14 |
| T2 | 16 |
| T3 | 9 |

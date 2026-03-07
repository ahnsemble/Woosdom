# WorldMonitor → Woosdom 적용 로드맵
*Created: 2026-03-03 — Brain 판정*
*Source: github.com/koala73/worldmonitor*

## 채택 패턴

### 🟢 P1. Intelligence Gap Reporting (즉시)
- **원본**: 14개 데이터 소스 신선도 추적, 데이터 부재 명시 보고
- **적용**: agent_activity.md에 last_seen 타임스탬프 + Monitor v2 Agent Grid에 stale 경고
- **시점**: Monitor v2 구현 시 함께

### 🟢 P2. AI Fallback Chain (완료)
- **원본**: Ollama → Groq → OpenRouter → browser T5
- **적용**: Sub-Brain 인수 프로토콜 L0→L1→L2→L3 승계 체인
- **시점**: ✅ 설계 완료, brain_callback.py 장애감지 코드 완료

### 🟢 P3. Circuit Breaker + Graceful Degradation (근시일)
- **원본**: 피드별 서킷 브레이커 5분 쿨다운, stale 캐시 반환
- **적용**: brain_callback에 연속 실패 카운터(이미 구현) + 이전 성공 응답 캐시 반환 추가
- **시점**: Sub-Brain E2E 테스트 시 함께 검증

## 보류 패턴

### 🟡 P4. 하이브리드 분류 파이프라인 (자동화 고도화 시)
- **원본**: 키워드 즉시 분류 → LLM 비동기 오버라이드
- **적용**: 에이전트 라우팅 — 1차 키워드 매칭 → Brain LLM 보정
- **전제 조건**: 자동 위임이 일상화되어 라우팅 레이턴시가 병목이 될 때
- **예상 시점**: 2026 Q2 이후

### 🔴 P5. Welford 이상 탐지 (데이터 축적 후)
- **원본**: 90일 롤링 윈도우 z-score 이탈 감지
- **적용**: 포트폴리오 변동성 급등, 운동 패턴 이탈 자동 감지
- **전제 조건**: DCA 6개월 이상 데이터 축적 (현재 첫 매수 $2,200)
- **예상 시점**: 2026 Q3~Q4

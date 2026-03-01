# Woosdom 진화 로드맵 — 통합 v3
*Created: 2026-03-01 | Updated: 2026-03-01 (D-4~D-5+B-5 완료 반영)*
*Owner: Brain*

---

## Track A: Codex 생태계 이식 (Phase 0~5) — ✅ 전체 완료

| Phase | 내용 | 상태 |
|-------|------|------|
| 0 | 리서치 — Codex 스킬/MCP 생태계 조사 → 우즈덤 갭 분석 | ✅ 완료 |
| 1 | 디스패치 채널 분리 — to/from_hands → 엔진별 전용 파일 6개 | ✅ 완료 |
| 2 | Codex 스킬 설치 — curated 8개 + experimental 2개 | ✅ 완료 |
| 3 | MCP 코드 패치 — delegate_to_engine/read_hands_result 엔진별 분기 + Task Bridge v4.0 | ✅ 완료 |
| 4 | 스킬 표준화 — openai.yaml + AGENTS.md + meta-skill-writer 이식 | ✅ 완료 |
| 5 | 검증 & 마무리 — 3루트 E2E + read_hands_result + active_context 정리 | ✅ 완료 |

---

## 자동 트리거: CC — ✅ 완료

| Step | 내용 | 상태 |
|------|------|------|
| 0-1 | CLI 비용/블록 리스크 검증 — Max 5x 구독 토큰 소모 확인 | ✅ 완료 |
| 0-2 | task_bridge v4.1 + hands3_runner Popen 스트리밍 구현 (CC만) | ✅ 완료 |
| 0-3 | 가드레일 — debounce, --max-turns 15, 일일 20건 한도, API키 제거 | ✅ 완료 |
| 0-4 | E2E 검증 — Brain → CC 자동실행 → TG 알림 → from_claude_code.md | ✅ PASS (7초) |

---

## Track B: Woosdom App 최종 진화 — ✅ 전체 완료

| Phase | 내용 | 상태 |
|-------|------|------|
| B-1 | 코드 전체 진단 — DIAGNOSIS.md, 4009 LOC, 부채 12건 | ✅ 완료 |
| B-2 | 리팩토링 7건 (R1~R7) — 빌드+런타임 검증 PASS | ✅ 완료 |
| B-3 | 잔여 부채 6건 (T1~T6) — 빌드+런타임 PASS | ✅ 완료 |
| B-4 | 기존 버그 수정 — 줌보존 + 로그개선 PASS | ✅ 완료 |
| B-5 | .dmg 패키징 — arm64(94MB) + x64(99MB) | ✅ 완료 |

---

## Agent Corps D-4~D-5 — ✅ 완료

| Phase | 내용 | 상태 |
|-------|------|------|
| D-4 | VaultWatcher v3 디스패치 6파일 감시 + AG/Codex 실시간 연동 | ✅ 완료 (166초) |
| D-5 | Brain 관제 HUD + v3 IPC 프론트엔드 + Brain 동선 보강 | ✅ 완료 (287초) |

---

## 자동 트리거: Codex CLI + Gemini CLI — ✅ 완료 (2026-03-01)

목적: CC와 동일하게 Codex/AG도 Brain → 파일 작성 → 자동 실행 파이프라인 구축.

| Step | 내용 | 상태 |
|------|------|------|
| T-1 | Codex CLI DD — `codex exec` headless 확인, v0.104.0 | ✅ 완료 |
| T-2 | Gemini CLI DD — `gemini -p` headless 확인, v0.29.5 | ✅ 완료 |
| T-3 | task_bridge v4.2 — codex_runner.py + gemini_runner.py + 3엔진 자동 트리거 | ✅ 완료 (CC 257초) |
| T-4 | Deep Research MCP 수정 — outputs 파싱 + 폴링 재시도 + incomplete 처리 | ✅ 완료 |
| T-5 | 3엔진 E2E — CC ✅ / Codex ✅ (11초) / Gemini ✅ (13초) | ✅ PASS |

---

## VaultWatcher EIO 핫픽스 — ✅ 완료 (2026-03-01)

| 항목 | 내용 | 상태 |
|------|------|------|
| main.ts | process.stdout/stderr EIO/EPIPE 에러 핸들러 추가 | ✅ |
| VaultWatcher.ts | safeLog/safeError 래퍼 → console.log 14곳 교체 | ✅ |
| 빌드 검증 | tsc 0 에러, vite 빌드 성공 (35.20 kB) | ✅ |

소요: CC 48초

---

## Sprint 6: Brain-in-the-Loop (자율 에이전트화) — ⬜ 미착수

*참고: mrstack (github.com/whynowlab/mrstack) 아키텍처 벤치마크*
*3자회의: 2026-03-01 — Gemini/GPT/Brain 합의*

### S-1: Auto-Read Loop (최우선) — ✅ 완료 (2026-03-01)

목표: Brain이 엔진 결과를 자동으로 읽고 다음 행동을 결정하는 자율 루프

```
현재:  Brain → to_codex.md → Codex → from_codex.md → [사용자: "결과 확인해"] → Brain
목표:  Brain → to_codex.md → Codex → from_codex.md → [자동] Brain 읽기 → 다음 판단
```

| Step | 내용 | 상태 |
|------|------|------|
| S-1a | brain_callback.py 신규 — compact prompt + claude -p + 응답 파싱 | ✅ |
| S-1b | task_bridge v4.3 — Auto-Brain 콜백 통합 + 체이닝 + 가드레일 | ✅ |
| S-1c | 패치 2건 — chain depth 리셋 + 제목 파싱 정규식 보강 | ✅ |
| S-1d | 테스트 7건 PASS (pytest) | ✅ |
| S-1e | E2E — Brain→CC→from_→Auto-Brain→DONE→TG (32초+콜백) | ✅ PASS |

리스크: 매번 `claude -p` 프로세스 스폰 오버헤드 (GPT 지적)
대안: task_bridge가 결과를 요약해서 Brain에 전달 (프로세스 1회만)
예상: 3~4일

### S-2: LaunchAgent 데몬화 — ⬜

목표: task_bridge.py를 macOS 데몬으로 등록, 24h 상시 실행

| Step | 내용 | 상태 |
|------|------|------|
| S-2a | com.woosdom.taskbridge.plist 작성 (LaunchAgent) | ⬜ |
| S-2b | 자동 재시작 (KeepAlive) + 로그 경로 설정 | ⬜ |
| S-2c | 부팅 시 자동 시작 검증 | ⬜ |

예상: 1일
선행: S-1 완료

### S-3: 양방향 Telegram (Brain 원격 조종) — ⬜

목표: Telegram에서 Brain에게 지시 → 로컬 맥북에서 실행 → 결과 Telegram 회신
참고: mrstack은 `claude-code-telegram` (오픈소스)을 브릿지로 사용

```
현재:  시스템 → TG 알림 (일방향)
목표:  사용자 ↔ TG 봇 ↔ claude -p (Brain) ↔ 3엔진
       외출중/자기전에도 TG로 Brain에게 작업 지시 가능
```

| Step | 내용 | 상태 |
|------|------|------|
| S-3a | claude-code-telegram 설치 + Bot 연동 (기존 TG 봇 재활용) | ⬜ |
| S-3b | Brain 시스템 프롬프트 주입 — Obsidian MCP + 3엔진 위임 능력 부여 | ⬜ |
| S-3c | 보안 — chat_id 화이트리스트, 위험 명령 차단, 턴 제한 | ⬜ |
| S-3d | E2E — TG "Codex에 파이썬 스크립트 시켜" → 실행 → 결과 TG 회신 | ⬜ |

리스크: 보안 (인증/권한), Claude Max 토큰 소모
예상: 3~5일
선행: S-2 완료 (데몬 필수)

### S-4: 선제적 트리거 (후순위) — ⬜

목표: mrstack식 시스템 상태 감시 + 자동 개입

| Step | 내용 | 상태 |
|------|------|------|
| S-4a | 시스템 상태 수집 (배터리, CPU, git 상태, 활성 앱) | ⬜ |
| S-4b | 상태 분류 (CODING/BROWSING/BREAK/DEEP_WORK/AWAY) | ⬜ |
| S-4c | 트리거 엔진 (조건부 TG 알림 + Brain 자동 개입) | ⬜ |
| S-4d | 일일 코칭 리포트 (패턴 분석 + 생산성 메트릭) | ⬜ |

예상: 1~2주
선행: S-1~S-3 안정화 후

---

## Sprint 5-5: 안전장치 강화 (S-1과 병행) — ⬜

| 항목 | 내용 | 상태 |
|------|------|------|
| 승인 워크플로우 | 위험 작업 시 사용자 확인 필수 (S-1d에 통합) | ⬜ |
| 비용 모니터링 | 일일/주간 턴 소모 자동 리포트 | ⬜ |
| 롤백 전략 | 실패 시 자동 복구 / 재실행 | ⬜ |
| TG 알림 retry | 발송 실패 시 3회 재시도 + 지수 백오프 | ⬜ |
| 동적 턴 한도 | 작업 크기(S/M/L) 판별 → max-turns 자동 조절 | ⬜ |

---

## 실행 순서 요약

```
Track A (Codex 이식)            ✅ 완료
자동 트리거: CC                  ✅ 완료
Track B (앱 리팩토링+패키징)      ✅ 완료
Agent Corps D-4~D-5             ✅ 완료
자동 트리거: Codex+Gemini CLI    ✅ 완료 (2026-03-01)
VaultWatcher EIO 핫픽스          ✅ 완료 (2026-03-01)
────────────────────────────────────────
Sprint 6: Brain-in-the-Loop     ⬜ ← 현재 여기
  S-1: Auto-Read Loop           ⬜ (3~4일)
  S-2: LaunchAgent 데몬          ⬜ (1일)
  S-3: 양방향 Telegram           ⬜ (3~5일)
  S-4: 선제적 트리거             ⬜ (1~2주, 후순위)
Sprint 5-5 (안전장치, 병행)      ⬜
Project Crossy Week 1           ⬜
```

---

## 관련 프로젝트 위치
- `02_Projects/pixel-agents-woosdom/` — Electron 픽셀아트 앱 (.dmg 빌드 완료)
- `02_Projects/woosdom_app/` — PyWebView 대시보드
- `02_Projects/task_bridge/` — Task Bridge v4.2
- `00_System/Specs/agent_corps_spec.md` — Agent Corps 설계서
- GitHub: https://github.com/ahnsemble/Woosdom
- 참고: https://github.com/whynowlab/mrstack (mrstack — Brain-in-the-Loop 벤치마크)
- 참고: https://github.com/nicepkg/claude-code-telegram (S-3 텔레그램 브릿지)

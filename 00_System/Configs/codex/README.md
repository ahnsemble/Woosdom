# Codex 멀티에이전트 설정 — 설치 가이드
*생성: 2026-03-07 | Brain v3.1 기준*

## 파일 구조

```
00_System/Configs/codex/
├── config.toml                    ← 메인 설정 (9개 에이전트 등록)
└── agents/
    ├── compute-lead.toml          ← 연산 총괄 (T1, GPT-5.4)
├── sandbox-runner.toml        ← 코드 실행 (T2, GPT-5.3-Codex)
├── data-wrangler.toml         ← 데이터 전처리 (T2, GPT-5.3-Codex)
├── parallel-coordinator.toml  ← 병렬 오케스트레이션 (T2, GPT-5.3-Codex)
├── fin-quant.toml             ← 금융 수식 연산 (T2, GPT-5.4)
├── fin-backtester.toml        ← 백테스트/시뮬레이션 (T3, GPT-5.4)
├── eng-critic.toml            ← 코드 리뷰 (T1, GPT-5.4, 읽기 전용)
├── eng-refactorer.toml        ← 리팩토링 (T2, GPT-5.4)
└── res-experimenter.toml      ← PoC/벤치마크 (T2, GPT-5.4)
```

## 설치 방법

### 방법 1: 심볼릭 링크 (추천)
볼트 원본을 유지하면서 Codex가 읽도록 연결.

```bash
# 기존 config 백업
cp ~/.codex/config.toml ~/.codex/config.toml.bak 2>/dev/null

# 심볼릭 링크
ln -sf /Users/woosung/Desktop/Dev/Woosdom_Brain/00_System/Configs/codex/config.toml ~/.codex/config.toml
ln -sf /Users/woosung/Desktop/Dev/Woosdom_Brain/00_System/Configs/codex/agents ~/.codex/agents
```

### 방법 2: 직접 복사
```bash
cp /Users/woosung/Desktop/Dev/Woosdom_Brain/00_System/Configs/codex/config.toml ~/.codex/config.toml
cp -r /Users/woosung/Desktop/Dev/Woosdom_Brain/00_System/Configs/codex/agents/ ~/.codex/agents/
```

## 검증

```bash
# 설정 확인
codex --config-dump

# 에이전트 목록 확인
cat ~/.codex/config.toml | grep '\[agents\.'
```

## 에이전트 ↔ 우즈덤 매핑

| Codex 에이전트 | 우즈덤 ID | 부서 | 모델 | 핵심 역할 |
|---------------|-----------|------|------|----------|
| compute-lead | cmp-compute-lead | Compute | GPT-5.4 | 연산 총괄, 파이프라인 설계 |
| sandbox-runner | cmp-sandbox-runner | Compute | GPT-5.3-Codex | 코드 무변조 실행 |
| data-wrangler | cmp-data-wrangler | Compute | GPT-5.3-Codex | 데이터 전처리, 스키마 검증 |
| parallel-coordinator | cmp-parallel-coordinator | Compute | GPT-5.3-Codex | 병렬 연산, DAG 분석 |
| fin-quant | fin-quant | Finance | GPT-5.4 | FV/드리프트/샤프, 4중 Sanity Check |
| fin-backtester | fin-backtester | Finance | GPT-5.4 | Monte Carlo/Bootstrap, MDD 필터 |
| eng-critic | eng-critic | Engineering | GPT-5.4 | 코드 리뷰 (읽기 전용) |
| eng-refactorer | eng-refactorer | Engineering | GPT-5.4 | 리팩토링 (동작 불변) |
| res-experimenter | res-experimenter | Research | GPT-5.4 | PoC/벤치마크 (격리 실행) |

## 운용 방식

기존 to_codex.md 핸드오프와 병행 사용:
- **단일 작업**: to_codex.md → Codex 앱에서 수동 실행 (기존 방식)
- **멀티에이전트**: Codex가 자체적으로 역할 분배 (새 방식)

멀티에이전트 활성화 후 Codex에게:
> "compute-lead 역할로 이 백테스트를 실행해줘"

또는 복합 작업 시:
> "data-wrangler로 데이터 전처리하고, fin-quant로 FV 계산해줘"

## 주의사항
- `max_threads = 3`: 동시 에이전트 3개 제한 (Parallel Coordinator Hard Rule)
- `max_depth = 1`: 서브에이전트의 서브에이전트 소환 금지
- eng-critic은 `sandbox_permissions = "read-only"`: 코드 수정 물리적 차단
- 금융 파일(Rules.md, portfolio.json) 수정은 모든 에이전트에서 금지

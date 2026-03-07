# OpenAI Codex 멀티에이전트 효용성 검증

## 연구 범위와 전제

본 리서치는 **2026년 2월 23일(KST)** 시점에 공개된 1차 자료(공식 문서/공식 블로그/헬프센터)와 2차 자료(커뮤니티 포럼, GitHub 이슈, Reddit 사례)를 중심으로, **Codex의 “멀티태스크/멀티에이전트”가 Woosdom 워크플로우 병목(순차 수동 확인·전달)을 실질적으로 줄이는지**를 평가한다. citeturn21search0turn23view3turn13view0turn12view0turn20view0

용어는 아래처럼 구분한다.

- **멀티태스크(병렬 태스크)**: 서로 독립적인 “작업(Cloud task/Thread/Automation run 등)”을 동시에 여러 개 진행해 **대기 시간을 겹치게** 만드는 방식. (예: 동시에 3개 백테스트를 돌리고, 완료된 것부터 검토) citeturn17view0turn21search0turn14view0turn15view0  
- **멀티에이전트(서브에이전트/팀)**: “한 작업” 안에서 역할 분담된 여러 에이전트를 띄워 병렬로 탐색·검토·구현한 뒤 **하나의 합성 응답**으로 모으는 오케스트레이션. Codex CLI에서 “실험적 기능”으로 명시된다. citeturn13view0

또한 Codex는 “표면(surface)”이 여러 개다. (1) **Codex web(클라우드 작업)**, (2) **Codex 데스크톱 앱(로컬/워크트리 기반)**, (3) **CLI/IDE 확장(로컬 실행)**이 서로 다른 강점·제약을 갖는다. citeturn17view0turn21search0turn12view0turn20view0

## Codex 멀티에이전트 기능 현황

### 1) Codex의 정확한 기능 범위는 무엇인가?

**(1) 단일 태스크 비동기 실행 외에 병렬 처리 가능한가?**  
가능하다. Codex web(클라우드) 문서는 “백그라운드에서(병렬 포함) 작업할 수 있다”고 명시한다. citeturn17view0 또한 Codex 데스크톱 앱 소개 글은 “여러 에이전트를 동시에 관리, 병렬 작업 실행”을 핵심 가치로 제시한다. citeturn21search0

**(2) 태스크 간 의존성 체이닝(A 완료 → B 시작)을 정의할 수 있는가?**  
- “제품 기능으로 DAG(의존성 그래프)를 선언적으로 정의”하는 형태는, **문서상 명시적으로 보이지 않는다**(예: 워크플로 오케스트레이터 UI에서 A→B 연결). 따라서 “Codex 자체만으로 완전한 의존성 스케줄러”라고 말하긴 어렵다. (문서 부재 → 기능 확정 불가)  
- 다만 “현실적인 체이닝”은 3가지 경로로 가능하다.  
  1) **CLI 비대화형 모드(codex exec)**에 “resume”가 있어, 직전 세션을 이어 **2단계 파이프라인**처럼 운용할 수 있다. citeturn12view0  
  2) **Codex app의 Automations**는 “반복 작업을 스케줄”해 인박스에 결과를 쌓는다. 주기적 체이닝(매일/매주 반복)은 가능해진다. citeturn15view0  
  3) **외부 오케스트레이터(Agents SDK/MCP/CI)**로 “A 완료 이벤트 → B 실행”을 코딩으로 구현하는 방식이 가능하다(아래 11번에서 구체화). citeturn19search15turn12view0

정리하면 “Codex 단독의 DAG 선언 기능”은 확인되지 않지만, **세션 재개·스케줄·외부 오케스트레이션**으로 체이닝은 구현 가능하다. citeturn12view0turn15view0turn19search15

**(3) 동시 실행 가능한 태스크 수 제한이 있는가?**  
- **멀티에이전트(서브에이전트 스레드)** 관점에서는, CLI 설정에 `agents.max_threads`가 “동시에 열어둘 수 있는 에이전트 스레드 최대치”로 존재한다. 즉, 최소한 “제한을 둘 수 있는 훅”이 공식화되어 있다. citeturn13view0  
- **클라우드 태스크/앱 스레드** 관점에서는, “정확한 동시 실행 상한(숫자)”이 문서에 고정값으로 박혀 있진 않다. 대신 (a) 요금제/사용량 한도, (b) 크레딧 추가 구매, (c) 사용 제한 도달 시 모델을 더 작은 것으로 바꾸라는 가이드가 존재한다. citeturn11search0turn11search4turn20view0  
- 실제로 “서브에이전트를 여러 개 동시에 띄우면 사용량이 급격히 소모된다”는 사용자 보고가 GitHub 이슈로 다수 존재한다(버그/정책/계측 문제일 가능성 포함). citeturn19search20

따라서 **기술적으로 병렬은 되지만, 운영상(쿼터·크레딧·설정 max_threads) 제약이 곧 동시성 상한**이 된다. citeturn13view0turn11search0turn19search20

**(4) 태스크별로 다른 모델(GPT‑4o, GPT‑5.2, o1 등)을 선택할 수 있는가?**  
Codex에서 “모델 선택”은 일반 챗 모델 전체를 의미하기보다 **Codex용 모델 패밀리(예: gpt‑5.3‑codex, spark, mini 등)** 중심으로 문서화되어 있다. 예를 들어, 멀티에이전트 기능 문서는 에이전트 역할별 설정에서 `model`을 오버라이드할 수 있고(역할별 모델 상이 가능), 예시로 **gpt‑5.3‑codex / gpt‑5.3‑codex‑spark**를 든다. citeturn13view0turn23view3 또한 사용량 한도 접근 시 **GPT‑5.1‑Codex‑Mini로 전환**하라고 명시된다. citeturn11search0

즉 “태스크/에이전트 역할별로 모델을 다르게”는 가능하나, 그것이 GPT‑4o/o1 같은 범용 모델까지 동일하게 혼용되는지는 **Codex 문서 범위 내에선 확정하기 어렵다**(Codex는 Codex 에이전트/코딩에 특화된 모델 라인으로 설명됨). citeturn13view0turn11search0turn17view0

아래는 이 섹션의 핵심 출처(URL)이다.
```text
https://developers.openai.com/codex/cloud
https://openai.com/index/introducing-the-codex-app/
https://developers.openai.com/codex/multi-agent/
https://developers.openai.com/codex/noninteractive
https://developers.openai.com/codex/pricing/
https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan
```

image_group{"layout":"carousel","aspect_ratio":"16:9","query":["OpenAI Codex app worktrees screenshot","OpenAI Codex app automations inbox screenshot","OpenAI Codex CLI multi-agent /agent screenshot","Codex web cloud task GitHub PR screenshot"],"num_per_query":1}

### 2) Codex에서 에이전트 간 컨텍스트/파일 공유는 어떻게 동작하는가?

질문이 “태스크 A가 만든 파일을 태스크 B가 자동 참조”하는 수준까지 내려가면, Codex는 **기본적으로 ‘격리 + 명시적 동기화(또는 동일 작업공간)’** 쪽에 가깝다.

**(1) 태스크 A가 생성한 파일을 태스크 B가 자동으로 참조할 수 있는가?**  
- Codex 앱에서 병렬 작업의 기본 단위는 “스레드(Thread) + 작업 대상(Local/Worktree/Cloud)”이며, 특히 “Worktree”는 **리포지토리의 두 번째 체크아웃(파일 전체 복사)** 로 격리를 만든다. Worktree는 각각 독립 파일 사본이므로, **A 워크트리에서 생성한 파일이 B 워크트리에 자동으로 생기지 않는다**. 대신 “Sync with local(Apply/Overwrite)” 같은 동기화 기능으로 이동시킨다. citeturn14view0  
- `.gitignore`에 포함된 파일은 워크트리 동기화 시 “전송되지 않는다”는 제한이 공식 문서에 명시되어 있어, 데이터셋/결과 파일 공유에서 병목이 될 수 있다. citeturn14view0 이 “.gitignore 데이터 공유 문제”는 커뮤니티에서도 실제 운영상의 함정으로 언급된다. citeturn19search26  
- Codex cloud는 태스크마다 컨테이너를 만들고 리포지토리를 체크아웃하는 모델로 설명된다. 따라서 A 컨테이너의 산출물이 곧바로 B 컨테이너에 공유된다고 보긴 어렵다(기본은 태스크 단위 격리). citeturn7view2

결론적으로 “자동 참조”보다는, **같은 작업공간(같은 워크트리/같은 로컬 디렉토리)에서 수행**하거나 **Git/동기화 절차로 명시적으로 전달**하는 방식이 현실적이다. citeturn14view0turn7view2

**(2) 공유 워크스페이스/리포지토리 개념이 있는가?**  
- Codex web은 GitHub 계정 연결을 전제로 “리포지토리에서 작업하고 PR을 만든다”고 설명한다. 즉, 공유 단위는 “GitHub 리포지토리”이며, 작업 자체는 클라우드 태스크 컨테이너로 수행된다. citeturn17view0turn16view0  
- Codex app은 프로젝트 단위로 스레드를 조직화하고, 같은 프로젝트(= 로컬 체크아웃)에서 Worktree를 여러 개 만들어 병렬 작업을 수행하도록 설계되어 있다. citeturn21search0turn14view0

**(3) 에이전트 간 메시지 패싱/이벤트 시스템이 있는가?**  
두 층이 있다.

- **내부 오케스트레이션(에이전트↔에이전트)**: 멀티에이전트 기능은 “서브에이전트를 병렬로 띄우고, 후속 지시를 라우팅하고, 결과를 기다려 합성 응답을 반환”한다고 문서에 명시된다. 즉, Codex 내부적으로는 라우팅/대기/스레드 종료 같은 오케스트레이션이 존재한다. citeturn13view0  
- **외부 연동(시스템↔Codex)**: `codex exec --json`은 실행 중 발생하는 이벤트를 JSONL 스트림으로 내보내며, `thread.started`, `turn.completed`, `turn.failed`, `item.*` 등 이벤트 타입이 명시돼 있다. 이는 “이벤트 시스템”에 가깝고, 외부 오케스트레이터가 폴링/파이핑하기 쉬운 형태다. citeturn12view0

추가로, Codex app server는 WebSocket 모드에서 “bounded queue” 및 과부하 시 `-32001`로 거절하고 **클라이언트가 지수 백오프 재시도**하라고 설명한다(외부 시스템 연동 설계 관점에서 중요한 제약). citeturn2view1

아래는 이 섹션의 핵심 출처(URL)이다.
```text
https://developers.openai.com/codex/app/worktrees
https://developers.openai.com/codex/cloud/environments
https://developers.openai.com/codex/multi-agent/
https://developers.openai.com/codex/noninteractive
https://developers.openai.com/codex/automation/app-server/
```

### 3) Codex의 CLI / API 접근은 가능한가?

**(1) CLI로 태스크 생성/실행 및 결과 폴링이 가능한가?**  
가능하다. `codex exec`는 “스크립트/CI에서 Codex를 비대화형으로 실행”하기 위한 모드이고, 최종 메시지를 stdout으로 내보내거나, JSONL 이벤트 스트림을 내보내 머신이 읽도록 설계되었다. citeturn12view0 또한 세션을 이어가는 `resume` 기능도 문서화되어 있어 파이프라인형 운용이 가능하다. citeturn12view0

**(2) 프로그래밍 방식으로 태스크를 생성하고 결과를 폴링할 수 있는가?**  
- **가장 보수적/안정적인 방법**: 외부 프로세스에서 `codex exec --json`을 실행하고 JSONL 이벤트를 수집(=폴링/스트리밍)한다. 이벤트 타입·예시가 공식 문서에 명시되어 있다. citeturn12view0  
- **더 깊은 통합**: Codex app server는 JSON‑RPC API를 제공하며(예: WebSocket), 과부하·재시도 가이드를 포함한다. citeturn2view1  
- **SDK 계층**: 문서상 “Codex SDK”가 별도 항목으로 존재한다(세부는 표면상 문서 참조 링크로 제공). citeturn2view0

**(3) MCP 서버로 래핑하여 외부 시스템(Brain)이 직접 호출 가능한가?**  
가능하다. “Agents SDK로 Codex를 사용” 가이드는 **Codex CLI를 MCP 서버로 띄우고**, Agents SDK가 그 MCP 서버의 도구(`codex()`, `codex-reply()`)를 호출하는 구조를 명시한다. “Codex를 여러 턴에 걸쳐 살아있게 유지한다(keeps alive across multiple agent turns)”는 점이 Woosdom의 ‘비동기 실행 엔진’ 역할과 정합성이 높다. citeturn19search15

**(4) GitHub/GitLab 리포지토리 통합 수준은?**  
- GitHub 통합은 매우 구체적으로 문서화되어 있다. 예를 들어 PR 코멘트에 `@codex review`를 남기면 Codex가 GitHub 코드리뷰를 पोस्ट하고, “자동 리뷰” 옵션도 제공한다. citeturn16view0 또한 `@codex` 멘션으로 리뷰 외 작업을 시키면 “PR 컨텍스트로 클라우드 태스크를 시작한다”고 명시된다. citeturn16view0  
- Codex web(클라우드 태스크)은 “GitHub 계정 연결”을 전제로 하며, 이를 통해 리포지토리에서 작업하고 PR을 만들 수 있다고 밝힌다. citeturn17view0  
- 반면 GitLab은 Codex 문서의 “1차 통합(Connect GitLab)”로 나타나지 않는다. 따라서 **Codex cloud의 정식 통합 채널은 GitHub 중심**으로 보는 게 안전하다. (GitLab은 로컬/CLI에서 `git clone`로 사용하는 방식은 가능하겠지만, cloud 연결은 문서로 확인되지 않음) citeturn17view0

또한, GitHub 자체가 “여러 AI 코딩 에이전트를 관리하는 허브(Agent HQ)와, Codex/Claude 통합”을 확장하는 흐름이 있다는 보도도 있어, GitHub 표면에서의 멀티에이전트 운영이 더 강화되는 신호로 읽을 수 있다. citeturn19news44

아래는 이 섹션의 핵심 출처(URL)이다.
```text
https://developers.openai.com/codex/noninteractive
https://developers.openai.com/codex/integrations/github
https://developers.openai.com/codex/cloud
https://developers.openai.com/codex/guides/agents-sdk/
https://developers.openai.com/codex/automation/app-server/
```

### 4) Codex의 알려진 제한사항과 버그는 무엇인가?

**(1) 실행/보안/네트워크 제한(공식 문서 기반)**  
- 기본적으로 **네트워크 접근은 꺼져 있으며**, 로컬 실행 시 OS 샌드박스로 작업공간 접근을 제한한다. citeturn20view0  
- Codex cloud는 컨테이너 기반이며, “Setup phase(설치 스크립트)에서는 네트워크가 가능”하지만 “Agent phase(에이전트 실행)에서 인터넷은 기본 off, 설정으로 제한/무제한 가능”이라고 명시된다. citeturn7view2turn20view0  
- Cloud environments에서 **Secrets는 setup script에만 제공되고, 보안상 agent phase 시작 전에 제거**된다고 명시된다. 이는 “백테스트 데이터/API 키를 에이전트가 런타임에 계속 써야 하는 설계”일 때 제약이 될 수 있다. citeturn7view2  
- 컨테이너 캐시는 “최대 12시간” 공유/재사용될 수 있다(재실행 시 속도·재현성에 영향). citeturn7view2  
- Automations는 “Codex 앱이 실행 중이어야 하며, 선택 프로젝트가 디스크에 있어야 한다”고 명시된다. 즉 “서버처럼 24/7 완전 무중단 자동화”는 앱 실행 상태에 종속된다. citeturn15view0

**(2) 워크트리/세션 운용 제한(공식 문서 기반)**  
- Worktree는 Git 리포지토리에서만 동작한다. citeturn14view0turn12view0  
- 동일 브랜치를 동시에 여러 worktree에 checkout할 수 없는 Git 제약이 있고, Codex 문서가 그 이유와 오류까지 설명한다. citeturn14view0  
- “세션을 워크트리 간 이동”은 “아직 불가(Not yet)”로 FAQ에 명시된다. 환경을 바꾸려면 새 스레드를 시작하고 프롬프트를 재진술해야 한다. citeturn14view0  
- Worktree 청소 정책(디스크 공간 통제): “4일 초과” 또는 “10개 초과” 조건에서 정리될 수 있고, 스냅샷 복구를 제공한다고 명시된다. citeturn19search2turn14view0

**(3) 런타임/시간 제한에 대한 신호(공식·보도 혼합)**  
- Codex 앱 소개 글은 “작업이 hours, days, weeks에 걸칠 수 있다”는 흐름을 제시한다. citeturn21search0  
- TechCrunch 보도는 “Codex가 모델 업데이트를 통해 수 초에서 최대 7시간까지 작업할 수 있다”는 내용을 전한다. citeturn21search18  
- (반면, “보통 1~30분”과 같은 평균적 수행 시간 언급은 과거 출시 문맥에서 발견되며, 시점/모델/표면에 따라 달라질 수 있다.) citeturn1view1

따라서 “당신의 55억 조합/50K bootstrap 같은 장시간 계산”이 **Codex cloud 단일 태스크로 안정 수행된다고 단정하긴 어렵고**, 표면(로컬 vs cloud)과 모델(예: GPT‑5.3‑Codex) 및 정책(쿼터/승인/네트워크)에 따라 편차가 크다고 보는 게 안전하다. citeturn21search0turn21search18turn23view3turn20view0

**(4) 알려진 버그/마찰(커뮤니티·이슈 기반: “보고됨”)**  
아래는 “문서에 없는 현실 운용 마찰”로, **공식 확정이라기보다 사용자 보고**라는 점을 전제로 한다.

- **네트워크 접근이 설정돼 있어도 매번 승인을 요구**한다는 이슈(샌드박스/승인 정책 상호작용 문제로 추정). citeturn20view2  
- **서브에이전트 완료 신호를 메인 에이전트가 못 받아 대기 상태로 멈춤**(멀티에이전트 워크플로우 신뢰성에 직접 타격). citeturn19search8  
- **멀티 워커를 쓴 뒤 스레드 전환 시 이전 질문을 반복**하는 문제 보고. citeturn19search0  
- **동시에 여러 서브에이전트를 띄우면 사용량 쿼터가 즉시 소모**된다는 보고(계측/요금화/버그 여부는 추가 확인 필요). citeturn19search20  
- **Worktree UI가 업데이트 후 사라졌다**는 앱 이슈(기능 토글/릴리즈 안정성 문제 신호). citeturn19search6  
- **VSCode 확장/윈도우에서 과도한 승인 클릭**의 불편 사례가 커뮤니티에 장기간 존재. citeturn20view1turn20view0  
- **MCP 서버를 많이 붙이고 병렬 스레드를 오래 돌리면 메모리를 많이 먹는다**는 보고. citeturn21search16  
- Windows 샌드박스는 “실험적이며 중요한 제한이 있다”고 공식 문서에 명시되어, 플랫폼별 편차/버그 가능성이 구조적으로 크다. citeturn20view0turn19search25

아래는 이 섹션의 핵심 출처(URL)이다.
```text
https://developers.openai.com/codex/security/
https://developers.openai.com/codex/cloud/environments
https://developers.openai.com/codex/app/worktrees
https://github.com/openai/codex/issues/9298
https://github.com/openai/codex/issues/9607
https://github.com/openai/codex/issues/12184
https://github.com/openai/codex/issues/9748
https://github.com/openai/codex/issues/11181
https://community.openai.com/t/codex-vscode-extension-agent-full-access-always-asks-for-approval/1355908
```

## 비교 분석: Codex vs 경쟁 도구

### 5) Codex vs Antigravity vs Claude Code vs Cursor vs Devin vs Replit Agent 비교표

아래 표는 “비동기 코드 실행 + 멀티태스크/멀티에이전트” 관점으로 요약했다. (세부 기능은 제품 업데이트로 수시 변동 가능)

| 도구 | 병렬 태스크/에이전트 지원 | 태스크 체이닝/의존성 관리 | CLI/API 접근성 | 외부 파일시스템/Repo 접근 | 비용 구조(요약) | 코드 실행 환경 |
|---|---|---|---|---|---|---|
| Codex | Cloud에서 **병렬 백그라운드 태스크** 가능, App에서 **멀티 스레드/Worktree 병렬**, CLI에서 **실험적 멀티에이전트** citeturn17view0turn21search0turn13view0 | “DAG 선언”은 불명확. 대신 `codex exec resume`로 단계형 파이프라인, App Automations로 스케줄 기반 반복 가능 citeturn12view0turn15view0 | `codex exec --json`(이벤트 스트림), App Server(JSON‑RPC), MCP 서버/Agents SDK 연동 가이드 존재 citeturn12view0turn2view1turn19search15 | Cloud는 GitHub 연결 기반 repo 작업/PR, App는 로컬+Worktree(격리/Sync), `.gitignore` 전송 제한 citeturn17view0turn14view0 | ChatGPT 요금제에 포함 + 한도 초과 시 크레딧 구매, 모델 다운시프트 권장 citeturn11search4turn11search0turn11search10 | Cloud 컨테이너(환경 설정/캐시), 로컬 OS 샌드박스(승인 정책) citeturn7view2turn20view0 |
| Antigravity | Agent Manager로 “여러 에이전트/워크스페이스 병렬 관리”를 전면에 둠 citeturn9search5turn9news38 | (IDE 내 오케스트레이션은 가능) “의존성 DAG”는 문서 확인 필요 → [추정] | (공식 CLI/API 범위) 이 리서치 범위 내에 확정 자료 부족 → [추정] | IDE/워크스페이스 중심(에이전트가 에디터/터미널/브라우저 사용) citeturn9news38 | 공개 프리뷰 무료+레이트리밋(리셋) 언급 citeturn9news38 | 로컬 IDE 기반(모델이 도구 사용) citeturn9news38 |
| Claude Code | Agent Teams로 **여러 세션 병렬**, 서브에이전트/팀 개념 분리 citeturn9search0turn9search24turn9search12 | 팀 리드가 분배/요약(오케스트레이션). “의존성 그래프 선언”은 명시적 제품 기능이라기보다 운영 패턴에 가까움 citeturn9search0 | 문서 기반 CLI 도구 성격(구체 API는 별도) citeturn9search0turn9search8 | 로컬 코드베이스/세션 컨텍스트 기반 citeturn9search0 | Claude Pro에 포함(“Includes Claude Code”) citeturn11search1 | 로컬 실행(세션/도구 사용) citeturn9search0 |
| Cursor | “한 프롬프트에서 최대 8 에이전트 병렬”, Git worktree/원격 머신으로 격리 citeturn9search1turn9search4 | 기본은 병렬 결과 비교/선택(의존성 체이닝은 사용자 작업 설계) [추정] | 별도 제품(편집기/CLI) 존재. 비용/크레딧 구조 문서화 citeturn11search2turn9search6 | 로컬 repo + worktree 격리(또는 원격) citeturn9search1 | 구독 + 포함 크레딧/에이전트 사용량 citeturn11search2turn11search5 | 로컬/원격 혼합(에디터 중심) citeturn9search1 |
| Devin | “여러 병렬 Devin 인스턴스” 및 동시 세션(최대 10 등 플랜 표기) citeturn9search14turn11search3 | 티켓→계획→테스트→PR 흐름 중심(의존성 선언보단 제품 플로우) citeturn9search2turn9search10 | 웹/제품 중심(정식 API 범위는 별도 확인 필요) [추정] | 클라우드 IDE/VM 격리, repo/도구 연동 citeturn9search14turn9search10 | ACU(Agent Compute Unit) 기반 과금 citeturn11search3turn11search6 | 클라우드 격리 IDE/VM citeturn9search14turn9search10 |
| Replit Agent | “자율 빌드/장시간 빌드”, 내부적으로 멀티에이전트 아키텍처 소개 citeturn10search3turn10search28 | Replit Workflows는 태스크 병렬 실행 모드 문서화(워크플로 수준) citeturn10search10turn10search35 | 플랫폼 내 기능 중심(외부 API는 별도 확인 필요) [추정] | 브라우저 기반 클라우드 워크스페이스/실행 citeturn10search14turn10search26 | 구독 + 크레딧/사용량(코어 $20 등) citeturn10search1turn10search7turn10search27 | 클라우드 실행/스냅샷·격리 등 안전장치 citeturn10search26turn10search14 |

(표 주의) Antigravity/Devin/Replit의 “정식 API/CLI”는 제품마다 계속 변하고, 문서 범위에서 확정되지 않은 항목은 [추정]으로 처리했다.

아래는 이 섹션의 핵심 출처(URL)이다.
```text
https://developers.openai.com/codex/cloud
https://openai.com/index/introducing-the-codex-app/
https://developers.openai.com/codex/multi-agent/
https://developers.openai.com/codex/noninteractive
https://antigravity.google/docs/agent-manager
https://www.theverge.com/news/822833/google-antigravity-ide-coding-agent-gemini-3-pro
https://code.claude.com/docs/en/agent-teams
https://claude.com/pricing
https://cursor.com/changelog/2-0
https://cursor.com/docs/account/pricing
https://devin.ai/pricing/
https://docs.replit.com/replit-workspace/workflows
https://replit.com/pricing
```

### 6) 2026년 현재, 개인 개발자의 “복잡한 Python 작업 비동기 실행”에 가장 효율적인 도구는?

결론부터 말하면, “복잡한 Python 작업”이 **(A) 대규모 병렬 계산**인지, **(B) 코드베이스 변경+테스트+PR**인지에 따라 최적 도구가 갈린다.

- **(A) 대규모 병렬 계산(예: 조합 탐색/부트스트랩/몬테카를로)**  
  Codex 자체는 “코딩 에이전트 + 실행”에 강하지만, “55억 조합”급 계산을 Codex 단일 런타임에 온전히 얹는 것은 **쿼터/시간/환경 제약과 충돌할 가능성**이 높다. citeturn21search18turn20view0turn11search0  
  이 경우에는 **계산을 전담하는 실행 플랫폼**(예: Modal, GitHub Actions matrix fan‑out 등)을 두고, Codex는 코드를 생성/검증/리포트화하는 조력자로 두는 구조가 효율적일 가능성이 높다. Modal은 “배치 잡을 대규모 병렬로 스케일”한다고 소개하고, 함수 `.map()`으로 병렬 실행을 제공한다. citeturn22search6turn22search2 GitHub Actions도 matrix 전략과 `max-parallel`로 동시 실행 잡 수를 제어할 수 있다. citeturn22search0turn22search4  
  ⇒ **추천(계산 중심)**: “Modal/GitHub Actions + Codex(코드 작성·검증·리포트)”가 비용·확장성 측면에서 유리할 수 있음. (당신의 워크로드 특성상 특히) citeturn22search2turn22search0turn12view0

- **(B) repo 기반 분석/구현/테스트/PR 생성(엔지니어링 워크플로우)**  
  Codex web은 GitHub 연결 후 “클라우드에서 병렬 백그라운드 작업 + PR 생성”을 목표로 설계되어 있고, GitHub에서 `@codex` 멘션으로 작업 트리거도 지원한다. citeturn17view0turn16view0 또한 Codex는 CLI의 `codex exec`로 CI 파이프라인에 넣기 쉬우며, JSONL 이벤트로 결과를 기계적으로 수집 가능하다. citeturn12view0  
  ⇒ **추천(엔지니어링 자동화 중심)**: Codex가 “비동기 실행 엔진”으로 가장 정합성이 높다.

- **(C) 모델 실행(특히 ML inference) 비동기화**  
  Replicate는 API 기본 동작이 async이며 prediction ID를 즉시 반환하고, 웹훅으로 완료 이벤트를 받을 수 있다. citeturn22search3turn22search7 (다만 이는 “Python 시뮬레이션”이라기보다 “모델 추론” 범주에 더 적합)

정리하면, 당신의 “Stage 1~4 백테스트”는 계산 집약도가 매우 높기 때문에, **Codex를 ‘계산기’로 쓰기보다 ‘오케스트레이터/자동화 러너’로 쓰고 계산은 별도 실행면으로 분리하는 설계가 장기적으로 더 견고**할 가능성이 크다. citeturn22search2turn22search0turn12view0turn20view0

## 멀티태스크 병렬 실행의 실질 효용

### 7) 개인 사용자가 Codex 멀티태스크 병렬 실행으로 생산성 향상을 보고한 사례가 있는가?

**있다(사례는 많음). 다만 “정량 수치(시간 단축 %)”가 공개적으로 일관되게 보고된 자료는 상대적으로 부족**하다.

- **공식 케이스 스터디(조직 사용자)**: Datadog 사례에서 “1,000명 이상이 정기적으로 사용”한다고 언급되며, “시간 절약이 크다”는 서술이 있으나, “정식 툴 내 지표로 계량한다”기보다 Slack 공유 같은 정성 피드백 중심으로 설명된다. 즉, **효용은 인정하지만 정량 KPI가 공개된 구조는 아니다**. citeturn23view0  
- **개인 사용자 커뮤니티(정성·혼재)**: Reddit에서는 “반복 작업(보일러플레이트/테스트 스켈레톤/요약 자동화)이 시간을 절약한다”는 글이 있으나, 구체 %는 드물다. citeturn21search2 반대로 “출력 정리에 시간이 더 든다”는 회의적 경험담도 공존한다. citeturn21search9  
- **Codex 앱/워크트리 사용자 경험(정성)**: 워크트리로 여러 스레드를 동시에 돌리는 패턴이 “게임 체인저”라거나, “병렬이 검증 가능할 때만 가치가 있다”는 식의 현장 조언이 보이지만, 역시 수치화는 제한적이다. citeturn21search8turn21search23

따라서 “Codex 병렬 기능이 생산성을 높인다”는 **정성 신호는 강하지만**, 당신이 원하는 “시간 단축 비율”을 바로 가져다 쓸 만큼의 공개 정량 데이터는 부족하다(이 자체가 중요한 시그널). citeturn23view0turn21search2turn21search9

### 8) Codex에 동시에 여러 백테스팅 태스크를 던지는 것이 기술적으로 가능한가?

**가능은 하다. 다만 ‘어디에서 실행하느냐(Local/Worktree/Cloud)’에 따라 효율이 달라진다.**

- **Codex web(클라우드)**: “클라우드 환경에서 병렬 백그라운드 작업”이 가능하다고 명시된다. citeturn17view0 즉 Track A/B/C를 별도 태스크로 동시에 시작하는 것은 제품 의도와 부합한다.  
- **Codex app(로컬 + Worktree)**: Worktree는 “동일 프로젝트에서 서로 간섭 없이 다중 독립 태스크를 병렬 실행”하게 해준다. citeturn14view0turn21search0 다만 Worktree가 많아지면 디스크 공간과 청소 정책(4일/10개)이 운영 이슈가 된다. citeturn19search2  
- **Codex CLI 멀티에이전트(한 작업 내 분업)**: “서브에이전트를 병렬로 띄워 결과를 모아 한 번에 응답”이 가능하지만, 이는 계산 트랙을 동시에 ‘실행’한다기보다 **탐색/구현/검토** 같은 지식 작업 분업에 더 적합하다. citeturn13view0

**같은 데이터셋을 여러 태스크가 참조해야 할 때의 처리 방식(핵심)**  
- Cloud에서는 “setup script 단계에서 인터넷 접근이 가능”하고, agent 단계는 기본적으로 인터넷이 꺼져 있으므로, **데이터를 setup 단계에서 내려받아 작업공간에 두는 패턴**이 가장 안정적이다. citeturn7view2turn20view0  
- 단, Cloud environments에서 secrets가 agent 단계 전에 제거되므로, S3/API 토큰 같은 비밀값이 런타임에 계속 필요하면 설계를 바꿔야 한다(예: setup 단계에서 필요한 데이터를 모두 스테이징). citeturn7view2  
- 컨테이너 캐시가 최대 12시간 유지되므로, 동일 환경/리포에 대해 짧은 간격으로 여러 태스크를 돌릴 때 “의존성 설치·데이터 준비”가 반복되지 않게 만드는 여지가 있다. citeturn7view2  
- 로컬 Worktree에서는 `.gitignore` 파일이 동기화에서 제외될 수 있어, 데이터 파일을 `.gitignore`에 넣는 습관이 있으면 공유가 깨질 수 있다. citeturn14view0turn19search26

요약하면: **Track 병렬 실행은 ‘기술적으로 가능’**하나, 데이터 공유·시크릿·네트워크 정책 때문에 “파이프라인 설계”가 실사용 성패를 가른다. citeturn7view2turn14view0turn17view0

### 9) 멀티태스크 실행이 오히려 비효율적인 경우는 언제인가?

Codex 맥락에서 특히 뼈아픈 비효율은 “병렬화로 인간 병목이 사라지지 않는데 비용/검증 부하가 늘어나는 경우”다.

- **(1) 실패 연쇄/대기 정지**: 서브에이전트 완료 신호를 못 받아 메인 에이전트가 멈추는 보고가 있다. 병렬로 여러 개를 띄울수록 “하나라도 stuck → 전체 진행 지연”이 생긴다. citeturn19search8turn13view0  
- **(2) 승인/권한 오버헤드**: 네트워크/명령 실행 승인 프롬프트가 과도해 “자동화가 반자동 클릭 노동”으로 변질되는 문제가 커뮤니티에서 지속 보고됐다. citeturn20view1turn20view0 병렬로 태스크 수가 늘면 승인도 선형(혹은 그 이상)으로 늘 수 있다.  
- **(3) 사용량/비용 폭증 리스크**: “여러 서브에이전트를 동시에 띄우면 플랜 쿼터가 즉시 소모”된다는 보고가 있다. 사실이라면 병렬화가 곧 비용 폭발 트리거가 된다. citeturn19search20turn11search0turn11search10  
- **(4) 결과 머지/검증이 인간 병목**: Worktree 기반 병렬은 충돌을 줄이지만, 결국 “Sync/Apply/Overwrite/PR 리뷰”가 인간 병목이 될 수 있다. citeturn14view0turn21search0  
- **(5) MCP/통합이 무거울수록 안정성 저하**: MCP 서버를 많이 연결하고 병렬 스레드가 많으면 메모리 문제가 보고된다. citeturn21search16turn18view0

따라서 병렬화의 손익은 “(절약된 대기 시간) > (승인·검증·비용·불안정성)”일 때만 성립한다. 이 손익분기 판단은 작업 성격에 따라 다르며, 아래 10번에서 패턴별로 [추정]치를 제시한다. citeturn14view0turn19search20turn20view0

## Woosdom 적용 시나리오와 대안

### 10) 패턴 A/B/C별 Codex 멀티태스크 활용 시 예상 시간 절감률과 품질 변화는?

아래 수치는 **당신의 워크로드 설명만으로 계산한 추정치**이며, 실제는 (1) 계산 시간 비중, (2) 승인 정책, (3) 데이터 공유 설계, (4) 쿼터/크레딧, (5) 검증 자동화 수준에 따라 크게 달라진다. 따라서 전부 **[추정]** 으로 표기한다. (기능 가능성 자체는 공식 문서로 근거) citeturn17view0turn14view0turn15view0turn12view0

**패턴 A — 포트폴리오 백테스팅(Stage 1~4 순차)**  
- **현실적인 병렬화 범위**: Stage 의존성이 강해(상위 15,000개 재평가/부트스트랩/시각화) “계산 그 자체”를 병렬 태스크만으로 직렬→병렬로 뒤집기 어렵다. 대신 병렬화의 핵심은 “(a) 다음 단계 코드/리포트 템플릿을 미리 준비, (b) 여러 시나리오(파라미터/리스크 모델)를 동시에 평가, (c) 검증·리포트 생성 자동화”로 이동한다. citeturn12view0turn15view0turn14view0  
- **예상 시간 절감률**:  
  - (인간 대기·수동 릴레이 기준) **15~35% 절감 [추정]** — Codex web/cloud 병렬 태스크 또는 app worktree로 Track을 동시에 돌리되, “데이터 준비(Setup phase) + 결과 인박스화(Automations/CI)”로 자신이 확인하는 타이밍을 배치 처리하면서 줄어드는 폭. citeturn17view0turn7view2turn15view0  
  - (총 wall-clock, 계산 포함) **0~20% 절감 [추정]** — 계산이 지배적이면 병렬이 오히려 로컬 자원 경합을 일으켜 느려질 수도 있다(특히 로컬 worktree 동시 실행). 로컬 자원 경합은 공식 문서에 직접 숫자로 없으므로 추정.  
- **품질 변화**:  
  - 긍정: 자동화된 리포트/검증 루프가 붙으면 재현성과 점검 폭이 늘어 품질이 좋아질 수 있음 **[추정]**  
  - 부정: 병렬로 결과가 쏟아지면 “선별/검증 비용”이 늘어 품질이 들쭉날쭉해질 수 있음. (Worktree/승인/검증 병목) citeturn14view0turn20view0

**패턴 B — MCP 도구 개발(TypeScript 코드 생성→빌드 테스트→반영)**  
- **병렬화 포인트**: (1) 구현, (2) 테스트 작성/실행, (3) 리뷰/보안 점검을 워크트리 또는 멀티에이전트 역할로 분업하기가 쉽다. Codex 멀티에이전트는 “PR/코드베이스 탐색처럼 병렬 가능한 복잡 작업에 유용”하다고 명시한다. citeturn13view0turn14view0  
- **예상 시간 절감률**: **25~50% 절감 [추정]** — 특히 `codex exec`를 CI에 붙여 “빌드 실패→자동 수정 PR” 같은 루프를 만들면 수동 왕복이 줄어드는 폭이 크다. citeturn12view0turn16view0  
- **품질 변화**:  
  - 긍정: 독립 reviewer 역할(모델/지시문 분리)로 보안/정확성 체크가 강화될 수 있음. (역할별 모델/지시문 오버라이드) citeturn13view0  
  - 부정: 멀티에이전트가 실험적이어서 stuck/완료 신호 문제 등이 품질·속도에 악영향 가능. citeturn19search8turn13view0

**패턴 C — 데이터 수집 + 전처리(ETF 가격/CSV 생성)**  
- **병렬화 포인트**: (1) 수집, (2) 전처리/결측 처리, (3) 품질 검증(교차검증), (4) 리포트 생성은 비교적 독립적이다. 또한 Automations는 “반복 작업을 백그라운드에서 실행하고 인박스에 쌓는다”고 명시되어, “매번 수동 실행” 병목을 직접 겨냥한다. citeturn15view0turn21search0  
- **예상 시간 절감률**: **30~60% 절감 [추정]** — 데이터 파이프라인은 반복성이 강하므로 스케줄·자동검증·요약이 붙으면 체감 절감이 크다. 다만 앱이 켜져 있어야 한다는 운영 제약이 있다. citeturn15view0  
- **품질 변화**: **개선 가능성이 큼 [추정]** — 반복 작업을 “같은 명령/같은 환경”에서 돌리면 재현성이 좋아진다(단, secrets가 agent phase에서 제거되는 cloud 제약 등 설계 필요). citeturn7view2turn15view0

---

간단 요약: **MCP 도구 개발(B)과 데이터 파이프라인(C)** 는 병렬/자동화로 이득이 크고, **대규모 백테스팅(A)** 은 “계산 병목”이 지배적이면 병렬 UI만으로는 이득이 제한적이다. citeturn12view0turn15view0turn17view0

### 11) Codex를 MCP 서버로 래핑하여 Brain(Claude)이 직접 태스크를 생성/조회 가능한가?

**기술적으로 가능하다. 단, “Codex Cloud 태스크를 원격 API로 생성/폴링”과 “로컬 Codex 실행을 MCP로 감싸기”는 다르다.**

**(1) Codex API/CLI 존재 여부**  
- CLI는 명확히 존재하며, `codex exec`가 자동화 진입점이다. JSONL 이벤트를 통해 실행 상태를 외부에서 추적할 수 있다. citeturn12view0  
- MCP 연동은 “Agents SDK가 Codex CLI를 MCP 서버로 호출”하는 공식 가이드가 존재한다. citeturn19search15  
- 반면 “Codex 전용 클라우드 태스크 생성 API 엔드포인트”는 공식 문서에서 직접 확인되지 않는다. 오히려 GPT‑5.3‑Codex 소개 글은 “Codex에서는 쓰이지만 API 접근은 곧 안전하게 enable 예정(safely enable API access soon)”이라고 하여, **2026‑02‑05 시점에는 API 접근이 ‘아직’**임을 시사한다. citeturn23view3

**(2) 존재한다면 어떤 엔드포인트로 태스크 생성/결과 폴링?**  
- “플랫폼 API 엔드포인트”로 Codex cloud task를 직접 생성하는 문서가 없으므로, 여기서는 단정할 수 없다. (문서 부재 → [추정] 금지, “미확인”으로 처리) citeturn23view3  
- 대신 “확실히 가능한” 폴링/조회는 다음 2가지다.  
  1) `codex exec --json` 이벤트 스트림 파싱(로컬/CI 실행): `turn.completed`/`turn.failed`를 트리거로 다음 단계 수행 citeturn12view0  
  2) GitHub에서 `@codex` 멘션으로 cloud task를 트리거하고 PR/리뷰 결과를 GitHub 이벤트로 받는 방식(다만 이는 “Codex API”가 아니라 “GitHub를 매개로 한 트리거”) citeturn16view0turn17view0

**(3) Woosdom 관점 구현 스케치(권장 아키텍처) [추정]**  
- Brain(Claude)이 “작업지시서(md)”를 작성  
- 오케스트레이터(간단히는 Python/Node)가  
  - (로컬 실행형) `codex exec --json` 실행 → 이벤트 수집 → 결과 파일(리포트/CSV) 저장 → Brain에게 요약 전달  
  - (혹은) Codex CLI를 MCP 서버로 띄워 Agents SDK가 tool-call로 `codex()` / `codex-reply()`를 호출  
- 계산이 매우 큰 Stage는 Modal/GitHub Actions로 분산 실행하고, Codex는 코드/검증/리포트 생성 담당 citeturn19search15turn12view0turn22search2turn22search0  

이렇게 하면 “사람이 Codex에 복사→다시 Brain에 전달”하는 릴레이를 줄이고, Brain이 “결과만” 보도록 만들 수 있다. 다만 이는 Woosdom 구현 설계이므로 [추정]이다.

아래는 이 섹션의 핵심 출처(URL)이다.
```text
https://developers.openai.com/codex/guides/agents-sdk/
https://developers.openai.com/codex/noninteractive
https://openai.com/index/introducing-gpt-5-3-codex/
https://developers.openai.com/codex/integrations/github
https://developers.openai.com/codex/cloud
```

### 12) Codex 없이도 같은 효과를 달성할 수 있는 대안적 워크플로우는?

가능하다. 특히 “대규모 계산”은 Codex 밖으로 빼는 게 오히려 정석일 수 있다.

- **(1) GitHub Actions로 Stage 병렬화(팬아웃) + 결과 아티팩트화**  
  GitHub Actions는 matrix job과 `max-parallel`로 동시 실행 잡 수를 제어할 수 있다. citeturn22search0turn22search4 이를 이용하면 (예: 상위 15,000 포트폴리오를 50분할) 병렬로 재평가/부트스트랩을 수행하고, 결과를 아티팩트로 모아 Brain이 요약하도록 만들 수 있다. (구현은 [추정], 기능은 문서 기반)

- **(2) GitHub Codespaces를 “공유 실행 환경”으로 사용**  
  Codespaces는 GitHub가 호스팅하는 개발 환경이며, 브라우저에서 코드 편집/실행이 가능하다고 문서화되어 있다. citeturn22search1turn22search29 다만 Codespaces는 “장시간 배치 계산(HPC)”보다는 “재현 가능한 개발/실험 환경” 쪽에 적합한 경우가 많다. (용도 판단은 [추정])

- **(3) Modal로 조합 탐색/부트스트랩을 대규모 병렬 실행**  
  Modal은 “배치 잡을 대규모 병렬로 스케일”한다고 소개하며, `.map()`으로 병렬 map을 제공한다. citeturn22search6turn22search2 특히 `spawn_map`은 “생성 즉시 반환(완료를 기다리지 않음)”을 제공하되 “결과의 programmatic retrieval은 향후 지원”이라고 명시돼 있어, 현재 단계에선 설계 주의가 필요하다. citeturn22search2

- **(4) Replicate 같은 비동기 API(웹훅) 기반 실행(ML 범주에 특히 적합)**  
  Replicate는 기본이 async이며 prediction ID를 바로 반환하고, 웹훅으로 생성/업데이트/완료 이벤트를 수신할 수 있다. citeturn22search3turn22search7 (다만 이는 “일반 Python 시뮬레이션”보다 모델 추론에 더 적합)

- **(5) Replit Workflows로 워크플로 병렬 실행**  
  Replit Workflows 문서는 “Parallel execution”이 태스크를 병렬로 시작하며 한 태스크 실패가 다른 태스크 중단으로 이어지지 않는다고 설명한다. citeturn10search10

- **(6) n8n/Make로 오케스트레이션**: 가능성은 높지만, 본 리서치 범위에서 1차 문서를 수집하지 못했으므로 구체 설계는 [추정].  

결론적으로, “Codex 멀티에이전트”는 강력하지만, **계산 집약 파트는 GitHub Actions/Modal로 분산하고, Codex는 코드/리포트/검증을 맡기는 혼합형이 가장 비용 효율적일 가능성**이 있다. citeturn22search0turn22search2turn12view0

아래는 이 섹션의 핵심 출처(URL)이다.
```text
https://docs.github.com/actions/writing-workflows/choosing-what-your-workflow-does/running-variations-of-jobs-in-a-workflow
https://modal.com/docs/reference/modal.Function
https://modal.com/docs/guide
https://docs.github.com/en/codespaces
https://replicate.com/docs/topics/predictions/create-a-prediction
https://replicate.com/docs/topics/webhooks
https://docs.replit.com/replit-workspace/workflows
```

## 의사결정 종합 판단과 6개월 전망

### 13) “Codex 멀티에이전트 기능에 시간을 투자해 워크플로우를 재설계할 가치가 있는가?”

**CONDITIONAL — (1) B·C 패턴(개발/데이터파이프라인)에선 ROI가 높을 가능성이 큼. (2) A 패턴(초대규모 계산)은 Codex 병렬만으로 병목이 안 풀릴 수 있어 ‘계산 분리’가 선행 조건. (3) 멀티에이전트는 실험적+버그/쿼터 리스크가 있어 ‘작게 도입→측정’이 필요.** citeturn13view0turn15view0turn19search20turn23view3

근거를 질문 흐름에 맞춰 압축하면 아래와 같다.

- **왜 YES가 아닌가?**  
  - 멀티에이전트 기능은 “실험적”이며, CLI에서만 가시화되고 다른 표면으로의 확대는 “coming soon”으로 남아 있다. 안정성을 전제로 한 전면 재설계는 리스크가 있다. citeturn13view0  
  - 병렬 실행이 쿼터/비용을 급격히 소모한다는 보고가 있어, ‘병렬=이득’이 자동 성립하지 않는다. citeturn19search20turn11search0turn11search10  
  - GPT‑5.3‑Codex 소개에서 “API access soon”이라고 밝힌 점은, “지금 당장 완전한 API 오케스트레이션 기반 재설계”가 아직 덜 성숙했음을 시사한다. citeturn23view3

- **그럼에도 CONDITIONAL로 긍정하는 이유**  
  - Codex는 이미 “병렬 태스크(Cloud) + 병렬 워크트리(App) + 멀티에이전트(CLI)”까지 제품 라인에서 공식화했다. Woosdom의 “비동기 실행 엔진” 역할과 정합성이 높다. citeturn17view0turn14view0turn13view0  
  - `codex exec --json` 이벤트 스트림과 `resume`, 그리고 Automations(인박스 큐)은 “수동 릴레이”를 구조적으로 줄이는 레일을 제공한다. citeturn12view0turn15view0  
  - MCP 서버로 Codex를 래핑하는 공식 가이드가 있어, Brain이 “직접 태스크 생성/조회”하는 자동화로 넘어갈 발판이 이미 있다. citeturn19search15

**YES가 되는 조건(구체)**  
- (조건 1) A 패턴(백테스트)은 **계산 실행면(Modal/GitHub Actions 등)을 분리**하고, Codex는 코드/검증/리포트에 집중시킨다. citeturn22search2turn22search0turn12view0  
- (조건 2) 멀티에이전트/병렬 태스크의 **사용량 소모/비용 계측**을 먼저 붙인다(Worktree 2~3개, 서브에이전트 2~4개 수준의 작은 실험). “동시 서브에이전트가 쿼터를 즉시 소모” 같은 리스크를 먼저 확인해야 한다. citeturn19search20turn11search0  
- (조건 3) 승인 정책/네트워크/시크릿 제거(setup-only) 제약을 고려해 **데이터 준비 단계를 재설계**한다. citeturn7view2turn20view0

**도입 우선순위(추천) [추정]**  
1) **패턴 B(MCP 도구 개발)**: codex exec를 CI에 붙여 “빌드/테스트 실패 자동 수정 초안” 루프부터 (ROI가 빠르게 계측 가능) citeturn12view0  
2) **패턴 C(데이터 수집/전처리)**: Automations로 “주기 수집 + 인박스 리포트” 만들고, Brain은 결과만 비교/판단 citeturn15view0  
3) **패턴 A(백테스트)**: Stage별 계산은 Actions/Modal로 분산 후, Codex가 파이프라인 코드·리포트 자동화 담당 citeturn22search0turn22search2

### 14) Codex vs Antigravity — “비동기 실행 엔진”을 하나로 통일해야 한다면?

**현 상태(이중 운용)가 합리적일 가능성이 높다 [추정].**  
다만 “비동기 실행 엔진 역할”만 놓고 하나로 통일해야 한다면, **Codex 쪽으로 수렴**하는 편이 구조적으로 유리할 가능성이 크다.

- Codex는 (1) cloud 병렬 백그라운드 작업, (2) app worktree 병렬, (3) CLI 비대화형/JSONL 이벤트, (4) GitHub 멘션 트리거, (5) MCP/Agents SDK 연동이라는 “자동화 레일”이 문서화되어 있다. citeturn17view0turn12view0turn16view0turn19search15turn14view0  
- Antigravity는 “여러 에이전트를 병렬로 관리”하는 IDE 컨셉은 강하지만, 본 질문(비동기 실행 엔진) 관점에서 “스크립트/이벤트 스트림/CI 연결” 같은 자동화 입출력 레일이 Codex 수준으로 문서화되어 있진 않다(이 리서치 범위 한정). citeturn9search5turn9news38

**통일 시 잃는 것(대표) [추정]**  
- Antigravity의 IDE 내 리서치/브라우징/아티팩트 기반 검증 UX를 잃을 수 있다(특히 “연구+분석” 체감). citeturn9news38  
- Codex는 워크트리/승인/샌드박스 정책에 따른 마찰(클릭/네트워크/시크릿 제거)이 여전히 존재하므로, Antigravity에서 더 매끄럽던 일부 상호작용이 거칠어질 수 있다. citeturn20view0turn20view1

따라서 결론은:  
- **“실행 엔진”만 통일**한다면 Codex.  
- **“리서치/상호작용 IDE”까지 포함해 통일**한다면, 지금 시점에선 이중 운용이 더 안전할 수 있음[추정]. (특히 Codex 멀티에이전트가 실험적이므로) citeturn13view0

### 15) 향후 6개월 내 Codex 로드맵/업데이트 예정에서 멀티에이전트 워크플로우에 영향 줄만한 것?

공식 문서/공식 블로그에서 “앞으로 바뀔 가능성이 큰 지점”은 크게 2개가 확인된다.

- **(1) 멀티에이전트 기능의 표면 확대**: 멀티에이전트는 현재 “CLI에서만 가시화”되고, “Codex app과 IDE Extension에서의 가시화는 coming soon”이라고 명시되어 있다. 6개월 내 가장 직접적인 UX 변화 후보로 볼 수 있다. citeturn13view0  
- **(2) Codex용 최신 모델 라인 고도화 + API 접근**: GPT‑5.3‑Codex는 2026‑02‑05 공개되었고 “25% 더 빠르다”고 주장한다. 또한 “API access를 곧 안전하게 enable”하겠다고 명시해, Woosdom 같은 외부 오케스트레이션과의 결합 가능성이 커질 수 있다(단, 일정은 불명확). citeturn23view3

추가로, GitHub 쪽에서도 Codex/Claude 같은 에이전트들을 한곳에서 관리하는 흐름(Agent HQ/통합)이 강화되고 있어, “GitHub 표면에서의 멀티에이전트 운용”이 더 촘촘해질 가능성이 있다. citeturn19news44

반면, “정확히 어떤 날짜에 어떤 기능이 GA”인지는 공식 로드맵 형태로 고정 공개된 문서가 확인되지 않아, 구체 일정 예측은 [추정]을 넘어설 수 없다.

아래는 이 섹션의 핵심 출처(URL)이다.
```text
https://developers.openai.com/codex/multi-agent/
https://openai.com/index/introducing-gpt-5-3-codex/
https://www.theverge.com/news/873665/github-claude-codex-ai-agents
```

## 전체 참고 링크 모음

(요청 사항에 따라 URL을 한 번에 모아 제공)
```text
# Codex (공식)
https://developers.openai.com/codex/cloud
https://developers.openai.com/codex/noninteractive
https://developers.openai.com/codex/multi-agent/
https://developers.openai.com/codex/security/
https://developers.openai.com/codex/app/worktrees
https://developers.openai.com/codex/app/automations
https://developers.openai.com/codex/cloud/environments
https://developers.openai.com/codex/integrations/github
https://developers.openai.com/codex/guides/agents-sdk/
https://developers.openai.com/codex/pricing/
https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan
https://help.openai.com/en/articles/12642688-using-credits-for-flexible-usage-in-chatgpt-freegopluspro-sora

# OpenAI (공식 발표)
https://openai.com/index/introducing-the-codex-app/
https://openai.com/index/introducing-gpt-5-3-codex/
https://openai.com/index/datadog/

# Codex (이슈/커뮤니티: “보고됨”)
https://github.com/openai/codex/issues/9607
https://github.com/openai/codex/issues/9298
https://github.com/openai/codex/issues/9748
https://github.com/openai/codex/issues/11181
https://community.openai.com/t/codex-vscode-extension-agent-full-access-always-asks-for-approval/1355908

# 대안 실행면 (병렬/비동기)
https://docs.github.com/actions/writing-workflows/choosing-what-your-workflow-does/running-variations-of-jobs-in-a-workflow
https://docs.github.com/en/codespaces
https://modal.com/docs/guide
https://modal.com/docs/reference/modal.Function
https://replicate.com/docs/topics/predictions/create-a-prediction
https://replicate.com/docs/topics/webhooks

# 경쟁 도구(대표 문서)
https://code.claude.com/docs/en/agent-teams
https://claude.com/pricing
https://cursor.com/changelog/2-0
https://cursor.com/docs/account/pricing
https://devin.ai/pricing/
https://docs.replit.com/replit-workspace/workflows
https://replit.com/pricing
https://antigravity.google/docs/agent-manager
```
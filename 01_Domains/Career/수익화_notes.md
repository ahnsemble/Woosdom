# Opus Handoff — GPT 앱 수익화 딥리서치 설계/검증 정리 (2026-02-12, KST)

## 0) 목적/상황
- 대상: **한국 거주 1인 개발자** (니치: **AEC(건축/설계)** + **직장인 생산성**)
- 목표: 2026년 기준 **GPT 앱(=Custom GPT + Wrapper SaaS) 수익화 전략** 수립
  - GPT Store 유효성 판정(수익 채널 vs 리드 채널)
  - 유닛 이코노믹스 기반 가격/쿼터 설계
  - 30일 실행 플랜(채널별 KPI/Cut-line 포함)

---

## 1) 핵심 결론(메타 전략)
- **GPT Store는 “직접 수익 채널”이 아니라 “리드 제너레이션 채널”로 보는 게 기본값.**
- 수익화는 **외부 Wrapper SaaS(웹/앱)**에서 **구독+크레딧(usage)** 형태로 통제하는 **하이브리드 래퍼 전략**이 최적.
- 2026년 경쟁력: 단순 요약/챗봇 래퍼가 아니라 **버티컬 워크플로우(Agentic) + 도메인 데이터 파이프라인**.

---

## 2) 딥리서치 최종 연구계획(사용자가 확정/승인한 버전)
(1) OpenAI 공식 문서와 커뮤니티를 조사하여 **‘GPT Store Builder Revenue Program’의 한국 지급 가능 여부, 산정 기준, 정산 주기**를 확인하고, 컷라인 조건(한국 불가, 기준 불명확 등)에 따라 GPT Store를 **‘리드 채널’ vs ‘수익 채널’**로 최종 판정한다. (**가능/불가/불확실 라벨링 및 공식 근거 링크 필수**)

(2) ‘AEC’ 및 ‘직장인 생산성’ 분야에서 **유료 플랜 운영 + 가격/지표 확인 가능한 성공 사례 10개**를 선정하여, **JTBD, 온보딩, 유통 채널, 과금 모델(구독/종량/좌석 등)**을 분석한다.

(3) 한국 1인 개발자가 이용 가능한 글로벌 결제 솔루션(LemonSqueezy, Paddle, Stripe Atlas)을 비교하되, **가입 조건, MoR(VAT 자동 처리), 환불 책임, 구독 관리 기능**을 중심으로 **‘한국 실사용 가능 여부’**를 검증한다.

(4) 대용량 컨텍스트(PDF/도면) 처리를 가정한 **OpenAI API + 인프라 비용**을 산출하여 **트래픽 3시나리오(Low/Med/High)별 마진과 손익분기 임계점**을 계산하고, 이를 바탕으로 **Free/Pro/Team 3티어 가격 및 쿼터 정책 최종안**을 도출한다.

(5) B2B/AEC 타겟팅 시 필요한 **데이터 보안(암호화, 학습 제외), 개인정보보호(GDPR/국내법), 프롬프트 인젝션 방어** 조치를 조사하여 **‘MVP 필수 10개’ / ‘추후 적용 10개’** 체크리스트를 작성한다.

(6) 초기 30일 매출을 위한 마케팅 실행 플랜을 수립하되, **런칭(디렉토리), SEO, B2B(아웃리치)** 채널별로 **주차별 가설/실행 과제/KPI/중단-피벗 기준(Cut-line)**을 포함한 구체적인 표를 작성한다.

---

## 3) “팩트체크 4종” 통합 프롬프트(사용자 요청으로 한방에 합친 버전 제공)
- Builder Program(한국 지급/조건/정산), ChatGPT Ads(플랜별), OpenAI API Pricing(공식표), Stripe Managed Payments(MoR) 한국 지원 여부
- 공통 규칙: 1차 출처 우선, 결론 라벨(확정/부정/불확실), 근거 링크≥2(공식≥1), 근거 문구 짧게 인용, 기준일 표기, 한국 명시 없으면 Unknown 처리

(※ 실제 대화에서는 이 프롬프트를 통합 형태로 제공했고, 사용자가 이를 기반으로 팩트체크 결과물을 작성해옴.)

---

## 4) 사용자 제출 “팩트체크 패키지(결과)” 핵심 내용
### (1) GPT Store Builder Revenue Program
- 결론: **한국 거주자 지급 대상 아님(현재), 미국 기반 일부 빌더 제한 파일럿** → GPT Store는 **리드 채널**로 확정
- 근거: OpenAI Help Center Monetizing GPT FAQ에 “US-based builders / not accepting additional builders” 문구
- 출처(사용자 기재):
  - https://help.openai.com/en/articles/9119255-monetizing-your-gpt-faq (업데이트: 2026-01 표기)
  - https://openai.com/index/introducing-the-gpt-store/

### (2) ChatGPT 광고
- 결론: **광고는 Free/Go에만**, Plus/Pro/Business/Enterprise/Edu는 광고 없음
- 출처(사용자 기재):
  - ZDNet 기사(2026-02-09)
  - OpenAI 공식 블로그(광고 관련) 링크

### (3) OpenAI API 가격표
- 사용자 표에 gpt-4o / gpt-4o-mini / o1 / o3-mini 단가를 기재했고,
- “고성능 추론 모델은 비싸서 무제한 구독은 적자 → 크레딧/종량 결합 필요” 결론을 냄.

### (4) MoR(Stripe Managed Payments / Lemon Squeezy)
- 결론: **한국 사업자 미지원** → MoR 필요 시 **Stripe Atlas로 미국 법인 설립**이 사실상 최단/유일 루트
- 출처(사용자 기재): Stripe docs supported business locations / Lemon Squeezy 업데이트 글

---

## 5) Sub-Brain 검토 및 “수정 요청/교정” 발생 지점
### 문제점: (3) 가격표는 반드시 “공식 pricing 페이지” 기준으로 통일 필요
- 사용자 결과물의 (3) 가격표는 “공식 문서와 숫자가 다를 가능성”이 있어,
  **유닛이코노믹스(마진/쿼터) 설계에 치명적** → “공식 pricing 표로 다시 기입” 지시.

### 문제점: (4) Stripe 문서 링크가 ‘구글 검색 링크’ 형태로 들어간 부분이 있어 근거 품질 약함
- Stripe docs 원문 링크로 교체 요청.

---

## 6) 교체본 제공(대화에서 Sub-Brain이 사용자에게 준 “붙여넣기용 수정본”)
### (3) 교체본(사용자 보고서에 그대로 교체하도록 제공)
- 핵심: **OpenAI Developer Docs 공식 Pricing 기준으로 표를 다시 작성**하라고 했고,
- gpt-4o / gpt-4o-mini / o1 / o3-mini 가격표를 “공식 pricing 링크”와 함께 제공함.
- 링크(대화에서 사용):
  - https://developers.openai.com/api/docs/pricing/
  - https://platform.openai.com/docs/guides/prompt-caching

> 주의: 실제 숫자는 “해당 공식 페이지의 현재 표”를 최종 기준으로 재확인 필요.

### (4) 링크 교체
- Stripe Managed Payments 근거 링크를 **Stripe docs 원문**으로 교체하라고 안내.
  - (대화에서는 docs.stripe.com managed-payments 관련 원문 링크로 교체 지시)

---

## 7) 사용자 감정/커뮤니케이션 이슈(중요)
- 사용자가 “수정사항은 한번에 말하라”고 반복 요청.
- 중간에 Sub-Brain이 소량 개선을 반복 제안하면서 사용자 불만이 커졌고,
- 최종적으로 사용자는 “그냥 실행한다”로 정리했고,
- 이후에는 “추가 수정 제안 없이 실행 지시문만” 제공하는 방식으로 대응.

---

## 8) 현재 상태 요약(오늘 기준)
- 연구계획: **확정**
- 팩트체크: 사용자 결과물 제출 완료
- 교정: (3) 가격표 “공식 pricing 기준 재기입” + (4) Stripe 근거 링크 원문 교체가 핵심 남은 작업
- 다음 액션(옵션):
  - 유닛이코노믹스 시트(3시나리오) 만들고, Free/Pro/Team 쿼터/크레딧 차감표 확정
  - AEC/생산성 사례 10개를 기준에 맞춰 실제로 선정해 표로 정리
  - 결제 스택: 한국 거주자 기준 MoR(Managed Payments) 불가 시 Atlas(미국 법인) vs Paddle 경로 비교 확정

---

## 9) Opus가 이어서 하면 좋은 “결정/출력”
1) **최종 가격/쿼터안(Free/Pro/Team)**: 
   - o1/o3 계열(고비용) 작업을 “크레딧 소모”로 분리
   - 헤비유저 적자 방지(임계점 기반 쿼터)
2) **AEC MVP 스코프(30일용)**:
   - 도면 멀티모달은 난이도가 높으니, 1차는 시방서/RFI/계약서 기반 RAG로 시작 후 확장
3) **GTM 30일 표**:
   - 런칭(디렉토리/PH), SEO(키워드 20개), B2B 아웃리치(리드 50/메시지 3종) + KPI/Cut-line

---

## 10) 링크 모음(핵심 근거)
- OpenAI Monetizing your GPT FAQ: https://help.openai.com/en/articles/9119255-monetizing-your-gpt-faq
- Introducing the GPT Store: https://openai.com/index/introducing-the-gpt-store/
- OpenAI API Pricing (공식): https://developers.openai.com/api/docs/pricing/
- Prompt caching guide: https://platform.openai.com/docs/guides/prompt-caching
- Stripe Managed Payments docs(원문): https://docs.stripe.com/payments/managed-payments
- (참고) Lemon Squeezy / Stripe 관련 공식 공지(사용자 결과물 포함)

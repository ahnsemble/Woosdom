# AEC FDE/SA 전환 역량 딥리서치 (2026-02 기준)

요청 저장 경로: `/01_Domains/Career/research/deepresearch_aec_fde_competency_2026.md`

## 요약 및 역할 정의

본 리포트는 “한국 건축사사무소 5년 경력(건축 전공, CS 정규 학위 없음) → AEC Forward Deployed Engineer(FDE) 또는 Solutions Architect(SA)” 전환을 목표로, **2025~2026 실제 채용 공고(10건 이상)**와 **AEC 소프트웨어/AI 시장 신호**를 교차 검증해 **필수 역량 지도(competency map)**와 **갭 분석 프레임워크**를 제시한다. citeturn15view4turn16view5turn16view0turn17view0turn15view7turn15view9turn15view8turn8search1turn8search25

FDE는 고객 현장(또는 고객 워크플로우) 내부에 “깊게” 들어가 **문제 구조화 → 프로토타입/제품급 코드 → 배포/운영까지**를 통해 고객의 성과를 만들어내는 “현장형 엔지니어”로 확산되고 있으며, 특히 대형 고객의 PoC를 생산 환경으로 밀어붙이는 역할로 정의되는 사례가 보고된다. citeturn11news41turn11search14turn11search18  
반면 SA/SE(솔루션 아키텍트/솔루션 엔지니어)는 대체로 **pre-sales + 설계/워크숍/데모 + 기술적 승리(technical win)**에 무게중심이 있으며, 회사/조직에 따라 “구현(implementation)”까지 포함하기도 한다(특히 엔터프라이즈 SaaS에서 통합/데이터 워크플로우까지). citeturn16view5turn16view0turn15view7turn16view3

한국에서도 “Forward Deployed Engineer”라는 직무명이 실제로 사용되고 있다. 예를 들어 채널톡은 FDE를 고객 가까이에서 AX(“AI Transformation”) 문제를 엔지니어링으로 풀고, 일회성 커스텀이 아니라 **현장 검증 해법을 제품팀이 가져갈 프로토타입으로 빠르게 만드는 팀**으로 설명한다. citeturn19search6turn19search0

## AEC FDE/SA 역량 지도

아래 역량 지도는 (a) AEC 도메인 강점을 “기술 제품화/배포 역량”으로 연결하는 데 초점을 두며, (b) 2025~2026 채용 공고에서 반복적으로 등장하는 키워드를 근거로 **필수 / 강력 권장 / 차별화 요소**를 분류한다. citeturn15view4turn17view3turn16view0turn17view0turn15view7turn15view9turn15view8turn10search4turn3search10

**프로그래밍 & 소프트웨어 개발**

| 역량(구체 기술/도구) | 중요도 | 채용 근거/해석 |
|---|---|---|
| Python(자동화/데이터/AI 파이프라인) | 필수 | AEC 소프트웨어 기업·플랫폼 조직에서 스크립팅/데이터/AI 파이프라인 요구가 반복된다(예: Nemetschek AI/ML 클라우드 배포·공용 컴포넌트 Python, Bentley의 agentic workflow/LLM 파이프라인, Bluebeam 데이터/백엔드). citeturn10search5turn3search10turn10search9turn10search0 |
| TypeScript/JavaScript(Node.js 포함) | 강력 권장 | AEC SaaS/디지털트윈/웹 제품에서 프론트·백엔드 경계의 실전 스택으로 반복 등장(예: Bentley TypeScript/Node/React, Doxel의 three.js 기반 3D 웹앱 언급). citeturn3search14turn15view8 |
| SQL(쿼리/Stored Procedure 이해 포함) | 필수 | “데이터 구성 최적화/워크플로우 최적화/통합” 역할에서 SQL 이해가 명시된다(예: Bentley SA가 SQL Stored Procedure·Query 최적화 요구). citeturn17view4 |
| C#/.NET(특히 AEC 레거시/윈도우 생태계) | 강력 권장 | AEC/BIM·엔터프라이즈 연동 영역에서 .NET 스택 수요가 관측된다(예: Bentley에서 C#/.NET·SQL·마이크로서비스). 또한 AEC 업계의 BIM 확장(플러그인)에서 .NET 계열 역량은 실무 적합성이 높다. citeturn2search2 |
| Go(고성능 백엔드/플랫폼) | 차별화 요소 | 일부 AEC 소프트웨어(예: Bluebeam)에서 Go 기반 백엔드·클라우드 서비스 개발이 명시된다. citeturn10search0turn10search1 |
| 테스트(유닛/통합/E2E), 코드리뷰, Git 기반 협업 | 필수 | “테스트 작성·코드리뷰·Git”은 제품 조직의 기본 요건으로 반복(예: Bentley에서 unit/integration test·Git·PR·Azure DevOps 언급). citeturn2search2turn3search14 |

**클라우드 & 인프라**

| 역량(구체 기술/도구) | 중요도 | 채용 근거/해석 |
|---|---|---|
| AWS | 강력 권장(일부는 필수) | AEC 소프트웨어 기업 백엔드/플랫폼에서 AWS가 직접 요구되거나(예: Bluebeam) “클라우드 네이티브 분산 환경” 경험이 핵심으로 제시된다. citeturn10search0turn10search1 |
| GCP(특히 Vertex AI, Cloud Run, GKE 등) | 차별화 요소(빠르게 상향 중) | Nemetschek AI Engineer 공고는 GCP 중심(VDP/Cloud Run/GKE/PubSub 등) 배포와 멀티클라우드 연계를 명시한다. citeturn10search5 |
| 컨테이너(Docker) & 오케스트레이션(Kubernetes/GKE) | 강력 권장 | AI/플랫폼 배포(특히 멀티클라우드)와 운영 역량으로 요구된다(Kubernetes 인지/이해가 자격요건에 포함되는 국내 FDE 사례도 존재). citeturn10search5turn20search30 |
| CI/CD(Jenkins/GitLab/Azure DevOps 등), 릴리스·버전 관리 | 필수 | 데이터/플랫폼 엔지니어 공고에서 CI/CD가 “Required Technical Skills”로 등장하며, 엔터프라이즈 운영에 필수 기반으로 제시된다. citeturn10search9turn2search2 |
| 데이터 웨어하우스/분석 스택(Snowflake, BigQuery, Redshift 등) | 강력 권장 | AEC SaaS에서도 데이터 파이프라인/아키텍처 역량 수요가 명시(예: Bluebeam Data Engineer). citeturn10search9 |
| 스트리밍/메시징(Kinesis, Pub/Sub 등) | 차별화 요소 | 대규모 현장 데이터(영상/이미지/IoT) 및 이벤트 기반 시스템에서 자주 쓰이며, 실제 공고에서 서비스 구성요소로 언급된다. citeturn10search0turn10search5turn15view8 |

**AI / ML / LLM**

| 역량(구체 기술/도구) | 중요도 | 채용 근거/해석 |
|---|---|---|
| “Agentic workflow/agent runtime” 설계·구현(프레임워크 포함) | 강력 권장 | Bentley는 “multi‑stage, agentic workflows”를 통한 현대화/자동화와 LLM 파이프라인을 명시하고, Nemetschek은 “agent runtime and store”를 공용 AI 플랫폼 역량으로 제시한다. citeturn3search10turn10search4 |
| RAG 파이프라인(도면/BIM 데이터 질의 포함) | 강력 권장 | Autodesk Platform Services + Bedrock 기반 “CAD/BIM-specific” 챗봇·agent-based architectures·RAG를 다루는 세션이 공식 행사(Autodesk University)에 등장하며, 설계 데이터 질의형 워크플로우가 산업 문제로 인식된다. citeturn5search2 |
| 평가/관측(LLM eval, 모니터링, 품질 게이트, observability) | 강력 권장 | Bentley와 Nemetschek 공고는 LLM 파이프라인의 “evaluation, monitoring” 및 품질/운영 표준(테스트·관측·릴리스)을 강조한다. citeturn3search10turn10search4 |
| 파인튜닝/서빙 기본기(특히 “현장 데이터로 성능 개선”) | 차별화 요소 | Nemetschek은 fine-tuning·evaluation pipeline을 공용 서비스 역량으로 포함하고, 국내 FDE 공고에서도 RAG·fine-tuning·agent 경험을 우대/요구한다. citeturn10search4turn20search30 |
| 컴퓨터 비전(Scan-to-BIM, 현장 영상 이해, 3D 재구성) | 차별화 요소(Contech에서 핵심) | Scan-to-BIM을 돕는 연구는 Revit API 수준의 편집 시퀀스를 예측하는 방식까지 제안되며, 대규모 포인트클라우드→BIM 변환의 “수작업 부담”을 전제로 한다. citeturn20academia39 Doxel은 CV/ML object detection·3D 웹앱·복잡한 데이터 파이프라인을 공개적으로 언급한다. citeturn15view8 Bentley도 3D 재구성/가우시안 스플래팅 등 고급 비전 역량을 채용한다. citeturn2search7turn2search5 |

**AEC 도메인 기술**

| 역량(구체 기술/도구) | 중요도 | 채용 근거/해석 |
|---|---|---|
| BIM 정보관리(ISO 19650/BS1192 수준의 “정보관리” 관점) | 필수(상위/글로벌) | Bentley SA 공고는 ISO19650/BS1192 이해를 자격요건에 명시한다. citeturn17view4 |
| 공통데이터환경(CDE)·플랫폼 정보관리 | 필수(특히 AEC SaaS/플랫폼) | Autodesk Korea Solutions Engineer 공고는 AEC 업계의 CDE 및 플랫폼 정보관리 기술을 “influencing and shaping” 경험으로 요구한다. citeturn6search2 |
| 건설관리 플랫폼 이해(Procore/ACC 등) + 통합 관점 | 강력 권장 | Procore(플랫폼 기반 커스텀 통합), Autodesk Construction Cloud(통합/ACC Connect), Clearstory·Doxel 공고에서 Procore/Autodesk Build 등 현장 시스템 친숙도를 직접 언급한다. citeturn16view0turn16view5turn15view9turn12search11 |
| 디지털 트윈/현장 데이터(영상·IoT·센서) | 차별화 요소 | Doxel은 영상/이미지/IoT 출력 등 현장 데이터 기반 워크플로우를 “대규모로 처리”하는 제품 개발을 설명하며, Bentley는 디지털 트윈 기술 친숙도를 언급한다. citeturn15view8turn17view4 |
| 규제/법규 자동화(인허가·사업성·코드체크) | 차별화 요소(한국에서 특히 강함) | 스페이스워크(랜드북)는 건축·도시 법규와 데이터를 결합해 토지 개발 시나리오/수익 등을 제공한다고 설명한다. citeturn18search15 |

**시스템 통합 & 엔터프라이즈**

| 역량(구체 기술/도구) | 중요도 | 채용 근거/해석 |
|---|---|---|
| REST API/웹훅/OAuth | 필수 | Autodesk 통합 솔루션 엔지니어 공고는 REST API, OAuth, webhooks, iPaaS 경험을 명시한다. citeturn17view3 |
| GraphQL/gRPC 등(특히 플랫폼/정체성/구독) | 차별화 요소 | Bluebeam Principal Backend 공고는 REST/GraphQL API 운영을 요구한다. citeturn10search1 |
| iPaaS(Workato, MuleSoft, Boomi, Zapier, Tray.io 등) | 강력 권장 | Autodesk 공고에서 iPaaS가 “Preferred Qualifications”로 직접 열거된다. citeturn17view3 |
| 데이터 파이프라인(ETL/ELT, 품질·프라이버시) | 강력 권장 | Bluebeam Data Engineer는 ETL/ELT·데이터 프라이버시/컴플라이언스 경험을 기술요건에 포함한다. citeturn10search9 |
| 엔터프라이즈 시스템 연동(SAP/SharePoint 등) | 차별화 요소 | Bentley는 iTwin과 외부 엔터프라이즈 시스템(SAP, Maximo, SharePoint 등) “제로코드 연결”을 목표로 하는 통합 엔진을 설명한다. citeturn2search2 |

**소프트 스킬 & 클라이언트 대면**

| 역량(구체 기술/도구) | 중요도 | 채용 근거/해석 |
|---|---|---|
| 워크숍/디스커버리/데모/프레젠테이션 | 필수 | OpenSpace·Clearstory는 discovery, 데모, RFP/RFI 응답 등을 핵심 업무로 명시한다. citeturn15view7turn15view9 Autodesk 통합 솔루션 엔지니어는 “technical win”과 세일즈 협업을 명시한다. citeturn16view5 |
| 문서화(Enablement 자료, playbook, 기술문서) | 강력 권장 | Autodesk는 파트너/고객 문서 유지, Clearstory는 템플릿·플레이북·문서를 반복 업무로 둔다. citeturn16view5turn15view9 |
| 이해관계자 관리(임원~현장) | 필수 | Clearstory는 “executive communication”, Doxel은 현장~VP까지 다양한 사용자 맥락을 언급한다. citeturn15view9turn15view8 |
| 영어 커뮤니케이션(글로벌) | 강력 권장 | 글로벌 AEC 소프트웨어 기업 공고는 영어 이력서 제출/영어 유창성/다국어 가점을 명시하는 경우가 있다. citeturn2search1turn16view3 |

image_group{"layout":"carousel","aspect_ratio":"16:9","query":["BIM digital twin construction visualization","construction management software dashboard","scan to BIM point cloud to building model","construction site AI computer vision monitoring"],"num_per_query":1}

## 채용 공고 기반 동향

### 표본 채용 공고

아래는 2025~2026 기간에 공개된(또는 해당 기간에 게시로 기록된) AEC FDE/SA/SE 및 인접 포지션 10건+ 표본이다. (Procore 커리어 페이지는 접근 제한이 있어, 동일 JD를 포함하는 외부 채용 보드/아카이브를 함께 활용했다.) citeturn16view0turn16view3turn15view4turn16view5turn17view0turn15view7turn15view9turn15view8turn12search11

| 기업 | 직무/레벨 | 지역/근무 형태 | 게시일(공개된 경우) | 핵심 요건(요약) | 연봉/보상(공개된 경우) | URL |
|---|---|---|---|---|---|---|
| Bentley | Solution Architect (ProjectWise Data Optimization) | 유럽(복수 국가) Home-Based/Hybrid | 2026-02-18 | 고객 워크플로우 최적화, 데이터 통합, PowerShell 스크립트, SQL SP/Query, ISO19650/BS1192, 디지털트윈 친숙도 | 미공개 | https://jobs.bentley.com/job/Remote-Solution-Architect/1365897100/ citeturn17view4 |
| Autodesk | Technical Solutions Engineer – Integrations | (채용 보드 기준) 인도(벵갈루루) | 미공개 | SaaS SE/구현 3+년, REST API, OAuth/webhooks, iPaaS(Workato/MuleSoft/Boomi/Zapier/Tray.io), ACC/통합, JS/Ruby/Python/Java/C++ 디버깅 보조 | 미공개 | https://group.themuse.com/jobs/autodesk/technical-solutions-engineer-integrations citeturn17view3 |
| Autodesk | Solution Engineer (Korea) | 대한민국(서울), 대면+출장 | 미공개 | AEC CDE/정보관리 영향력 경험, AEC 워크플로우 이해, 한국어+영어, 워크숍/현장방문, 출장 최대 30% | 미공개 | https://kr.linkedin.com/jobs/view/solution-engineer-at-autodesk-3862636295 citeturn6search2 |
| Procore | Senior Solutions Architect (Technical Services, Integrations) | 미국(리모트) | (보드 기록) 2024-11-05 제거 | “커스텀 통합 프로젝트”에서 통합 설계/개발, 스코핑, 테크 컨설팅, 워크플로우/클라이언트 관계 | Base $90,360–$124,245 | https://builtin.com/job/senior-solutions-architect/3023795 citeturn16view0 |
| Procore | Enterprise Solutions Engineer (UK) | 영국(런던), (보드 기준) | 미공개 | 엔터프라이즈 세일즈 엔지니어링, 발표/커뮤니케이션, 영어 필수+유럽 언어 가점 | Base £75,264–£103,488 / OTE £107,520–£147,840 | https://builtin.com/job/enterprise-solutions-engineer/8153074 citeturn17view2 |
| Procore | Solutions Engineer, Install Base, SMB | 미국(원격), SE(커미션)형 | 미공개 | (요약 노출 중심) Install base 대상 세일즈/기술 결합 역할 | 시급 Base $38–$52 + OTE $112k–$154k | https://startup.jobs/solutions-engineer-install-base-smb-procore-technologies-5545799 citeturn16view1 |
| Procore | Enterprise Solutions Engineer, Specialty Contractors | (미국 추정) | 미공개 | 엔터프라이즈 고객 대상, 커미션/OTE 구조 | 시급 Base $64–$88 + OTE $189k–$259,875 | https://www.wayup.com/i-Other-j-Enterprise-Solutions-Engineer-Specialty-Contractors-Procore-Technologies-326228186180582/ citeturn16view2 |
| Trimble | Solutions Architect Consultant (Construction, Viewpoint Vista) | 미국(덴버/포틀랜드), 출장 25% | (LinkedIn 기록) 5일 전 | Viewpoint Vista ERP 5+년 활용, 건설 컨설팅 10+년, 제품 SME/멘토링, 회계/PM 도메인 전문성 | Base $122,500–$168,400 | https://www.linkedin.com/jobs/view/solutions-architect-consultant-at-trimble-inc-4333069961 citeturn17view0 |
| entity["company","OpenSpace","construction reality capture saas"] | Solutions Engineer II | EMEA(하이브리드) | 2025-12-24 | 학사(건축/건설공학), 기술 세일즈/CS 6+년, 클라우드 SW 이해, 디스커버리/데모/RFP, 관계관리 | 미공개 | https://jobs.menlovc.com/companies/openspace/jobs/64118329-solutions-engineer-uki-nordics citeturn15view7 |
| entity["company","Clearstory","construction change order saas"] | Solutions Engineer | 원격(유연) | 미공개 | 시공/원가관리 3–5년 + 건설 SaaS SE/구현 2+년, API/데이터플로우/아키텍처 대화 가능, Procore/Autodesk Build/Sage 가점 | 미공개(“Series B market-rate”) | https://jobs.prudence.vc/companies/clearstory/jobs/62822446-solutions-engineer citeturn15view9 |
| entity["company","Doxel","construction progress tracking ai"] | Senior Solutions Engineer | 미국(오스틴), Hybrid | 미공개 | CV/ML+3D 웹앱+데이터 파이프라인 기반 제품, 대규모 현장 데이터(영상/이미지/IoT) 워크플로우, 0→1 프로젝트/기술 리드 | 미공개 | https://startup.jobs/senior-solutions-engineer-doxel-7561870 citeturn15view8 |
| Doxel | Construction Analytics Solutions Engineer | 미국(오스틴) | 2025-06-09 | (Preferred에) Procore/Aconex/Autodesk Build 친숙도, 건설 프로젝트 도메인 | 미공개 | https://jobs.insightpartners.com/companies/doxel-2-8fb6ad5f-0382-4d0d-b4d7-4338c9597d7d/jobs/52262890-construction-analytics-solutions-engineer citeturn12search11 |

### 공통 “필수 요건” 패턴

표본에서 반복되는 공통분모는 “건설/AEC 도메인 이해”만이 아니라, **통합·데이터·워크플로우를 실제로 굴리는(그리고 설명하는) 능력**이다. Autodesk 통합 공고가 REST/OAuth/webhooks/iPaaS를 직접 요구하고, Bentley SA 공고가 SQL·PowerShell·정보관리 표준(ISO19650)을 함께 요구하는 점은 “AEC SA/FDE = AEC 도메인 + 엔터프라이즈 데이터/통합 + 고객 대면”의 결합 직무임을 잘 보여준다. citeturn17view3turn17view4  
Contech/AI 스타트업(예: Doxel, Clearstory)은 “현장 데이터(비정형) → 제품 워크플로우(정형) → 고객 가치”를 연결하는 역량을 강조하며, 단순 모델링 역량보다 **데이터 흐름/시스템 아키텍처 대화 능력**을 명시한다. citeturn15view8turn15view9

### 연차별 기대치(현실적 구분)

- Junior~Mid 구간은 “기술 세일즈/CS”라 해도, 최소 요건으로 **SaaS 환경에서의 구현(implementation)·문제 해결·커뮤니케이션**이 명시되는 경향이 있다(Autodesk 통합 공고의 “3+ years” 등). citeturn17view3  
- Mid~Senior 구간은 **고객 관계를 유지하면서 표준화/확장 가능한 해법을 설계하는 역량**(예: Bentley의 “표준화·커스터마이징 최소화·워크플로우 최적화”, OpenSpace의 “복합 세일즈 사이클·온보딩 총괄”)이 핵심으로 이동한다. citeturn17view4turn15view7  
- Senior 이상에서는 도메인 SME(예: Trimble Viewpoint/Vista ERP) + 멘토링/에스컬레이션 처리 + 조직 내 enablement가 결합되는 형태가 뚜렷하다. citeturn17view0

### 연봉 범위(미국/한국/원격)

미국/영국 등은 역할에 따라 **기본급 + 커미션/OTE + 주식(Equity)** 구조가 흔하며, 구체적인 pay range를 명시하는 사례도 다수다(예: Procore SE/SA, Trimble SA). citeturn16view0turn16view1turn16view2turn17view0turn16view3  
또한 동일 회사라도 지역/경력/역량에 따라 실제 보상이 달라질 수 있음을 공고 본문에 명시하는 경우가 많다. citeturn16view0turn16view3

- 미국(예시): Procore Senior Solutions Architect 기본급 $90,360–$124,245(원격). citeturn16view0  
- 미국(예시): Procore Solutions Engineer(Install Base, SMB) 시급 $38–$52 + OTE $112k–$154k. citeturn16view1  
- 미국(예시): Trimble Solutions Architect Base $122,500–$168,400. citeturn17view0  
- 영국(예시): Procore Enterprise Solutions Engineer 기본급 £75,264–£103,488, OTE £107,520–£147,840. citeturn16view3  
- 한국(공시형 예시): 한국딥러닝의 FDE 공고(잡코리아 표기)는 연봉 4,000~7,001만원 범위를 노출한다(단, AEC 전용 직무라기보다 AI 산업 전반의 FDE 사례). citeturn19search2

보조 지표로, Glassdoor는 Procore/Autodesk “Solutions Engineer” 직군의 추정 연간 보상 범위를 제시한다(표본 수가 적을 수 있으므로 참고값으로만 사용). citeturn14search0turn14search2

## 전환 사례 및 포트폴리오 시사점

“건축 배경 → 테크 전환”은 희귀 경로가 아니며, 특히 **‘도메인이 강한 소프트웨어 엔지니어’**로 포지셔닝할 때 설득력이 높아진다. 예로 주거 건설 기술 회사 entity["company","Higharc","homebuilding design software"]는 “LEED/면허 보유 건축가 출신이 Senior Software Engineer로 전환”한 사례를 팀 프로필로 공개한다. citeturn20search19  
또 다른 “건축가→개발자” 전환 인터뷰는 전환의 동기(문제 해결 방식 선호), 학습 방식(자기주도), 그리고 초기 진입 포지션(프론트엔드/웹 등)이 현실적 경로임을 보여준다. citeturn20search0  
건축 전공 후 IT 커리어로 옮긴 개인 회고 역시 “학위보다도 학습·프로젝트 기반 증명”이 핵심이라는 관찰을 제공한다. citeturn20search16

이 사례들을 AEC FDE/SA로 변환하면 포트폴리오의 결론은 단순하다. **(1) 도메인 문제를 정확히 정의하고 (2) 코드로 해결하며 (3) 배포/운영·고객 사용 장면까지 포함**해야 한다. 이는 OpenSpace/Autodesk/Procore/Clearstory 공고에서 “워크숍·데모·문서·온보딩·통합”을 반복 요구하는 이유와 맞물린다. citeturn15view7turn17view3turn16view0turn15view9

## 한국 시장 및 원격 전략

한국에서는 “FDE”라는 용어 자체가 이미 채용에서 사용되며, 고객 가까이에서 문제를 보고 “스케일러블 프로토타입”을 만든다는 정의가 명시적으로 등장한다(채널톡). citeturn19search6turn19search0 이는 “한국에 FDE 개념이 없다”기보다는, **AEC가 아닌 영역에서 먼저 확산**된 뒤 도메인 버티컬로 이식되는 양상에 가깝다. citeturn19search14turn11news41  
따라서 한국에서 AEC FDE/SA에 준하는 유사 직무명을 찾을 때는 “FDE” 외에도 **Solution Engineer(기술영업), Professional Services/Implementation, Technical Account, Presales Consultant** 계열 키워드로 탐색하는 것이 현실적이다. citeturn17view3turn15view7turn15view9

한국 proptech/contech 신호로는, 스페이스워크가 “인공지능·데이터 기술로 토지 개발 시나리오 구현”을 표방하고(자사 소개), 랜드북 서비스가 건축·도시 법규와 데이터를 결합해 개발 가치/설계/수익을 추정한다고 설명하는 점이 확인된다. citeturn18search3turn18search15 직방은 AI 기반 서비스 고도화(“AI 중개사”)와 데이터 통합 분석을 언급하며, 부동산 플랫폼이 AI 의사결정 인프라로 확장하려는 목표를 제시한다. citeturn18search9

해외 원격 지원의 현실은 “완전 원격”이라도 **국가/권역 제한**이 붙는 경우가 많다(예: Bentley SA는 유럽 특정 국가 거주를 전제로 Home-Based/Hybrid). citeturn15view4 따라서 한국 거주 상태에서 해외 AEC 소프트웨어 기업을 노릴 때는 (a) 한국 지사 채용(예: Autodesk Korea), (b) APAC 범위 원격/계약, (c) 글로벌 기업의 한국 파트너/리셀러/컨설팅 채널을 통한 진입을 함께 고려하는 편이 안전하다. citeturn6search2turn15view4

## 갭 분석 프레임워크와 18개월 실행 로드맵

### 갭 매트릭스

아래는 “현재 제공된 배경”을 토대로 한 **추정** 수준(면담/포트폴리오 검토 시 보정 필요)이며, 목표 수준은 채용 공고에서 반복되는 “실제 수행 가능 상태”를 기준으로 한다. citeturn17view3turn17view4turn15view7turn15view9turn16view0turn15view8turn10search4turn3search10

척도: 현재/목표 = 0(경험 없음)~4(실무 리드 가능). 시간은 “집중 학습+프로젝트 적용” 기준의 **범위 추정**(개인 상황에 따라 변동).

| 역량 클러스터 | 현재(추정) | 목표 | 갭 | 난이도 | 예상 소요(범위) | 근거(목표 정의) |
|---|---:|---:|---:|---|---|---|
| AEC 도메인(BIM 실무/워크플로우) | 4 | 4 | 0 | 중 | 유지 | AEC SA/SE는 CDE/정보관리/프로세스 이해를 전제로 요구. citeturn6search2turn17view4 |
| API/통합(REST, OAuth, webhooks, iPaaS) | 2 | 4 | 2 | 중~상 | 8~16주 | Autodesk 통합 공고가 핵심 자격으로 명시. citeturn17view3 |
| 데이터(SQL, ETL/ELT, 품질, 프라이버시) | 2 | 3~4 | 1~2 | 중 | 6~14주 | Bentley SA(SQL SP), Bluebeam Data Engineer(ETL/프라이버시) 등. citeturn17view4turn10search9 |
| 제품형 웹 개발(TypeScript/Node/React, 3D web) | 1~2 | 3 | 1~2 | 중 | 8~20주 | Bentley TypeScript/React, Doxel 3D 웹앱(three.js) 언급. citeturn3search14turn15view8 |
| 클라우드/배포(Docker/K8s, CI/CD, 운영) | 1 | 3 | 2 | 상 | 10~24주 | Nemetschek AI Engineer(GCP+GKE), Bluebeam(클라우드 서비스/CI/CD), 국내 FDE의 K8s 인지. citeturn10search5turn10search9turn20search30 |
| LLM/에이전트(오케스트레이션, eval/monitoring) | 3 | 4 | 1 | 중 | 6~12주 | Bentley/Nemetschek이 “agentic workflow + evaluation/monitoring”을 명시. citeturn3search10turn10search4 |
| 고객 대면(워크숍/데모/문서/내부 enablement) | 2~3 | 4 | 1~2 | 중 | 8~20주(반복 훈련) | OpenSpace·Clearstory·Autodesk 공고에 반복 등장. citeturn15view7turn15view9turn16view5 |
| 영어(문서·회의·이력서) | 2(가정) | 3~4 | 1~2 | 중 | 12~24주(루틴) | 글로벌 공고에서 영어/다국어 요건을 명시한다. citeturn16view3turn2search1 |

### 우선순위 매트릭스

임팩트(채용 가능성 상승) × 학습 가능성(18개월 내 달성) 기준으로 정렬하면, ROI 상위는 아래 순서로 수렴한다. 이 우선순위는 “AEC 도메인 강점을 활용해 통합/데이터 문제를 해결”하는 공고 패턴에 맞춘 것이다. citeturn17view3turn16view0turn15view9turn17view4turn15view7

1) **API/통합 + 고객 대면 패키지(워크숍→데모→문서→온보딩)**: Autodesk/OpenSpace/Clearstory가 직무 중심축으로 요구. citeturn17view3turn15view7turn15view9  
2) **SQL/데이터 워크플로우(ETL/품질) + AEC 정보관리(ISO19650/CDE)**: Bentley SA의 결합 요구가 상징적. citeturn17view4  
3) **클라우드/배포(컨테이너·CI/CD·관측)**: AI/통합을 “제품/운영”으로 마감하기 위한 필수 바닥. citeturn10search5turn10search4turn3search10  
4) **TypeScript/React 기반 제품형 구현(특히 ‘데모를 넘어 프로덕션 품질’)**: Doxel처럼 3D/현장 데이터 UI가 강한 영역에서 차별화. citeturn15view8

### 6·12·18개월 마일스톤(현실형)

**6개월:** “AEC 통합·데이터·LLM”을 하나의 데모로 묶어, SA/SE 인터뷰에서 요구되는 워크숍·데모·문서를 세트로 보여줄 수준을 만든다. (Autodesk/OpenSpace/Clearstory 패턴). citeturn17view3turn15view7turn15view9  
- 산출물: 고객 페르소나/문제정의 문서(1p), 데모 영상(5~8분), 기술 아키텍처 다이어그램, API 문서(간단 OpenAPI), 운영 체크리스트(로그/모니터링 포함).

**12개월:** “배포/운영”을 강화해 FDE 성격을 만든다. 즉, 고객 환경에 설치(또는 SaaS 형태)하고, 데이터 품질/보안/관측으로 운영 가능성을 입증한다. citeturn10search5turn10search4turn17view4  
- 산출물: Docker/K8s 배포 스크립트, CI/CD 파이프라인, eval/모니터링 대시보드(간이), 장애 시나리오 대응 문서.

**18개월:** “엔터프라이즈 통합 + 표준화” 버전으로 확장한다. Bentley/Trimble 계열이 요구하는 표준화·커스터마이징 최소화·에스컬레이션 대응 관점까지 포함한다. citeturn17view4turn17view0  
- 산출물: 다중 프로젝트/테넌트, 권한/감사로그, 데이터 마이그레이션 플레이북, 파트너/리셀러 enablement 문서.

### 포트폴리오 프로젝트 제안

아래 프로젝트는 “건축 배경”이 직접적인 차별점이 되도록 설계했으며, 동시에 채용 공고가 요구하는 통합·워크플로우·고객 대면 산출물까지 포함하도록 스코프를 구체화했다. citeturn16view0turn17view3turn17view4turn15view7turn15view9turn15view8turn3search10turn10search4

**프로젝트 A: BIM/CDE “질의형 업무” RAG 데모 (설계·시공 협업용)**  
- 목표: “도면/모델 기반 질의”를 실제 협업 질문(RFI/설계변경/면적·수량)으로 변환하는 챗 인터페이스. Autodesk University에서 CAD/BIM 데이터 챗봇·RAG·agent 기반 아키텍처가 다뤄지는 만큼, ‘설계 데이터 질의’는 산업적 맥락이 있다. citeturn5search2  
- 스코프: (1) Revit/IFC에서 속성·공간·객체 메타데이터 추출(Python), (2) SQL 저장(Postgres) + 임베딩 인덱스, (3) RAG + “행동(액션)”(예: 이슈 생성/태그/리포트) 에이전트, (4) 평가셋(20~50문항)과 hallucination 방지 규칙, (5) 데모 영상 + 워크숍 진행안.

**프로젝트 B: AEC SaaS 통합(ACC/Procore 유사) “Change Order/RFI” 워크플로우 자동화**  
- 목표: Clearstory가 변화오더(change order) 프로세스 자동화를 제품 가치로 설명하고, Autodesk 통합 공고가 iPaaS·API 통합을 핵심으로 보며, Procore가 커스텀 통합 프로젝트를 SA 역할로 둔 점을 한 번에 겨냥한다. citeturn15view9turn17view3turn16view0  
- 스코프: (1) REST API + OAuth + webhooks 기반 이벤트 수집, (2) ETL로 데이터 정규화, (3) 승인/비용/일정 영향 요약(LLM) + 근거 링크, (4) 운영 로그·재처리(replay) 메커니즘, (5) 고객용 운영/설치 문서.

**프로젝트 C: “ISO 19650 스타일” 정보관리 품질 점검기 + 표준화 리포트**  
- 목표: Bentley SA가 ISO19650/BS1192 이해를 명시하고 “표준화/커스터마이징 최소화”를 강조하는 흐름을 직접 겨냥한다. citeturn17view4  
- 스코프: (1) 프로젝트 정보구조 검사(폴더/파일 네이밍, 메타데이터 필수항목), (2) 결함 리포트 생성, (3) PowerShell/파이썬 스크립트로 고객 환경 적용(샘플), (4) ‘표준화 이행’ 성과 대시보드(전/후 비교).

**프로젝트 D: 현장 영상/IoT 데이터 기반 “진도/리스크” 대시보드(축소판)**  
- 목표: Doxel이 강조하는 “현장 비정형 데이터→의사결정 워크플로우” 전환을 축소판으로 구현(영상/이미지/IoT). citeturn15view8  
- 스코프: (1) 영상 프레임/이미지 수집, (2) 간단한 객체/상태 추정, (3) 3D/2D 뷰어(three.js 등)에서 이슈 표시, (4) 리스크 요약/에스컬레이션 룰. (Scan-to-BIM 연구 맥락을 “도면-현장 정합” 문제로 연결 가능). citeturn20academia39turn15view8

### Pre‑Mortem: 18개월 후 실패했을 때 가장 가능성 높은 원인

1) **“프로토타입은 있으나, 운영·표준화·보안”이 비어 있어 엔터프라이즈 신뢰를 못 얻음**: 공고들은 단순 데모가 아니라 통합/운영(스크립트, SQL, 배포, 보안/컴플라이언스)을 반복 요구한다. citeturn17view4turn10search4turn10search9turn17view3  
2) **“AEC 도메인 강점”이 ‘제품 가치’로 번역되지 않음(고객 대면 산출물 부족)**: OpenSpace/Clearstory/Autodesk는 디스커버리·데모·문서·온보딩을 핵심 업무로 둔다. 이 묶음을 포트폴리오로 제시하지 못하면 “좋은 엔지니어”여도 SA/FDE로는 약해진다. citeturn15view7turn15view9turn16view5  
3) **타깃 직무 정의가 흔들림(FDE vs SA vs SWE) → 학습/포트폴리오가 분산됨**: FDE는 “현장 문제를 제품급 코드로 마감”하는 역할로 설명되며, SA는 설계/프리세일즈 중심인 경우가 많다. 목표 직무를 한 문장으로 못 고정하면 18개월이 쉽게 분산된다. citeturn11news41turn11search14turn16view0turn15view7
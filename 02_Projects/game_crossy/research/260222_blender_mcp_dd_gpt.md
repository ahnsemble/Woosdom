# Blender MCP + Roblox 3D 에셋 파이프라인 시장조사 DD

## 요약
Project Crossy의 “Godot → Roblox 직행”은 **기술적 파이프라인 관점에선 충분히 현실적**이다. Roblox Studio의 3D Importer는 `.fbx`/`.gltf`/`.obj`를 지원하며, FBX·glTF는 **PBR 텍스처, 리깅/스키닝, 애니메이션, 버텍스 컬러**까지 폭넓게 가져올 수 있다. citeturn14view2turn9view3 또한 Studio 자체에서 **glTF Export(베타 스펙/제약 포함)**가 제공되기 시작해(2025년 공지), 외부 DCC(Blender 등)와 왕복 워크플로우도 점점 강화되는 추세다. citeturn9view4turn15view1

다만 “Blender MCP 기반 **프롬프트만으로 로우폴리 게임 에셋을 대량 생산**”을 핵심 가정으로 두면 리스크가 크다. MCP 자체는 **LLM이 Blender를 조작**하게 해주는 “접착제/오케스트레이션”에 가깝고, 실제 메시 품질은 (a) 파라메트릭/프로시저럴 모델링 역량, (b) 외부 텍스트→3D/이미지→3D 생성기의 성능과 (c) 리토폴로지·UV·피벗·LOD 등 “게임 제작 마감 작업”에 달려 있다. citeturn7view2turn7view3turn14view0

Roblox 측면에서 가장 중요한 하드 리미트는 **개별 메시 20,000 triangles 상한**이며, 이를 넘으면 importer가 자동 단순화를 시도하거나(품질 편차 존재) 메시를 분할해야 한다. citeturn14view0turn9view4turn11search22 텍스처는 “파일 업로드/작업” 관점에선 4K(4096²)까지 언급되지만, UV/컴포지터·예산·디바이스별 다운샘플링 등 실전 제약이 있어 **1024² 중심의 예산 설계가 안전**하다. citeturn14view3

결론적으로, **엔진 피벗(→Roblox)은 Go 쪽으로 기운다**. 다만 Blender MCP는 “필수 생산 라인”이 아니라 **(1) 회색박스→콘텐츠 치환 속도를 높이는 도구** 또는 **(2) 에셋 조립·정리·배치 자동화 레이어**로 두는 것이 합리적이다. 근거는 (a) Roblox의 3D import/자동화 수단이 이미 꽤 성숙했고 citeturn14view2turn15view2turn15view0 (b) MCP 생태계는 급성장 중이지만 유지보수 편차가 크며 citeturn2view0turn5view1turn2view4turn5view5 (c) 현 세대 AI 3D 생성은 “로우폴리+일관된 스타일+게임레디”를 무인으로 보장하기 어렵기 때문이다(도구별로 Smart Low-Poly/리토폴로지 기능을 내세우지만 결과 편차는 여전히 남는다). citeturn27view0turn27view2turn27view1

## Blender MCP 현황
“Blender MCP”는 2025~2026에 걸쳐 빠르게 확산된 키워드로 보이며, **(1) Blender를 MCP 서버/애드온으로 노출**해 LLM이 씬을 제어하고, **(2) 외부 3D 생성/자산 검색을 엮어** “텍스트/이미지 지시 → Blender에서 실행” 흐름을 만드는 프로젝트들이 다수다. citeturn8view2turn7view3turn0search5

### GitHub 주요 프로젝트 요약 (3~5개)
아래는 entity["company","GitHub","code hosting platform"]에서 “blender mcp”로 발견되는 대표 구현들 중, 스타/커밋 최신성 기준으로 실무 검토 가치가 높은 편에 속하는 것들이다(2026-02-22 KST 기준 스냅샷).

- **ahujasid/blender-mcp**  
  스타 약 **17.2k**, 이슈 25, PR 18로 커뮤니티 사용량이 압도적으로 크다. citeturn2view0 커밋 최신 날짜가 **2026-01-23**로 2026년에도 활발히 움직인 정황이 있다. citeturn5view1 기능적으로 “Blender ↔ Claude” 통합을 표방하며, Hunyuan3D, Sketchfab 검색, Poly Haven 자산, Hyper3D Rodin 지원 등을 명시한다. citeturn7view3turn7view2  
- **VxASI/blender-mcp-vxai**  
  스타 약 **290**, 커밋 최신 날짜 **2025-03-19**로(활성은 있으나 최근성은 다소 떨어짐) 릴리스 기반 운영을 한다. citeturn2view1turn5view4  
- **CommonSenseMachines/blender-mcp**  
  스타 약 **120**, 커밋 최신 날짜 **2025-04-25**. citeturn2view2turn5view2 entity["company","CSM.ai","3d ai asset platform"] 세션(공개/비공개) 검색을 통한 3D 모델 검색/가져오기, Mixamo 파일 기반 애니메이션 적용 워크플로우 등을 특징으로 내세운다. citeturn8view1turn8view2  
- **dhakalnirajan/blender-open-mcp**  
  스타 약 **70**, 커밋 최신 날짜 **2025-03-24**. citeturn2view3turn5view3 로컬 LLM(예: Ollama)과의 연결, Poly Haven 연동 등을 강조한다. citeturn0search14  
- **poly-mcp/Blender-MCP-Server**  
  스타 약 **19**로 작지만, “50+ 도구” 등 명시적으로 범용 MCP 서버를 지향한다. citeturn2view4turn0search5 커밋 최신 날짜 **2025-11-13**으로 2025년 말까지는 움직임이 확인된다. citeturn5view5

### MCP 기반 “AI 자동 모델링”의 실제 능력과 한계
Blender MCP 류가 잘하는 것은 대체로 **‘모델 생성 그 자체’**라기보다, “(A) Blender 조작 자동화” + “(B) 생성형 3D/자산 라이브러리 호출” + “(C) 씬 편집/배치”다. 예를 들어 ahujasid/blender-mcp는 “로우폴리 던전 씬을 만들고 20개 이상 자산을 채운다” 같은 지시 예시를 제시하지만, 실제로는 **외부 자산 검색(예: Sketchfab/Poly Haven) 및 외부 3D 생성기(예: Hyper3D Rodin, Hunyuan3D)**를 엮어 목표를 달성하는 구조다. citeturn7view2turn7view3

따라서 “프롬프트로 로우폴리 게임 에셋 생성”의 수준 평가는 다음처럼 분해하는 것이 정확하다.

**프롬프트만으로 ‘완전 신규’ 로우폴리 프롭을 즉시 게임레디로 뽑는가?**  
- 가능 범위는 분명히 있다. 예컨대 Tripo는 유료 티어에서 **Smart Low Poly**, 파트 세그멘테이션, 스켈레톤 포함 익스포트 등을 기능으로 내건다. citeturn27view0 Hyper3D(Rodin)는 플랜 스펙상 “폴리 카운트 옵션/리두(redo)·4K 텍스처(상위 플랜)” 등을 제공한다. citeturn27view1  
- 하지만 “Roblox 친화적 로우폴리”는 단순히 폴리 수만 낮추는 문제가 아니라, **피벗/스케일(Studs), 콜리전, 메시 분할(20k tri), UV/텍스처 예산, 일관된 스타일(카툰/심플), 반복 제작 시 변동성 관리**가 핵심이다. Roblox는 개별 메시 20,000 triangles 상한을 명시한다. citeturn14view0 즉, 생성 결과가 아무리 ‘그럴듯’해도 이 제약을 자동으로 지켜주지 않으면(또는 자동 단순화 품질이 불안정하면) 실무는 다시 수작업으로 끌려간다. citeturn9view4turn11search22

**현실적 결론**  
- Blender MCP는 “프롬프트 기반 3D 제작”의 완성형이라기보다, **1인 개발자가 반복 작업(배치, 이름 정리, 머티리얼 적용, 익스포트 등)을 줄이는 ‘오케스트레이터’**로서 가치가 가장 크다. citeturn14view2turn7view3  
- “로우폴리 에셋 대량 생성”은 MCP 단독보다는 **Tripo/Hyper3D/Meshy/Stable Fast 3D 같은 전용 생성기 + Blender에서 최소 정리 + Roblox Import 규격 준수** 조합이 더 현실적이다. citeturn27view0turn27view1turn27view2turn25search14turn14view0  

## Roblox 3D 에셋 파이프라인
Roblox로 직행할 때 가장 중요한 것은 “Roblox가 받아주는 형태로 메시·텍스처·애니메이션을 **규격화**하는 일”이다. Roblox 공식 Creator Docs 기준으로 Studio의 3D Importer는 `.fbx`, `.gltf`, `.obj`를 지원한다. citeturn14view2turn14view1 또한 glTF 지원은 2023년 “정식 릴리스” 공지를 통해, **텍스처·리깅·스키닝·애니메이션**까지 포함한다고 명시됐다. citeturn9view3

### Blender → Studio Import 포맷 선택
Creator Docs의 파일 타입 가이드는 꽤 명확하다. citeturn14view2  
- **OBJ**: “기본 단일 메시 오브젝트” 중심(간단 지오메트리). citeturn14view2  
- **FBX**: 멀티 메시/계층, 텍스처(기본/PBR), 리깅/애니메이션, 버텍스 컬러 등 “거의 모든 것”에 적합. citeturn14view2  
- **glTF**: FBX와 유사하게 멀티 메시/계층, PBR 텍스처, 리깅/애니메이션, 버텍스 컬러 등을 지원하며(Importer 측), “텍스처 경로 문제/전달 편의성” 측면에서 `.glb`(단일 바이너리 패키징)의 이점이 자주 언급된다. citeturn9view3turn15view0

실무적으로는, **정적 프롭/환경물은 glTF(.glb)로 묶어 전달**, 캐릭터/애니메이션 등은 FBX로 가져가는 스튜디오가 많다(다만 Roblox Importer는 glTF 애니메이션도 지원한다고 공지된 바 있어, 팀 선호도·툴체인에 따라 달라질 수 있다). citeturn9view3turn14view2

### MeshPart(메시) 예산·리미트
Roblox의 일반 모델링 스펙은 **개별 메시가 20,000 triangles를 초과할 수 없다**고 명시한다. citeturn14view0 20k 초과 시 Importer가 자동 단순화를 수행할 수 있고, 2025년 “Asset Workflows Recap”에서 Roblox는 **20k 초과 메시 자동 단순화 엔진을 새 것으로 교체해 품질이 크게 개선**됐다고 밝힌다. citeturn9view4 그래도 결과가 불만족스러우면 메시를 나눠 임포트하는 우회가 권장되며, DevForum 스레드에서는 “모델 전체 폴리곤 합계 제한이 아니라 ‘개별 메시’ 제한”이라는 형태의 안내가 반복된다. citeturn11search22turn14view0

### 텍스처·PBR·SurfaceAppearance 제약
Roblox는 기본 텍스처와 PBR 텍스처를 지원하며, PBR은 `SurfaceAppearance`로 구현된다. citeturn14view3turn14view0 `SurfaceAppearance`는 최대 4개 맵(Albedo/Metalness/Normal/Roughness)을 전제로 하고, Normal은 **OpenGL tangent space**를 요구하는 등 제작 규칙이 명시돼 있다. citeturn14view3

텍스처 해상도는 문서 내에서도 “업로드/사용 가능 해상도(최대 4096² 언급)”와 “UV/컴포지터 상의 최대 텍스처 공간(1024² 언급)”이 함께 등장하며, 실제로는 디바이스 리소스에 따라 자동으로 낮은 해상도부터 로딩 후 점진적으로 올리고, 동시 렌더링이 많으면 다운샘플될 수 있다고 설명한다. citeturn14view3 즉, Roblox 환경/모바일까지 고려한다면 **1024² 중심 + 필요한 곳만 선택적으로 고해상**이 안전한 설계다. citeturn14view3

### Blender ↔ Roblox 스케일/좌표계 주의점
Creator Docs의 Blender 가이드는 Blender(기본 metric)와 Studio(Studs) 단위 차이, 그리고 Up 축(Blender=Z, Studio=Y) 차이를 강조한다. citeturn14view4 특히 “Blender 경험이 없는 개발자” 기준으로는 **스케일·피벗·축**이 첫 번째 난관이 될 가능성이 높다. citeturn14view4turn9view4

### 자동화 도구 존재 여부
Roblox는 공식 문서에서 **Roblox Blender plugin**을 명시적으로 소개한다. 이 플러그인은 Blender 애드온 형태로 Roblox 계정을 연결해, “파일 export/import를 건너뛰고” Blender에서 Studio 세션으로 3D 오브젝트를 빠르게 전송하는 것을 목표로 하며, Open Cloud API 기반 오픈소스 레퍼런스 구현이라고 설명돼 있다. citeturn15view2turn16search0

또한 Open Cloud의 Assets API는 “Studio 수동 임포트 대신 HTTP 요청으로 에셋 업로드/업데이트”를 지원하고, **요청 1회당 파일 크기 최대 20MB** 등의 제한을 명시한다. citeturn15view0 파이프라인 자동화를 진지하게 고려한다면(예: CI에서 에셋 버저닝, 반복 업로드), 이 경로는 Blender MCP와 결합 가능한 “정식 API 레일”로 볼 수 있다. citeturn15view0turn15view2

## Roblox 게임 에셋 시장 분석
Roblox 에셋 시장을 볼 때는 “플레이어 대상(Avatar Marketplace)”과 “개발자 대상(Creator Store)”을 분리해야 결론이 명확해진다. Roblox 문서 기준으로 Creator Store는 **모델/이미지/메시/오디오/플러그인 등**을 제공하며, 웹과 Studio Toolbox 안에서 접근 가능하다고 설명한다. citeturn21view0

Creator Store에는 “수백만(millions)의 에셋이 있다”는 표현이 문서에 직접 등장하고, 안전을 위해 **난독화 코드, 원격 require/loadstring, 특정 로딩 API 사용** 등을 제한하는 정책을 명시한다. citeturn21view0 이는 “Roblox용 3D 에셋 판매”가 단순히 아트 자산만이 아니라, **보안/저작권/모더레이션 리스크**와 강하게 연결된 시장임을 시사한다. citeturn21view0turn21view2

image_group{"layout":"carousel","aspect_ratio":"16:9","query":["Roblox low poly environment assets","Roblox Creator Store models thumbnails","Roblox stylized 3D props"],"num_per_query":1}

### Creator Store의 수익화 트렌드 (2025~2026)
2025년 하반기~2026년 초 Creator Store의 가장 큰 변화는 **‘Model을 USD로 판매’**가 본격 도입된 점이다. DevForum 공지에서 “ID 인증 및 모더레이션 히스토리 요건”을 걸고 Creator Store에서 Models 판매를 허용한다고 밝혔고, FAQ에서는 Robux가 아니라 **USD로만 가격 책정**이 가능하다고 정리했다. citeturn19search2turn19search1

공식 Creator Docs는 더 구체적으로, Creator Store에서 플러그인/모델을 USD로 팔려면 **Stripe 기반 seller account**가 필요하며, 판매 가능 국가 제한·연령/동의 요건·30일 에스크로·월 1회 지급(매월 1일) 등 “마켓플레이스 운영 규칙”을 상세히 명시한다. citeturn21view2 모델 가격은 **최소 $2.99 ~ 최대 $249.99** 범위를 문서에 명시한다. citeturn21view2

또한 Creator Store 문서에서는 **검증(verification) 여부에 따른 배포 한도**를 제시한다(예: verified 계정은 모델/메시/이미지 각각 30일당 200개 수준, unverified는 10개 수준). citeturn21view0 이는 1인 개발자가 “AI로 에셋을 대량 생성→판매/배포”를 생각할 때, **QoS(품질)뿐 아니라 운영상 ceiling(한도)**도 고려해야 함을 의미한다. citeturn21view0

### Avatar Marketplace(3D 아바타 자산) 경제 구조
Roblox의 Marketplace(카탈로그)는 아바타 3D 자산(바디/헤드/의상/액세서리 등)을 중심으로 돌아가며, 문서 기준 **업로드 수수료 750 Robux**, 퍼블리싱 advance(카테고리별 상이), 그리고 판매 커미션 구조(기본적으로 3D 자산은 creator 30%)가 명시돼 있다. citeturn21view1 또한 경험(게임) 내에서 구매하면 경험 소유주에게도 추가 커미션이 배분되는 구조다. citeturn21view1

반면 Creator Store의 USD 판매는 “세금 및 결제 프로세싱 fee만 공제”하는 형태로 **상대적으로 높은(‘market-leading’) 수익 배분**을 내세운다. citeturn21view2turn21view0 즉, “Roblox 스타일 3D 에셋”으로 돈을 벌려면  
- **개발자용(Studio 자산) 판매: USD 기반 Creator Store** citeturn21view2turn19search1  
- **플레이어용(아바타 아이템) 판매: Robux 기반 Marketplace** citeturn21view1  
두 트랙 중 어느 쪽에 집중할지 먼저 결정하는 것이 합리적이다.

### 인기 경험(게임)의 에셋 제작 방식에 대한 관찰
공개된 채용/공식 글을 기준으로, 상위권 Roblox 게임 스튜디오는 대체로 “Studio 안에서 모든 것을 만들기”보다 **전통 DCC(Blender/Maya/C4D) + PBR 텍스처 도구(Substance/Quixel 등) + 성능 예산 관리**를 하는 쪽에 가깝다. 예를 들어 entity["organization","Uplift Games","roblox game studio"](Adopt Me 개발사)의 3D Artist 채용 공고는 Blender/Maya/C4D 숙련, PBR 지식, 하이/로우폴리 모두 제작 가능, 그리고 PC/모바일/콘솔 성능 예산을 강조한다. citeturn24view1turn24view0

또한 entity["organization","Paradoxum Games","roblox game studio"] 관련 DevForum 스포트라이트에서는 팀 초기 구성에 “모델러”가 포함되어 있었고, 성장 과정에서 3D 모델링/텍스처링도 중요한 역량으로 언급된다. citeturn24view2 (Brookhaven의 경우 현재 개발 주체가 entity["company","Voldex","game studio"]로 넘어갔다는 사실 정도는 공개 페이지에서 확인 가능하나, 내부 DCC 파이프라인 상세는 공개 자료가 제한적이다.) citeturn23search10

## 경쟁 도구 및 대안 비교
“Blender MCP”는 자동화 레이어이고, 실제 3D 생성 품질은 전용 생성기(또는 자산 라이브러리)의 영향을 크게 받는다. 따라서 비교의 축을 “MCP(오케스트레이션)” vs “전용 3D 생성”으로 단순화하기보다, **1인 개발자의 실제 과업(프롭/환경물/캐릭터/애니메이션/텍스처) 기준**으로 나누는 게 유용하다. citeturn14view2turn7view3turn27view0

### 전용 AI 3D 생성 도구 스냅샷 (가격/기능/Roblox 친화성)
- entity["company","Tripo","ai 3d generator"]  
  공식 가격 페이지 기준 Basic은 **$0/월 + 월 300 credits**이며, Professional(연간 기준 월 $11.94 표기)은 **월 3000 credits**, Smart Low Poly, 파트 세그멘테이션/완성, “스켈레톤 포함 Export”, “Bulk Export”, “상업적 사용 가능한 private models” 등을 명시한다. citeturn27view0  
  → 문서상 “Smart Low Poly + 스켈레톤 Export”를 전면에 두는 점은 Roblox의 메시 예산(20k tri)과 애니메이션 파이프라인을 의식한 포지셔닝으로 해석 가능하다. citeturn27view0turn14view0turn14view2  

- entity["company","Hyper3D","ai 3d generator"] (Rodin)  
  구독 페이지 기준 Creator는 **$24/월(월 30 credits)**, Business는 **$120/월(월 208 credits)**로 표기되며, Business 티어에서 “4K textures & High-Poly(100K) export”, API 사용 권한 등을 언급한다. citeturn27view1 (운영 주체로 Deemos Corporation 표기) citeturn27view1  
  → 높은 폴리/4K 텍스처는 Roblox 무대(모바일 포함)에서는 그대로 쓰기 어려울 수 있어, 실제론 “저폴리 옵션으로 생성→Blender에서 최적화→Roblox Import” 전제의 도구로 보는 편이 안전하다(이 판단은 Roblox의 메시 예산/텍스처 정책에 근거한 추론). citeturn27view1turn14view0turn14view3  

- entity["company","Meshy","ai 3d generator"]  
  공식 가격 페이지에서 Free는 **월 100 credits**, Meshy-4 모델 다운로드 월 10개, 결과물 라이선스 **CC BY 4.0** 등을 명시하고, 상위 플랜에서 API 및 다양한 DCC/엔진 플러그인 접근을 제공한다고 적는다. citeturn27view2 가격 금액(예: Pro $20/월 등)은 제3자 가격 요약 페이지에 의존해야 하는데, G2는 Pro $20/월 등을 표기한다(단, 과금 정책은 수시 변경 가능). citeturn25search7turn27view2  

- entity["company","Stability AI","generative ai company"] / Stable Fast 3D  
  Stability AI는 Stable Fast 3D가 “단일 이미지 → 3D 에셋”을 매우 빠르게 생성하고 UV unwrapped mesh 및 material parameters를 포함한다고 소개한다. citeturn25search14turn25search22 API 가격은 “credits 기반, 1 credit = $0.01”로 안내된다. citeturn26search0turn26search13 다만 Stable Fast 3D “요청 1회당 credit 소모량”은 공식 문서 뷰어가 본 조사 환경에서 안정적으로 열리지 않아, 공개 데모/가이드에서 제시된 “성공 1회당 2 credits, 출력은 GLB”라는 정보를 참고 수준으로만 인용한다. citeturn26search16

### Roblox 전용/친화 자동화 도구
Roblox 자체가 제공/공식 문서에 포함한 연결고리들이 이미 존재한다는 점이 중요하다.  
- **Roblox Blender plugin**: Blender에서 Studio로 직접 전송(오픈소스, Open Cloud 기반). citeturn15view2turn16search0  
- **Open Cloud Assets API**: HTTP로 모델 업로드/버전관리(요청당 최대 20MB 등 제한). citeturn15view0  
- **3D Importer의 캐시/퀵 임포트/리임포트 방향성**: 대형 씬 반복 임포트의 병목을 줄이려는 로드맵(업로드 스로틀링 이슈 언급 포함). citeturn9view4  

즉, “Roblox 전용 플러그인/도구가 없어서 Blender MCP로 억지 자동화해야 하는 상황”은 아니다. 오히려 **공식 레일(Open Cloud/Blender plugin)을 중심에 두고, MCP는 보조 자동화 레이어로 붙이는 구조**가 안정적이다. citeturn15view2turn15view0turn14view2

## 1인 개발자 관점의 실용성 평가 및 권고
### End-to-End 현실성
**가능은 하다.** Roblox 쪽 “입출력 포맷/예산/자동화” 구성 요소는 대부분 준비되어 있다. citeturn14view2turn14view0turn15view2turn15view0  
다만 “Blender MCP가 자동으로 좋은 로우폴리 에셋을 뽑아준다”가 아니라, 실전은 다음 3단계 조합이 된다.

1) **회색박스(Studio 중심)**: Roblox Studio의 파트/CSG·간단 메시에 집중해 게임 루프를 먼저 검증한다(모바일 성능 예산이 빠르게 드러남). citeturn24view3turn14view0  
2) **AI 에셋 시도(전용 생성기)**: Tripo/Hyper3D/Meshy/SF3D 중 하나로 “형태 후보”를 빠르게 뽑는다. Tripo는 Smart Low Poly/스켈레톤 Export 등을 기능으로 직접 표기하고 있다. citeturn27view0  
3) **Blender에서 최소 정리(핵심)**:  
   - Roblox 스펙(개별 메시 20k tri, watertight/두께, UV 0:1, 텍스처 예산/다운샘플링)을 만족하도록 정리한다. citeturn14view0turn14view3  
   - 스케일(Stud), 축, 피벗을 고친다. citeturn14view4turn14view2  
   - Studio 3D Importer로 가져오고 프리셋/설정으로 반복한다. citeturn14view2turn9view4  
   - 필요하면 Roblox Blender plugin/Open Cloud로 업로드 자동화를 붙인다. citeturn15view2turn15view0  

이때 Blender MCP는 (2)~(3) 구간에서 특히 “반복 작업”을 줄이는 데 효율이 있다(자동 배치/머티리얼 적용/렌더/익스포트 등). citeturn7view2turn14view2

### 학습 곡선(Blender 무경험 가정)
Roblox 공식 Blender 가이드는 Blender/Studio 간 단위·축 차이, 설정의 중요성을 비교적 길게 설명한다. citeturn14view4 또한 Roblox Staff가 “Blender는 처음엔 intimidating할 수 있다”고 전제하고 입문용 모델링 가이드를 제공하는 점은, 신규 유입에서 학습 부담이 실제 이슈라는 방증이다. citeturn24view3  
따라서 “Blender 경험 없는 1인 개발자”가 Blender MCP를 붙인다고 해서 학습 부담이 0이 되지는 않는다. MCP는 UI 조작을 줄여줄 수 있어도, **‘무엇이 올바른 메시/텍스처/피벗/스케일인지’ 판단**은 여전히 사람에게 남는다. citeturn14view0turn14view3turn14view4

### “그레이박스 → 재미 검증 → AI 에셋 교체” 전략의 실현 가능성
이 전략은 Roblox에서 특히 잘 맞는다. 이유는  
- 3D Importer가 비교적 풍부한 설정과 프리셋을 제공하고, citeturn14view2  
- 2025년 공지에서 “재임포트/캐싱/퀵 임포트” 등 반복 작업 개선이 계속 진행되고 있으며, citeturn9view4  
- Creator Store에 배포/판매를 고려하지 않더라도, 모델을 “클라우드 기반 에셋”으로 올려 재사용하는 개념이 문서에 정리되어 있기 때문이다. citeturn22view1  

즉, 재미 검증 단계에서는 Studio 중심으로 빠르게 돌리고, 이후 필요한 구간에만 AI/Blender를 투입하는 방식이 비용 대비 효과가 크다. citeturn24view3turn14view2turn27view0

### 최종 권고: Go / Pivot / Block
**권고안: “Pivot = Go(엔진은 Roblox로 직행), 단 ‘Blender MCP를 코어 생산라인으로 두는 것은 Block’”**  

- **Go 근거(Roblox로의 피벗)**:  
  - 3D Importer의 포맷/기능 스펙이 명확하고(.fbx/.gltf/.obj, PBR/리깅/애니메이션 등), citeturn14view2turn9view3  
  - 메시 예산(20k tri)과 텍스처 요구사항이 문서화되어 있어 “성능 목표를 역산”하기가 쉽고, citeturn14view0turn14view3  
  - 공식 Blender 플러그인(Open Cloud 기반)과 Assets API(20MB/call 등)가 있어 자동화의 공식 레일이 존재한다. citeturn15view2turn15view0turn16search0  

- **Block 근거(Blender MCP에 “AI 자동 모델링 생산”을 전적으로 기대)**:  
  - MCP 프로젝트들의 유지보수 편차가 크고(최신 커밋/스타 편차), “특정 구현에 락인”될 위험이 있다. citeturn2view0turn5view1turn2view4turn5view5  
  - “로우폴리+일관된 스타일+게임레디”는 도구가 Smart Low Poly/폴리 옵션을 제공하더라도(Tripo/Hyper3D), Roblox의 규격(20k tri, UV/텍스처 예산, 축/스케일)을 만족시키는 마감 작업이 남는다. citeturn27view0turn27view1turn14view0turn14view3turn14view4  
  - 결과적으로 “프롬프트만으로 끝내는 자동 생산”이 아니라 “AI 초안 → Blender 정리 → Importer 반복”이 되고, 이때 병목은 Blender 경험/기술 판단으로 이동한다. citeturn14view4turn14view2turn24view3  

**실행 관점 요약(Brain 의사결정용)**  
- **엔진 피벗은 Go**: Roblox의 3D 에셋 레일이 충분히 성숙. citeturn14view2turn15view2turn9view4  
- **Blender MCP는 “가속 장치”로 채택**: 씬 조작·반복 작업 자동화에 가치. citeturn7view2turn7view3  
- **AI 에셋 생성은 ‘전용 툴+마감’ 전제**: Tripo(스마트 로우폴리/스켈레톤 익스포트), Hyper3D(폴리 옵션/4K·하이폴리 익스포트 등), Meshy(크레딧·플러그인) 등은 후보가 될 수 있으나, Roblox 스펙 준수는 별도 과업. citeturn27view0turn27view1turn27view2turn14view0
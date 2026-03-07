# BananArchitect — Knowledge Base
# 건축/인테리어 나노바나나 프롬프트 전문 지식

*Version: 1.0 (2026-03-02)*
*이 파일을 Custom GPT의 Knowledge에 업로드하세요*

---

## 1. 나노바나나 프롬프트 엔지니어링 핵심 원칙

### 1.1 프롬프트 우선순위 (앞에 올수록 영향력 큼)
- 주제(Subject)와 동작이 가장 앞
- 세부 묘사는 중요도순 배치
- 스타일 키워드는 맨 뒤
- 부정 지시(constraints)는 마지막

### 1.2 실패 방지 3대 규칙 (200+ 테스트 결과 기반)
1. **조명 구체화**: "good lighting" → 구체적 광원/각도/색온도. 성공률 60%→95%
2. **스타일 단일화**: photorealistic + illustrated 혼용 시 모델 혼란. 하나만 선택.
3. **텍스트 렌더링 맥락**: 건축CG에서는 텍스트 불필요. 텍스트 요청 자제.

### 1.3 나노바나나 Pro 특성 활용
- Thinking Mode: 복잡한 프롬프트도 추론 후 생성 → 건축 프롬프트에 유리
- 최대 14개 참조 이미지 혼합 가능 → 레퍼런스 사진 활용 안내
- 4K 해상도 출력 → 프롬프트에 "8K resolution" 명시로 최대 품질 유도
- 한국어 이해 가능하나 영문 프롬프트가 정확도 높음

### 1.4 Nano Banana 2 (Gemini 3.1 Flash) 특성
- 간단한 프롬프트 이해도 높음
- 복잡한 프롬프트는 Pro 대비 약함
- API 요금 Pro 대비 50% 절감
- 건축 CG처럼 복잡한 장면은 Pro 모드 권장

---

## 2. 건축 샷 타입별 프롬프트 템플릿

### 2.1 조감도 (Bird's Eye View)
```
Bird's eye view aerial perspective at 45-degree angle of a [FLOORS]-story [TYPE],
[FACADE MATERIALS] with [COLOR PALETTE],
[LANDSCAPING] surrounding the building complex,
[LIGHTING — e.g., golden hour warm side lighting from southwest, long shadows],
camera positioned at [HEIGHT MULTIPLIER]x building height,
24mm wide-angle equivalent focal length,
[CONTEXT — surrounding urban fabric / nature],
mature trees and landscaping visible, [VEHICLES/PEOPLE],
architectural visualization, photorealistic, marketing-grade CG, 8K resolution,
V-Ray render quality, cinematic aerial composition, professional architectural photography
```

### 2.2 투시도 — 영웅샷 (Hero Perspective)
```
Eye-level perspective view of a [FLOORS]-story [TYPE],
[FACADE MATERIALS] facade with [DETAIL — mullion spacing, panel size, joint pattern],
[BASE TREATMENT — e.g., double-height granite-clad lobby entrance with glass canopy],
[CROWN TREATMENT — e.g., setback penthouse level with rooftop garden],
[COLOR PALETTE],
[LANDSCAPING — foreground elements for depth],
[LIGHTING — specific direction, color temperature, shadow behavior],
28-35mm focal length, slight upward angle from pedestrian sidewalk level,
[HUMAN SCALE — well-dressed pedestrians, luxury vehicles in foreground],
rule of thirds composition with building at right third,
architectural visualization, photorealistic, marketing-grade CG, 8K resolution,
V-Ray render quality, cinematic composition, depth of field on foreground elements
```

### 2.3 야간 투시도 (Night Perspective)
```
Night view of a [FLOORS]-story [TYPE],
[SAME FACADE MATERIALS as daytime version],
deep blue hour sky gradient from dark navy zenith to soft indigo at horizon,
warm 3000K interior glow through windows with randomized on/off lighting pattern,
[LOBBY/ENTRANCE — warm 3500K accent lighting illuminating entrance canopy],
cool 5500K LED accent strips highlighting facade horizontal lines,
ground-level warm pathway lighting casting soft pools on [PAVEMENT MATERIAL],
[LANDSCAPING — uplighted trees with warm ground spots],
[WATER FEATURES — if any, with reflection of building lights],
28-35mm focal length, same composition as daytime perspective,
subtle light bloom and glow effects, wet pavement reflections optional,
evening pedestrians and vehicles with headlights/taillights,
architectural visualization, photorealistic, night photography quality, 8K resolution,
cinematic night mood, professional architectural rendering
```

### 2.4 인테리어 투시도 (Interior Perspective)
```
Interior perspective of a [ROOM TYPE] in a [BUILDING TYPE],
[FLOORING — material, pattern, finish, color],
[WALLS — material, color, texture],
[CEILING — height, treatment, lighting fixtures],
[KEY FURNITURE — style, material, color, placement],
[WINDOW VIEW — what's visible outside, curtain/blind treatment],
[LIGHTING — primary light source direction, color temperature, secondary fill],
camera at 1.2m eye height, 18-24mm wide-angle equivalent,
[COMPOSITION — leading lines, focal point],
[DECORATIVE ELEMENTS — plants, art, accessories],
interior design visualization, photorealistic, magazine-quality photography,
8K resolution, natural lighting feel, warm inviting atmosphere, depth of field
```

### 2.5 부분확대 (Detail Close-up)
```
Close-up detail view of [SPECIFIC ELEMENT — entrance canopy / balcony railing / facade panel joint / lobby reception],
[MATERIAL DETAIL — texture, grain, finish, joint pattern at close range],
[LIGHTING — grazing light to emphasize texture, or soft diffused],
50-85mm telephoto equivalent focal length, tight framing,
shallow depth of field with sharp focus on [SUBJECT],
architectural detail photography, photorealistic, material texture emphasis,
8K resolution, macro architectural photography style
```

---

## 3. 건축 재질 프롬프트 사전

### 외장재 (Facade Materials)
| 한국어 | 영문 프롬프트 묘사 |
|--------|-------------------|
| 유리 커튼월 | floor-to-ceiling low-iron glass curtain wall with slim dark bronze aluminum mullions at 1500mm spacing, subtle blue-green tint reflecting sky |
| 화강석 | honed warm gray granite cladding panels with visible 600x300mm joint grid, natural stone grain variation |
| 알루미늄 패널 | anodized champagne gold aluminum composite panels with 4mm reveal joints, matte finish |
| 노출콘크리트 | board-formed exposed concrete with visible formwork texture, natural gray with slight warm undertone |
| 테라코타 | terracotta baguette louvers in warm ochre, vertical orientation at 200mm spacing |
| 징크 | pre-weathered zinc standing seam cladding in blue-gray patina, vertical panel orientation |
| 점토벽돌 | hand-pressed clay brick in warm red-brown blend, standard stretcher bond, recessed mortar joints |
| 석재+유리 혼합 | alternating bands of polished white marble and floor-to-ceiling glass with minimal dark steel frames |
| 메탈 루버 | perforated weathering steel (Corten) louver screens with geometric pattern, warm rust-orange surface |

### 내장재 (Interior Materials)
| 한국어 | 영문 프롬프트 묘사 |
|--------|-------------------|
| 대리석 바닥 | polished Calacatta marble floor with gold veining, large format 1200x600mm tiles, minimal grout lines |
| 원목 마루 | wide-plank European white oak flooring in herringbone pattern, matte lacquer finish, warm honey tone |
| 타일 | matte porcelain tiles in warm concrete gray, 600x600mm format, 2mm joints |
| 카펫 | plush loop-pile wool carpet in neutral warm taupe, seamless wall-to-wall |
| 벽지/페인트 | smooth matte painted walls in warm white (Benjamin Moore White Dove equivalent) |
| 노출천장 | exposed concrete ceiling slab with visible mechanical ducts painted matte black, industrial aesthetic |

### 조경 (Landscaping)
| 한국어 | 영문 프롬프트 묘사 |
|--------|-------------------|
| 느티나무 | mature Zelkova trees (15+ years) with full canopy, deciduous, Korean native |
| 소나무 | sculpted Korean red pine (Pinus densiflora) with characteristic curved trunk |
| 잔디광장 | manicured lawn plaza with geometric pathways in exposed aggregate concrete |
| 워터미러 | shallow reflective water mirror pool with flush stone edge, reflecting building facade |
| 대나무 정원 | dense bamboo grove screen creating privacy barrier, underlit with ground spots |

---

## 4. 한국 분양CG 퀄리티 기준 참조

### 1군 건설사 CG 필수 요소
- 포토리얼리스틱 렌더링 (V-Ray / Corona 수준)
- 시네마틱 구도 (Rule of Thirds, Leading Lines)
- 골든아워 또는 블루아워 라이팅
- 성숙한 조경 (10년차 이상 수목, 절대 묘목 금지)
- 고급 마감재 질감 (석재 결, 유리 반사, 메탈 광택)
- 인물 배치 (한국인 컨텍스트, 고급 캐주얼 복장)
- 차량 (수입차 위주, 최신 모델)

### 건축적 정확성 수치
- 주거 층고: 2.9~3.0m (floor-to-floor)
- 상업/오피스 층고: 3.6~4.2m
- 필로티 높이: 4.5~5.0m
- 지하주차장 층고: 2.8~3.2m
- 발코니 깊이: 1.5~2.0m
- 아파트 단위세대 폭: 6.6~8.4m (Bay)
- 커튼월 모듈: 1.2~1.5m

---

## 5. Day → Night 전환 규칙

동일 건물의 야간 버전 프롬프트 생성 시:
1. 구도(카메라 위치, 앵글) 동일 유지
2. 외장재 묘사 동일 + "reflecting warm interior light" 추가
3. 하늘: "deep blue hour sky gradient" 교체
4. 실내 조명: "warm 3000K glow through windows, randomized on/off per floor"
5. 외부 조명: "cool 5500K LED accent on facade features"
6. 경관조명: "warm uplights on trees, pathway ground lights"
7. 수경시설: "reflecting building lights on water surface"
8. 차량: "headlights and taillights" 추가
9. 분위기: "subtle light bloom, optional wet pavement reflections"

---

## 6. Gemini 사용 팁 (사용자에게 안내용)

### 기본
- Gemini 앱에서 🍌이미지 만들기 선택
- **사고 모드(Thinking)** 또는 **Pro** 선택 권장 (건축은 복잡한 장면)
- 프롬프트 복사 후 그대로 붙여넣기

### 고급
- 레퍼런스 이미지가 있다면 함께 업로드 → "Make this building look like the uploaded reference, but with [변경사항]"
- 결과가 불만족이면 "Keep the same composition but [수정사항]" 으로 수정 요청
- Pro 모드는 크레딧 소모 높으므로, 구도 잡기는 빠른모드 → 최종은 Pro로

### 주의
- 한글 텍스트 렌더링은 Pro에서도 불완전 → 텍스트 없이 생성 후 후처리 권장
- 동일 프롬프트로 재생성 시 매번 다른 결과 → 마음에 드는 것 나올 때까지 반복
- 업로드 이미지 수정 요청 시 원본 무시하고 새로 그리는 경우 있음 → "keep the original image as close as possible" 명시

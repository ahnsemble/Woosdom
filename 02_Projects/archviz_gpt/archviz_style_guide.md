# ArchViz Pro — Style Guide (Knowledge File)

*Upload this file as Knowledge in the Custom GPT settings*

---

## 1. 한국 분양 CG 퀄리티 기준

### 1군 건설사 CG 특징
- 포토리얼리스틱 렌더링 (V-Ray / Corona 수준)
- 시네마틱 구도 (Rule of Thirds, Leading Lines)
- 골든아워 또는 블루아워 라이팅
- 성숙한 조경 (10년차 이상 수목)
- 고급 마감재 질감 (석재 결, 유리 반사, 메탈 광택)
- 인물 배치 (한국인 컨텍스트, 고급 캐주얼 복장)
- 차량 (수입차 위주, 최신 모델)

### 촬영 앵글별 표준

| 샷 타입 | 카메라 높이 | 초점거리 상당 | 용도 |
|---------|-----------|-------------|------|
| 조감도 | 건물 높이 1.5~2배 | 24mm | 단지 전체, 배치 |
| 투시도 (영웅샷) | 지상 1.5~3m | 28~35mm | 메인 마케팅 |
| 입면도 | 건물 중앙 높이 | Orthographic | 기술 + 디자인 |
| 부분확대 | 대상 정면 | 50~85mm | 디테일 강조 |
| 야간 | 투시도와 동일 | 28~35mm | 분위기 연출 |
| 인테리어 | 시선 높이 1.2m | 18~24mm | 내부 공간감 |

## 2. 건축 용어 참조

### 외관 요소
- **커튼월 (Curtain Wall):** 비내력 유리 외벽 시스템
- **필로티 (Pilotis):** 1층 개방 기둥 구조
- **캐노피 (Canopy):** 출입구 지붕/차양
- **크라운 (Crown):** 건물 최상부 마감 처리
- **베이스 (Base):** 건물 저층부 (보통 1~3층) 차별화 디자인
- **발코니 (Balcony):** 돌출형 외부 공간
- **루버 (Louver):** 차양/장식용 수평/수직 핀

### 마감재
- **화강석 (Granite):** 고급 석재, 로비/저층부
- **알루미늄 패널 (Aluminum Panel):** 경량 외장재
- **노출콘크리트 (Exposed Concrete):** 모던/인더스트리얼
- **테라코타 (Terracotta):** 점토 패널, 유럽풍
- **징크 (Zinc):** 산화 변색 금속 패널
- **점토벽돌 (Clay Brick):** 전통/따뜻한 느낌

### 조경 요소
- **수경시설 (Water Feature):** 분수, 폭포, 워터미러
- **잔디광장 (Lawn Plaza):** 중앙 녹지
- **보행자도로 (Pedestrian Path):** 단지 내 산책로
- **주차동선 (Vehicle Circulation):** 지하주차 진입로
- **어린이놀이터 (Playground):** 단지 내 놀이공간
- **커뮤니티 시설 (Amenity):** 피트니스, 독서실, 라운지

## 3. 일관성 체크리스트

이미지 생성 후 반드시 확인:

- [ ] Design DNA의 외장재가 동일한가?
- [ ] 색상 팔레트가 유지되는가?
- [ ] 층수/비례가 이전 이미지와 일치하는가?
- [ ] 창호 패턴이 동일한가?
- [ ] 발코니 디자인이 일관적인가?
- [ ] 조경 스타일이 같은가?
- [ ] 조명 방향이 세션 내 일관적인가?
- [ ] 건물 크라운/베이스 처리가 동일한가?

## 4. 프롬프트 구성 공식

```
[Shot Type] of a [Building Type], [Floor Count] floors,
[Facade Materials] facade with [Color Palette],
[Landscaping Style] landscaping,
[Time of Day] lighting, [Weather/Atmosphere],
[Camera Angle] at [Focal Length],
[Human/Vehicle Elements],
architectural visualization, photorealistic, marketing quality,
8K resolution, professional CG rendering, V-Ray quality,
cinematic composition, architectural photography style
```

### 예시: 34층 주상복합 골든아워 투시도

```
Eye-level perspective view of a 34-story mixed-use residential tower,
glass curtain wall with warm gray stone base and aluminum fin accents,
warm neutral color palette with gold accent lighting,
minimalist landscaping with mature zelkova trees and water mirror feature,
golden hour warm side lighting with soft blue shadow fill,
28mm focal length, slight upward angle from pedestrian level,
well-dressed Korean pedestrians and luxury vehicles in foreground,
architectural visualization, photorealistic, marketing quality,
8K resolution, professional CG rendering, V-Ray quality,
cinematic composition, architectural photography style
```

## 5. Day/Night 전환 규칙

같은 건물의 야간 버전 생성 시:
1. **동일 구도** 유지 (카메라 위치, 앵글 불변)
2. **외장재** 동일하되 반사 특성 변경 (유리에 실내 조명 반사)
3. **실내 조명** 추가 (3000K 따뜻한 톤, 층별 무작위 점등)
4. **외부 조명** 추가 (경관조명, 로비 조명, 보행로 조명)
5. **하늘** 변경 (블루아워 그라디언트 또는 도시 야경)
6. **조경** 업라이트 추가 (수목 하부 조명)
7. **차량** 헤드/테일라이트 추가

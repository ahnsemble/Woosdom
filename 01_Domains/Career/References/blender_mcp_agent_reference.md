# Blender MCP + Agent Manager 레퍼런스

*Created: 2026-02-22*
*Tags: #reference #3d #blender #mcp #aec #bim*

---

## 개요
Antigravity Agent Manager + Blender MCP 조합으로 3D 모델을 에이전트가 자동 생성한 사례.

## 결과물 스펙
- **도구:** Blender 4.4.0 + Antigravity Agent Manager + Blender MCP
- **오브젝트 수:** 1,568개
- **구조:** 역원뿔형 Vessel (장식용 성배/파빌리온)
- **Phase별 자동 생성:**
  - Phase 10-11: HD 브론즈 머티리얼 + 조명 (5개 머티리얼, 8개 조명)
  - Phase 13-14: 내부 계단 + 브릿지 (128개)
  - Phase 15: 하부 구리 플레이팅 패널 (6 디스크)
  - Phase 18: 수평 링 빔 (18개)

## 머티리얼 시스템
- **Bronze_Metal_HD:** 프로시저럴 노이즈 기반 브론즈 (색상 변화 + 러프니스 변화 + 범프맵)
- **Copper_Underside:** 폴리싱 구리색 반사 표면 (러프니스 0.08)
- **Foundation_Concrete:** 어두운 콘크리트
- **Ground_Pavement:** 노이즈 텍스처 포장재

## 렌더 설정
- 엔진: Cycles (256 샘플 + OpenImageDenoise)
- 해상도: 1920 × 1080
- 환경: Nishita 스카이 모델
- 조명: 3점 조명 + 4개 내부 액센트 라이트

## 활용 가능성
1. **Project Crossy** — 3D 에셋 자동 생성 필요 시 파이프라인 참고
2. **AEC FDE 전환** — BIM 시각화 / IFC 모델 렌더링에 Blender MCP 활용 가능
3. **일반** — 에이전트 기반 3D 모델링 워크플로우의 현실적 수준 벤치마크

## 출처
- 타 사용자의 Antigravity 작업물 (2026-02-22 확인)
- 스크린샷 기반 분석

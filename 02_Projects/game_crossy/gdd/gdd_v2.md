```yaml
agent: game_designer
status: needs_review
result:
  summary: "[v2] Critical/Warning 피드백 반영 완료: 스킬 3분류/등급제 도입, 메타 프로그레션 심화, 튜토리얼 런 신설, 난이도 S-커브 적용."
  document:
    type: gdd
    content: |
      # Game Design Document: Hybrid Casual Hopper (Project Crossy)
      *Version 2.0 | 2026-02-18 | [v2 Updated]*

      ## 1. Game Overview
      **Pitch:** "Crossy Road meets Vampire Survivors." (로그라이크 스킬 빌딩 x 무한 횡단 아케이드)
      **Genre:** Hybrid Casual Arcade / Roguelite
      **Target Audience:** 깊이 있는 성장을 원하는 캐주얼 게이머 (Session 3~5min).
      **USP:** "Hop" 컨트롤의 단순함 + "Build"의 전략적 깊이.

      ## 2. Core Loop [v2 변경]
      1. **Tutorial Run (First Time):** 강제된 첫 실행. 이동 → 장애물 → 레벨업 → 사망 → 보상 사이클 학습.
      2. **Hop & Dodge:** 탭으로 전진, 스와이프/더블탭(Dash)으로 회피.
      3. **Collect & Grow:** XP Orb 수집 → 레벨업 (30~60초 주기) → 스킬 선택 (Max Lv 10).
      4. **Die & Reward:** 사망 시 코인 획득, 퀘스트 달성 체크.
      5. **Meta Progression:** 코인으로 패시브 업그레이드, 캐릭터 해금, 시작 부스트 구매.

      ### Controls [v2 변경]
      - **Tap:** Hop Forward (기본)
      - **Swipe L/R/Back:** 방향 이동
      - **Double Tap:** **Dash** (전방 2칸 빠르게 이동 / 쿨타임 존재) [New]
      - **Auto-Move:** 설정에서 ON/OFF 토글 (Hold 대신 자동 전진) [New]

      ## 3. Skill System Redesign (Deep Roguelite) [v2 변경]
      단순 보조를 넘어 플레이 스타일을 바꾸는 3가지 카테고리로 재편.
      **Max Level:** 10 (이후 XP는 보너스 코인으로 전환).
      **Rarity:** Common (White) / Rare (Blue) / Epic (Purple).

      ### Category A: Attack / Modification (환경 제어)
      - **Dash (Active):** 더블 탭으로 전방 2칸 순간이동 + 무적 0.2초. (Epic: 쿨타임 감소)
      - **Bulldozer (Passive):** 10칸마다 전방 장애물(차/나무) 1개 파괴.
      - **Teleport Side (Active):** 화면 끝에서 반대편 끝으로 이동 가능.
      - **Time Freeze (Active):** 피격 직전 1회 시간 정지 (쿨타임 60초).

      ### Category B: Defense / Evasion (생존)
      - **Shield (Passive):** 1회 피격 무효화 (재생 불가/스테이지 클리어 시 재생).
      - **Safety Net (Passive):** 강(River)에 빠지면 즉시 뒤로 튕겨나옴 (1회).
      - **Eagle Eye (Passive):** 독수리/기차 경고 시간 +1.0초.

      ### Category C: Economy / Utility (스노우볼)
      - **Coin Magnet (Passive):** 3타일 내 코인/XP 자동 수집.
      - **Greed (Passive):** 코인 획득량 +20%, 하지만 장애물 속도 +5%.
      - **Investment (Passive):** 매 50스텝마다 이자 코인 획득.

      ### Synergies (조합 예시)
      - **Speed Runner:** *Dash* + *Coin Magnet* = 대시 경로상의 코인 자동 수집.
      - **Immortal:** *Shield* + *Time Freeze* = 2중 생존기.

      ## 4. Meta Progression (The Long Game) [v2 신설]
      단순 캐릭터 해금을 넘어 지속적인 스탯 강화를 제공.

      ### Passive Upgrade Tree (Coin Sink)
      | Stat | Max Lv | Cost Scaling | Effect |
      |---|---|---|---|
      | **Base Speed** | 20 | Low | 캐릭터 기본 이동 속도 증가 |
      | **Coin Value** | 20 | Medium | 코인 획득량 +5% per Lv |
      | **Magnet Range** | 10 | High | 기본 자석 범위 증가 |
      | **Reroll Count** | 5 | Very High | 스킬 선택 시 무료 리롤 횟수 |
      | **Revive Discount** | 5 | High | 부활 비용 감소 |

      ### Start Boosts (Consumable)
      런 시작 전 코인으로 구매.
      - **Head Start:** 50칸 건너뛰고 시작.
      - **Insurance:** 사망 시 코인 100% 보존 (미구매 시 50%만 획득 등 페널티 고려 가능하나, 현재는 보너스로 설계).
      - **Random Skill:** 랜덤 스킬 1개 갖고 시작.

      ### Quests
      - **Daily (3/day):** 짧은 호흡 (예: "기차 5번 피하기", "코인 100개 수집").
      - **Weekly (1/week):** 긴 호흡 (예: "누적 5000칸 이동", "Rare 스킬 3개 수집").

      ## 5. Character Roster (Unique Traits) [v2 변경]
      모든 캐릭터는 고유한 **Trait**을 가지며 플레이 전략을 바꿈.

      | ID | Name | Unlock | Trait (Unique Gameplay) |
      |---|---|---|---|
      | `char_chicken` | **Original Chicken** | Default | **Balanced:** 레벨업 시 선택지 4개 (기본 3개). |
      | `char_bot` | **Cyber Bot** | Tutorial Clear | **Tech:** 스킬 1회 무료 교체 (Reroll) 매 런마다 제공. |
      | `char_wizard` | **Mage** | 30 Revives | **Arcane:** 스킬 등급 업그레이드 확률(Rare/Epic) +20%. |
      | `char_ninja` | **Shadow** | 5 Rare Skills | **Agile:** *Dash* 스킬 기본 장착. 측면 이동 속도 2x. |
      | `char_tank` | **Dozer** | 7 Day Login | **Heavy:** *Bulldozer* 스킬 기본 장착. 이동 속도 -10%. |

      ## 6. Level Design & Difficulty (S-Curve) [v2 변경]
      무한 선형 증가 대신 **S-Curve**와 **Soft Cap** 적용.

      ### Difficulty Curve parameters
      - **Speed Multiplier:**
        - 0~200 Steps: 완만한 상승 (학습 구간)
        - 200~500 Steps: 급격한 상승 (챌린지 구간)
        - 500+ Steps: 완만한 수렴 (**Max +35%** Soft Cap)
      - **Traffic Density:** **Max +25%** 제한. 너무 빽빽해서 불가항력적인 죽음 방지.
      - **Eagle Timer:** **Min 0.7s** 제한. 반응 가능 시간 보장.

      ### Micro Events (15~25 Steps 주기)
      - **Merchant:** 코인으로 HP 회복 or 스킬 구매.
      - **Gamble Box:** 50% 확률로 코인 대박 or 50% 확률로 몬스터 스폰.
      - **Rest Area:** 50스텝마다 밀도 0% 안전지대 (v1 유지).

      ## 7. Economy & Monetization [v2 변경]
      **Ad Strategy (Less is More):**
      - **Ad Triggers:** 2개로 축소.
        1. **Revive:** 1회 부활 (가장 강력한 트리거).
        2. **Double Rewards:** 결과 화면 보상 2배.
      - **Skill Reroll:** 코인 소모(50 → 100 → 200)로 변경. 광고 아님.
      - **Piggy Bank:** 광고 해금 제거 → "누적 5000 코인 획득"으로 변경.

      **IAP:**
      - **No Ads ($2.99):** 순수 광고 제거.
        - 부활/2배 보상 버튼 누르면 광고 없이 즉시 적용.
        - 버프(코인 +20%) 등은 포함하지 않음 (P2W 오해 방지).
      - **Starter Pack ($4.99):** Mage + 5000 Coins + 10 Revive Tickets.

      ## 8. Onboarding Flow (Tutorial Run) [v2 신설]
      1. **Intro:** 타이틀 없이 즉시 게임 진입.
      2. **Phase 1 (Move):** "Tap to Hop" 손가락 가이드. 5칸 이동.
      3. **Phase 2 (Obstacle):** 멈춰있는 차, 느린 통나무, 경고등 울리는 기차 순차 경험.
      4. **Phase 3 (Develop):** 필드에 떨어진 XP Orb 강제 수집 → Level Up 연출 → **Coin Magnet** (Fixed) 선택.
      5. **Phase 4 (Death):** 필연적인 죽음 (또는 일정 구간 도달) → "스킬 덕분에 더 멀리 왔습니다!" 메시지.
      6. **Phase 5 (Unlock):** 획득 코인으로 **Cyber Bot** 무료 해금 유도 → 메인 로비 개방.

      ## 9. Technical Specifications (JSON Schemas) [v2 추가/변경]

      ### Level Config Schema (Expanded)
      ```json
      {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
          "difficulty_curve": {
            "type": "object",
            "properties": {
              "speed_curve_type": { "enum": ["LINEAR", "S_CURVE", "EXPONENTIAL"] },
              "max_speed_multiplier": { "type": "number", "default": 1.35 },
              "max_density_multiplier": { "type": "number", "default": 1.25 },
              "min_eagle_timer": { "type": "number", "default": 0.7 }
            }
          },
          "micro_events": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "event_id": { "type": "string" },
                "frequency_step_min": { "type": "integer" },
                "frequency_step_max": { "type": "integer" }
              }
            }
          }
        }
      }
      ```

      ### Skill Config Schema (Expanded)
      ```json
      {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "category": { "enum": ["ATTACK", "DEFENSE", "ECONOMY"] },
          "rarity": { "enum": ["COMMON", "RARE", "EPIC"] },
          "max_level": { "type": "integer", "default": 10 },
          "base_effect_value": { "type": "number" },
          "level_scaling": { "type": "number" },
          "synergy_ids": { "type": "array", "items": { "type": "string" } }
        }
      }
      ```

      ### Quest Config Schema (New)
      ```json
      {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
          "quest_id": { "type": "string" },
          "type": { "enum": ["DAILY", "WEEKLY", "LIFETIME"] },
          "condition": {
            "type": "object",
            "properties": {
              "metric": { "enum": ["HOP_COUNT", "KILL_ENEMY", "COLLECT_COIN", "REACH_SCORE"] },
              "target_value": { "type": "integer" }
            }
          },
          "reward": {
            "type": "object",
            "properties": {
              "currency": { "enum": ["COIN", "GEM"] },
              "amount": { "type": "integer" }
            }
          }
        }
      }
      ```

      ### Passive Upgrade Schema (New)
      ```json
      {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
          "upgrade_id": { "type": "string" },
          "name": { "type": "string" },
          "max_rank": { "type": "integer" },
          "cost_base": { "type": "integer" },
          "cost_multiplier": { "type": "number" },
          "stat_increase_per_rank": { "type": "number" }
        }
      }
      ```

  design_rationale: |
    1. **S-Curve & Soft Cap:** v1의 무한 난이도 상승은 유저에게 "불공정함"을 느끼게 함. 실력으로 극복 가능한 "Flow State" 구간(200~500 Step)을 의도적으로 설계함.
    2. **Skill Tier & Categories:** 모든 스킬이 평등하면 선택의 재미가 없음. Attack/Defense/Economy로 나누어 유저가 "이번 판은 파밍 런" 또는 "기록 갱신 런"을 의도적으로 선택하게 유도.
    3. **Tutorial Run:** 하이브리드 캐주얼의 핵심은 "첫 3분"임. 글로 설명하는 대신 강제된 성공 경험(Skill 획득)을 먼저 제공하여 시스템 이해도를 높임.
    4. **Passive Sink:** 코인이 쌓이면 게임 할 이유가 사라짐. 기하급수적으로 비싸지는 패시브 업그레이드를 통해 장기 리텐션 확보.

  kpi_prediction:
    d1_retention_estimate: "45% (Tutorial Run & Early Rewards 강화로 상승 예상)"
    monetization_risk: "Low (No Ads 분리로 P2W 인식 감소, Reroll 코인화로 재화 가치 상승)"

  handoff:
    to_engineer: |
      - **Priority:** Implement `TutorialManager` first. It overrides standard spawning rules.
      - **Difficulty:** Implement S-Curve logical function for speed calculation.
      - **Controls:** Add Double-Tap detection logic (threshold ~200ms).
      - **Data:** Use new `PassiveUpgrade` and `Quest` schemas to build the meta-layer backend.
    to_art_director: |
      - **Skill Icons:** Must clearly distinguish categories by Border Color (Red/Blue/Gold).
      - **Rarity VFX:** Rare/Epic skills need shiny shader effects on the card UI.
      - **Dash VFX:** Trail renderer needed for the Dash skill to convey speed/invincibility.
      - **Onboarding:** Need animated "Hand Cursor" assets for the tutorial overlay.

  open_questions:
    - **Double Tap vs Button:** 더블 탭이 오작동(빠른 연타와 혼동)할 경우, 화면 하단에 별도 'Dash' 버튼 배치 고려 필요. 테스트 후 결정.
    - **Quest Reset:** 일일 퀘스트 리셋 시간을 로컬 타임 자정으로 할지, UTC 0시로 할지 서버 여부에 따라 결정 필요. (MVP는 로컬 타임 권장).
```

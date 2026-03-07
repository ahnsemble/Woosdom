```yaml
agent: market_analyst
status: complete
collected_at: "2026-02-18T21:35:00+09:00"
result:
  summary: "Pure Infinite Hoppers are saturated/declining; Hybrid Casual (adding progression/meta) is the only viable path."
  data:
    - source: "Sensor Tower, data.ai, AppMagic Public Summaries (2024-2026)"
      content: "Market trends, retention benchmarks, competitor performance"
      freshness: "as_of 2026-02-18"
  
  competitors:
    - name: "Crossy Road"
      downloads: "100M+ (Lifetime)"
      revenue: "Steady (Ad-driven + IAP)"
      d1_retention: "~40-45% (Est.)"
      monetization: "Ads (Video/Native) + Character IAP"
      key_strength: "Timeless Art Style, IP Collabs"
      key_weakness: "Shallow Loop (Pure High Score)"
    - name: "Crossy Road Castle"
      downloads: "N/A (Apple Arcade)"
      revenue: "Subscription Share"
      d1_retention: "High (High Qual)"
      monetization: "Apple Arcade Subscription"
      key_strength: "Multiplayer Co-op, Level-based progression"
      key_weakness: "Platform Exclusivity, Connection Issues"
    - name: "Subway Surfers"
      downloads: "4B+ (Lifetime)"
      revenue: "Very High"
      d1_retention: "~40-50%"
      monetization: "Hybrid (Ads + Season Pass + Skins)"
      key_strength: "LiveOps, Constant Events"
      key_weakness: "Old Engine, Very Crowded Genre"
    - name: "Stumble Guys"
      downloads: "High (Viral)"
      revenue: "High (IAP focused)"
      d1_retention: "~35-40%"
      monetization: "Battle Pass + Skins (Gacha)"
      key_strength: "Social/Party Gameplay, Fall Guys on Mobile"
      key_weakness: "Aggressive Monetization, Bot issues"
    - name: "Steppy Pants"
      downloads: "5M+"
      revenue: "Low/Moderate"
      d1_retention: "Moderate"
      monetization: "Ads + VIP Sub"
      key_strength: "Physics Comedy, Unique Aesthetic"
      key_weakness: "Niche Gameplay, Frustrating Controls"
    - name: "Crossy Tiny Bird Tappy"
      downloads: "<100k"
      revenue: "Negligible"
      d1_retention: "Low"
      monetization: "Intrusive Ads"
      key_strength: "None (Clone)"
      key_weakness: "Floaty Controls, Ad spam, No polish"
    - name: "Crossy Dillo"
      downloads: "Low"
      revenue: "Negligible"
      d1_retention: "Very Low"
      monetization: "Excessive Ads"
      key_strength: "None"
      key_weakness: "Chaos, Unplayable, Ad spam"
    - name: "Crossy Cross"
      downloads: "Low"
      revenue: "Negligible"
      d1_retention: "Low"
      monetization: "Ads"
      key_strength: "None"
      key_weakness: "Bad Controls, Generic Art"
    - name: "Cross Road Chicken"
      downloads: "Moderate (Early)"
      revenue: "Low"
      d1_retention: "Low"
      monetization: "Ads"
      key_strength: "Early Mover"
      key_weakness: "Updates Stopped, Shallow"
    - name: "Climb Knight"
      downloads: "Niche"
      revenue: "Niche"
      d1_retention: "Good (Niche)"
      monetization: "Premium/Ads"
      key_strength: "Verticality, Skill-based"
      key_weakness: "Low Visibility"

  benchmarks:
    ecpm_rewarded: "$19 - $30 (Tier 1 US/KR/JP)"
    ecpm_interstitial: "$10 - $20 (Tier 1)"
    retention_arcade_d1: "30% - 40%"
    retention_arcade_d7: "8% - 13%"
    retention_arcade_d30: "3% - 6% (Need Hybrid Meta to boost this)"
    cpi_ios_arcade: "$2.50 - $3.50 (Tier 1)"
    cpi_android_arcade: "$1.50 - $2.50 (Globals)"

  review_analysis:
    top_complaints:
      - "Repetitive Gameplay: 'Fun for 10 minutes, then boring.'"
      - "Multiplayer Issues: 'Can't connect to friend next to me.'"
      - "Ad Spam: 'Ads after every single death.'"
      - "Pay-to-Win/Unlock: 'Takes too long to get good characters.'"
      - "Input Lag: 'I swiped but chicken didn't move.'"
    top_praises:
      - "Social/Co-op Fun: 'Laughing with friends/kids.'"
      - "Character Collection: 'Love unlocking the secret mascot.'"
      - "Pick-up-and-play: 'Perfect for bus rides.'"
      - "Fair Ads: 'Ads only when I want to revive.'"
      - "Art Style: 'Cute, vibrant voxel art.'"

  aso_keywords:
    korean:
      - "무한의계단" (Infinite Stairs - Major Ref)
      - "길건너친구들" (Crossy Road)
      - "캐주얼게임" (Casual Game)
      - "아케이드" (Arcade)
      - "동물게임" (Animal Game)
      - "점프게임" (Jump Game)
      - "무한러닝" (Infinite Running)
      - "킬링타임" (Time Killer)
      - "픽셀아트" (Pixel Art)
      - "피하기" (Avoidance)
    english:
      - "Crossy Road"
      - "Endless Hopper"
      - "Arcade Runner"
      - "Pixel Art Game"
      - "Voxel Animal"
      - "Tap to Jump"
      - "Frogger Style"
      - "Obstacle Course"
      - "Casual Arcade"
      - "Multiplayer Runner"

  flags:
    market_saturated: true
    emerging_trend: "Roguelike Elements (Random Buffs), Squad/Party Mechanics"

  korea_market_insight: |
    **'무한의 계단' (Infinite Stairs) Phenomenon:**
    한국 시장에서는 '길건너친구들'보다 '무한의 계단'이 아케이드 킹입니다.
    단순 반복 조작(Quick reaction) + 수집욕(Collection) + 병맛 스킨(K-Memes)이 핵심.
    한국 유저는 '경쟁'과 '숙련도 과시(Skin/Ranking)'에 매우 민감합니다.
    단순 달리기보다 PVP나 랭킹 시스템이 리텐션에 필수적입니다.

  brain_summary: |
    1. **순수 호퍼는 레드오션**: 단순 클론은 필패. Crossy Road Castle처럼 '멀티'나 '스테이지' 깊이가 필요.
    2. **하이브리드 필수**: D30 6% 저조. 로그라이크(스킬 선택)나 RPG 성장(장비/스탯) 메타 없이는 LTV 안 나옴.
    3. **Ads Revenue**: 보상형 광고(부활/캐릭터 뽑기)가 핵심 BM. eCPM $20+ 로 매우 높음.
    4. **기술적 차별화**: 1000개 이상의 물리 오브젝트가 쏟아지는 등 'Engine Power'를 보여주는 시각적 쾌감 필요.
    5. **한국 시장**: '무한의 계단' 식의 PVP/랭킹 도입 고려 강력 추천.
```

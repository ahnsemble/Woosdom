```yaml
agent: game_designer
status: draft
result:
  summary: "Hybrid Casual Hopper GDD v1: One-tap Core Loop + Roguelike Skill Meta to drive D30 Retention."
  document:
    type: gdd
    content: |
      # Game Design Document: Hybrid Casual Hopper (Project Crossy)
      *Version 1.0 | 2026-02-18*

      ## 1. Game Overview
      **Pitch:** "Crossy Road meets Vampire Survivors."
      **Genre:** Hybrid Casual Arcade / Roguelite
      **Target Audience:** Casual gamers (commuters, breaks) who crave progression beyond high scores.
      **USP (Unique Selling Point):** The simplicity of "hop" controls combined with the depth of "build-crafting" via roguelike skills.

      ## 2. Core Loop
      1. **Hop:** Player taps to move forward 1 tile. (Swipe L/R/Back to move sideways/back).
      2. **Dodge:** Avoid cars, trains, rivers, and eagles.
      3. **Collect:** Gather Coins and XP Orbs on the map.
      4. **Level Up (In-Game):** Every 100 XP, pause gameplay -> Choose 1 of 3 Random Skills (Roguelike element).
      5. **Die:** Hit an obstacle or get caught by the screen scroll.
      6. **Meta:** Use Coins to unlock Characters (permastats) or Upgrade Global Passives.

      ### Controls
      - **Tap:** Hop Forward (Primary action, 90% of inputs)
      - **Swipe Left:** Hop Left
      - **Swipe Right:** Hop Right
      - **Swipe Down:** Hop Backward
      - **Hold:** Rapid Hop (Optional setting for advanced players)

      ## 3. Roguelike Meta (The Retention Hook)
      Unlike classic Crossy Road, the player character grows stronger *during* the run.
      
      **Trigger:** Collect XP Orbs -> Fill Bar -> Level Up.
      **Action:** Game pauses, 3 cards appear.
      **Skill Examples:**
      - *Double Jump:* Jump over 1 obstacle (Cooldown: 10 hops).
      - *Coin Magnet:* Attract coins within 3 tiles.
      - *Time Dilation:* Cars move 20% slower.
      - *Ghost Mode:* Pass through 1 car without dying (Consumable).
      - *Eagle Eye:* See incoming trains 1 second earlier.

      ## 4. Character Collection (MVP 5)
      Characters are not just skins; they have passive bonuses.

      | Character ID | Name | Unlock Condition | Passive Bonus | Voxel Style |
      |---|---|---|---|---|
      | `char_chicken` | **Original Chicken** | Default | None (Baseline) | Classic White Chicken |
      | `char_robot` | **Cyber Bot** | 1000 Coins | +10% XP Gain | Metallic, Glowing Eyes |
      | `char_wizard` | **Mage** | 50 Deaths | Start run with 1 random skill | Blue Robe, Hat |
      | `char_ninja` | **Shadow** | Score 200 | Side hops are 2x faster | Black Suit, Red Scarf |
      | `char_rich` | **Piggy Bank** | Watch 5 Ads | +20% Coin Value | Pink, Gold Chain |

      ## 5. Procedural Generation Rules
      The world is generated in "Chunks" (rows).
      
      **Chunk Types:**
      - `SAFE_GRASS`: Static trees, rocks. (0-2 obstacles)
      - `ROAD`: Cars moving L->R or R->L. Speed varies by difficulty.
      - `RIVER`: Logs floating. Sink if not on log.
      - `TRAIN_TRACK`: Warning light -> Fast train.
      - `REST_AREA`: (New) 100% Safe row with multiple coins/XP OR reward chest. Appears every 50 steps.

      **Difficulty Scaling:**
      - `Speed Multiplier`: +5% every 50 steps.
      - `Traffic Density`: +2% spawn rate every 30 steps.
      - `Eagle Timer`: Decreases by 0.1s every 100 steps.

      ## 6. Economy & Monetization
      **Currencies:**
      - **Coins (Soft):** Earned in-game, Chests. Used for Character Gacha.
      
      **Ad Strategy (High eCPM Focus):**
      1. **Revive:** "Continue? Watch Video." (Limit 1 per run).
      2. **Gacha Reroll:** "Don't like these 3 skills? Watch Ad to Reroll."
      3. **Double Rewards:** End of run, 2x Coins.
      
      **IAP (MVP):**
      - `No Ads`: $2.99 (Removes forced ads, grants permanent +20% Coin buff).
      - `Starter Pack`: $4.99 (Mage Character + 5000 Coins).

      ## 7. Onboarding Flow
      1. **Game Start:** Direct to gameplay. No menu.
      2. **Hand Cursor:** Animates "Tap" gesture.
      3. **First Death:** "Tap to Restart" (Instant).
      4. **First 50 Coins:** Unlock Tutorial "Gacha" (Free first pull -> Get 'Cyber Bot').

      ## 8. Technical Specifications (JSON Schemas)

      ### Level Config Schema
      ```json
      {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
          "chunk_types": {
            "type": "array",
            "items": { "enum": ["GRASS", "ROAD", "RIVER", "TRAIN", "REST"] }
          },
          "difficulty_curve": {
            "type": "object",
            "properties": {
              "speed_increase_per_step": { "type": "number" },
              "density_increase_per_step": { "type": "number" }
            }
          }
        }
      }
      ```

      ### Character Config Schema
      ```json
      {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "name": { "type": "string" },
          "voxel_model_path": { "type": "string" },
          "base_stats": {
            "type": "object",
            "properties": {
              "move_speed": { "type": "number" },
              "xp_multiplier": { "type": "number" },
              "coin_multiplier": { "type": "number" }
            }
          },
          "starting_skill_id": { "type": "string" }
        }
      }
      ```

      ### Skill Config Schema
      ```json
      {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "name": { "type": "string" },
          "description": { "type": "string" },
          "rarity": { "enum": ["COMMON", "RARE", "LEGENDARY"] },
          "effect_type": { "enum": ["PASSIVE_STAT", "ACTIVE_ABILITY", "ONE_TIME_USE"] },
          "effect_value": { "type": "number" },
          "duration": { "type": "number" }
        }
      }
      ```

  design_rationale: |
    1. **Why Roguelike Skills?** The market analysis showed simple hoppers have low D30 retention. Adding "builds" (e.g., Speed Build vs. Safety Build) gives depth without complex controls.
    2. **Why Characters have Stats?** Cosmetic-only skins (Crossy Road model) are hard to monetize for indies without massive IP. Performance-impacting characters drive "Need" to unlock.
    3. **Why One-Tap?** Accessibility is king. Complex controls increase churn for this genre.
    4. **Why Voxel?** Cheapest asset production pipeline for 1-person dev + AI.

  handoff:
    to_engineer: |
      - Use `Godot Resources` (.tres) for all Configs based on the JSON Schemas.
      - Implement a `ChunkManager` that spawns rows based on the weighting in LevelConfig.
      - Create a modular `SkillSystem` where effects can be stacked.
      - Ensure input handling prioritizes 'Tap' over 'Swipe' for responsiveness.
    to_art_director: |
      - Style: MagicaVoxel, Orthographic Camera, Vibrant/Saturated Palette.
      - Visual Feedback: "Squash & Stretch" on hop is mandatory for game feel.
      - UI: Minimalist. Skill cards should look like Tarot cards (Vampire Survivors style but Voxel art).
      - Particles: Explosion of voxels on death (Critical for 'Engine Power' feel).

  open_questions:
    - Should we implement "Landscape" mode? (Currently assuming Portrait only).
    - Max level cap per run? (Suggest 10 for MVP balance).
```

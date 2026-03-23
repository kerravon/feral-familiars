# 🎮 Gameplay Mechanics

## 🌌 Spawning System
Spawns occur periodically (default every 2 minutes) in active channels with a configurable chance (default 15-25%).

### Types of Encounters
- **Essences (80%):** 
  - **Base Elements:** Earth, Wind, Fire, Water (Equal spawn weight).
  - **Special:** Arcane (Rare - ~50% spawn rate compared to base elements).
- **Spirits (20%):** Feline, Canine, Winged, Goblin. The core of a familiar.

### 💎 Rarity (Spirits Only)
Rarity determines the creation cost and the **success chance of Passive Effects**:
- **Common (60%):** Cost: 10 | Passive Chance: 15%
- **Uncommon (25%):** Cost: 20 | Passive Chance: 25%
- **Rare (12%):** Cost: 40 | Passive Chance: 40%
- **Legendary (3%):** Cost: 80 | Passive Chance: 60%

## 🪢 Capture (Binding)
- **Keyword:** `bind` for essences, `bind spirit` for spirits.
- **Limits:** 
  - **Essences:** Currently unlimited.
  - **Spirits:** Max **5** in inventory.
- **Rules:**
  - **First Response:** The first player to type the keyword correctly wins the encounter.
  - **Anti-Macro:** A 1-second delay is enforced after a spawn before capture is possible.
  - **Expiration:** Encounters fade after a few seconds if not bound.

## 🟢 Active Familiars
Equipping a familiar using `/summon` makes it your active companion. 
- **Stable Limit:** You can hold a maximum of **3** familiars.
- **Passive Bonuses:**
  - **Base Familiars:** % Chance to **double** captured essences of the SAME type (e.g., Fire familiar doubles Fire essences).
  - **Arcane Familiars:**
    - Higher % Chance (+15% flat) to **double ANY** essence type captured.
    - **Temporal Anchor:** If any player in the guild has an active Arcane familiar, all spawns in that server stay active for an additional **+15 seconds**.

## 🍂 Releasing
If your inventory or stable is full, you can release items to make room:
- `/release-spirit [id]`: Permanently removes a spirit from your inventory.
- `/release-familiar [id]`: Permanently removes a familiar from your stable.

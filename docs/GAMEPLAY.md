# 🎮 Gameplay Mechanics

## 🌌 Spawning System
Spawns occur periodically (default every 2 minutes) in active channels with a configurable chance (default 15-25%).

### Types of Encounters
- **Essences (80%):** Earth, Wind, Fire, Arcane, Water. Used for rituals and paying taxes.
- **Spirits (20%):** Feline, Canine, Winged, Goblin. The core of a familiar.

### 💎 Rarity (Spirits Only)
Rarity determines the creation cost and potential power of a familiar:
- **Common (60%):** Cost: 10
- **Uncommon (25%):** Cost: 20
- **Rare (12%):** Cost: 40
- **Legendary (3%):** Cost: 80

## 🪢 Capture (Binding)
- **Keyword:** `bind` for essences, `bind spirit` for spirits.
- **Rules:**
  - **First Response:** The first player to type the keyword correctly wins the encounter.
  - **Anti-Macro:** A 1-second delay is enforced after a spawn before capture is possible.
  - **Expiration:** Encounters fade after a few seconds if not bound.

## 🟢 Active Familiars
Equipping a familiar using `/equip` makes it your active companion. Currently, only one familiar can be active at a time. Active familiars provide passive bonuses (under development).

# 🎮 Gameplay Mechanics

## 🌌 Spawning System
Spawns occur periodically (default every 2 minutes) in active channels with a configurable chance (default 15-25%).

### Types of Encounters
- **Essences (80%):** 
  - **Base Elements:** Earth, Wind, Fire, Water (Equal spawn weight).
  - **Special:** Arcane (Rare - ~50% spawn rate compared to base elements).
- **Spirits (20%):** 
  - **Base Spirits:** Feline, Canine, Winged, Goblin (Standard spawn rate).
  - **Special:** Restless (Rare - ~10% spawn weight).

### 💎 Rarity (Spirits Only)
Rarity determines the creation cost and the **success chance of Passive Effects**:
- **Common (60%):** Cost: 10 | Passive Chance: 8%
- **Uncommon (25%):** Cost: 20 | Passive Chance: 15%
- **Rare (12%):** Cost: 40 | Passive Chance: 25%
- **Legendary (3%):** Cost: 80 | Passive Chance: 40%

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
  - **Base Familiars:** % Chance to gain an extra essence based on the **Mode**.
  - **Arcane Familiars:**
    - Higher % Chance (+10% flat) to trigger passives.
    - **Temporal Anchor:** If any player in the guild has an active Arcane familiar, all spawns in that server stay active for an additional **+15 seconds**.
  - **Restless Familiars:**
    - **Soul Anchor:** If a Restless familiar's resonance is active in the server, any spirit that is about to fade has a **20-50% chance** (by rarity) to be anchored, staying for an additional **+30 seconds**.
- **Resonance (Activation):** Passives are manually enabled using **`/familiar [name]`**:
  - Click **`Ignite Resonance`** to enable passives for **4 hours**.
  - Can be ignited **once per day** per familiar.
  - **Unlimited Triggers:** No limit on how many times the passive can trigger during the 4-hour window.
- **Resonance Modes:**
  - **ECHO (Default):** The familiar doubles the essence type you just captured (e.g., Fire familiar gives an extra Fire essence).
  - **PULSE:** The familiar transmutes the energy into a **random different** element (e.g., Fire familiar gives an extra Water essence).

## 🍂 Releasing
If your inventory or stable is full, you can release items to make room. Releasing triggers a **Resonance Surge**—a series of immediate spawns in the current channel.
- **Rules:** The player who releases the item **cannot** capture the resulting spawns.
- **Spirits:** 
  - 30% chance to respawn the spirit.
  - 70% chance to splinter into **3 matching Essences**, spawned 5 seconds apart.
- **Familiars:** 
  - Triggers a **Prismatic Burst**: Spawns the original Spirit **AND** **5 random Essences**, spawned 4-6 seconds apart.

**Commands:**
- `/release-spirit [name]`: Permanently removes a spirit from your inventory.
- `/release-familiar [name]`: Permanently removes a familiar from your stable.

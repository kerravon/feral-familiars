# 🎮 Gameplay Mechanics

## 🌌 Spawning System
Spawns occur periodically (Configurable via `SPAWN_INTERVAL_SECONDS`) in active channels.

### Dynamic Spawn Chance
The probability of a spawn is influenced by channel activity and a pity system:
- **Base Chance:** 15-25% (Configurable).
- **Activity Bonus (Heat):** Each message sent in the channel increases the chance of the next spawn by **+0.5%** (Max +20%).
- **Pity Bonus:** Every time the spawn clock ticks and NO item appears, the chance for the next tick increases by **+2%**.
- **Reset:** Both bonuses reset to 0 immediately after a successful spawn.

### Types of Encounters
- **Essences (80%):** 
  - **Base Elements:** Earth, Wind, Fire, Water (Equal spawn weight).
  - **Special:** Arcane (Rare - ~12% spawn weight).
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
- **Rules:**
  - **First Response:** The first player to type the keyword correctly wins the encounter.
  - **Anti-Macro:** A delay is enforced (default 1s) after a spawn before capture is possible.
  - **Expiration:** Encounters fade after a few seconds (default 45s).

## 🟢 Active Familiars
Equipping a familiar using `/summon` makes it your active companion. 
- **Stable Limit:** You can hold a maximum of **3** familiars by default.

## 📈 Familiar Leveling
Familiars grow in power as you interact with them. A higher level increases the success rate of their passive effects and unlocks new resonance modes.

### Gaining Experience (XP)
- **Binding:** Capturing an item while a familiar is **summoned** grants XP.
  - Standard Capture: **+5 XP**
  - Matching Element Capture: **+10 XP**
- **Feeding:** Use the `/feed` command to burn excess essences for rapid XP gain.
  - Matching Essence: **10 XP** per essence.
  - Arcane Essence: **20 XP** per essence.
  - Different Essence: **2 XP** per essence.

### Progression & Unlocks
| Level | Unlock / Milestone |
| :--- | :--- |
| **1** | **ECHO Mode** (Standard duplication) |
| **2-4** | Permanent +0.5% to +2.0% trigger chance bonus. |
| **5** | **PULSE Mode** (Transmute energy into random elements) |
| **6-7** | Permanent +0.5% to +2.0% trigger chance bonus. |
| **8** | **ATTRACT Mode** (Focus on a specific element via `/set-attract`) |
| **9** | Permanent +0.5% to +2.0% trigger chance bonus. |
| **10** | **MAX LEVEL** (Final growth roll) |

### Passive Resonance
- **Activation:** Passives are manually enabled using **`/familiar [name]`**:
  - Click **`Ignite Resonance`** to enable passives for **4 hours**.
  - **Global Limit:** You can ignite resonance **2 times per day** across your entire stable.
  - **Unlimited Triggers:** No limit on how many times the passive can trigger during the 4-hour window.
- **Unique Passives:**
  - **Arcane Familiars:** +10% flat bonus to trigger passives. **Temporal Anchor:** If ignited, all spawns in the server stay active for an additional **+15 seconds**.
  - **Restless Familiars:** **Soul Anchor:** If ignited, expiring spirits have a **20-50% chance** to stay for an additional **+30 seconds**.
- **Resonance Modes:**
  - **ECHO (Level 1):** Doubles captures that **match the familiar's element**. (Arcane doubles all elements).
  - **PULSE (Level 5):** Transmutes the energy into a **random different** element.
  - **ATTRACT (Level 8):** Targets a **specific element** of your choice.

## 🤝 Social & The Well
- **The Well of Souls:** All ritual fees are collected into a community pot.
- **Overflow Surge:** When the Well hits its threshold (1,000 essences), it triggers 8 rapid spawns for everyone.
- **Commands:**
  - `/vault`: View current Well progress.
  - `/donate`: Manually contribute essences to the Well.
  - `/bestow`: Gift items to other players (3% tax to the Well).
  - `/transmute`: Trade items with other players (3% tax to the Well).

## 🍂 Releasing
If your inventory is full, you can release items to trigger a **Resonance Surge** (3-5 immediate spawns). The releaser is blacklisted from these spawns.

## 📜 Guidance
- **/help**: Use this command at any time for an interactive guide to all game systems.
- **Onboarding:** Look for helpful tips in chat after your first capture or ritual success!

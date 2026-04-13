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
  - **Essences:** Max **500** per type (Configurable via `MAX_ESSENCES`).
  - **Spirits:** Max **5** in inventory (Configurable via `MAX_SPIRITS`).
- **Rules:**
  - **First Response:** The first player to type the keyword correctly wins the encounter.
  - **Anti-Macro:** A delay is enforced (default 1s, configurable via `ANTI_MACRO_DELAY_SECONDS`) after a spawn before capture is possible.
  - **Expiration:** Encounters fade after a few seconds (default 45s, configurable via `CAPTURE_WINDOW_SECONDS`).

## 🟢 Active Familiars
Equipping a familiar using `/summon` makes it your active companion. 
- **Stable Limit:** You can hold a maximum of **3** familiars (Default, configurable via `DEFAULT_STABLE_LIMIT`).

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

- **Passive Bonuses:**
  - **Base Familiars:** % Chance to gain an extra essence based on the **Mode**.
  - **Arcane Familiars:**
    - Higher % Chance (+10% flat) to trigger passives.
    - **Temporal Anchor:** If any player in the guild has an active Arcane familiar, all spawns in that server stay active for an additional **+15 seconds**.
  - **Restless Familiars:**
    - **Soul Anchor:** If a Restless familiar's resonance is active in the server, any spirit that is about to fade has a **20-50% chance** (by rarity) to be anchored, staying for an additional **+30 seconds**.
- **Resonance (Activation):** Passives are manually enabled using **`/familiar [name]`**:
  - Click **`Ignite Resonance`** to enable passives for **4 hours**.
  - **Global Limit:** You can ignite resonance **2 times per day** across your entire stable.
  - Can be ignited **once per day** per specific familiar.
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

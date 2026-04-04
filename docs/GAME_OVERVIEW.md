# 🐾 Feral Familiars: Master Game Overview

Feral Familiars is a social creature-collection and resource-management game played entirely within Discord. Players act as mystical binders who capture raw elemental energy (**Essences**) and wandering souls (**Spirits**) to perform ancient **Rituals**, creating permanent, unique **Familiars** with passive powers.

---

## 🌀 Core Mechanics

### 1. The Spawning System (The Pulse)
The game operates on a rhythmic "Pulse" that checks for spontaneous encounters.
*   **Natural Spawns:** Every **2 minutes**, there is a **15% chance** (default) for an item to appear in an active channel.
*   **The Wait:** Items remain active for **~45 seconds** before fading.
*   **Temporal Anchor:** If any player has an active **Arcane Familiar** summoned, the timer increases to **60 seconds** for everyone in the server.
*   **Visual Feedback:** When an item fades, it turns into a dark grey "Faded" placeholder. When bound, it shows a "Bound" version of the artwork.

### 2. The Capture System (Binding)
Unlike most bots, Feral Familiars requires active attention via keywords.
*   **Essences:** Type `bind` to capture.
*   **Spirits:** Type `bind spirit` to capture.
*   **Anti-Macro:** A **1-second delay** is enforced. Attempting to bind instantly after a spawn will fail.
*   **Competitive:** Only the **first** person to correctly type the keyword wins the item.

---

## 🎒 Items & Ingredients

### Essences (80% Spawn Rate)
Essences are the "fuel" for rituals and the "currency" for social taxes.
*   **Base Elements (22% weight each):** Earth, Wind, Fire, Water.
*   **Special (12% weight):** Arcane (Used for advanced rituals and paying taxes).

### Spirits (20% Spawn Rate)
Spirits are the "core" of a familiar. They possess a Type and a Rarity.
*   **Spirit Types:** Feline, Canine, Winged, Goblin, and **Restless** (Rare).
*   **Rarity Weights:**
    *   **Common:** 60%
    *   **Uncommon:** 25%
    *   **Rare:** 12%
    *   **Legendary:** 3%

---

## ✨ Familiars & Rituals

### The Creation Formula
Players use the `/ritual` command to combine ingredients into a permanent familiar.
*   **Standard Recipe:** 1 Spirit + X matching Essences.
*   **Restless Recipe:** 1 Restless Spirit + X matching Essences + **Arcane Essence Infusion** (5-25 based on rarity).

**Cost Table (Essences):**
| Rarity | Base Cost | Arcane Bonus (Restless only) |
| :--- | :--- | :--- |
| **Common** | 10 | +5 |
| **Uncommon** | 20 | +10 |
| **Rare** | 40 | +15 |
| **Legendary** | 80 | +25 |

### Dynamic Naming
Familiars are named based on their ingredients: **`[Essence Adjective]` + `[Spirit Noun]`**.
*   *Example:* A Legendary Fire Canine might be named **"Inferno Alpha-Predator."**
*   *Example:* A Common Arcane Restless might be named **"Mystic Wisp."**

---

## 🔥 Passive Powers (Resonance)

### Manual Activation
Passives are not active 24/7. A player must **summon** a familiar and then **ignite its resonance**.
*   **Method:** `/familiar [name]` -> **Ignite Resonance**.
*   **Duration:** **4 Hours**.
*   **Limits:** Players can ignite resonance **2 times per day** across their entire stable.
*   **Summon Swap:** Summoning a different familiar immediately ends the active resonance of the previous one.

### Passive Effects
*   **ECHO Mode (Default):** A % chance to get an extra essence of the **same type** when you bind one.
*   **PULSE Mode:** A % chance to get an extra essence of a **random different** element.
*   **Arcane Bonus:** Arcane familiars can double **ANY** type and have a **+10% flat bonus** to trigger chances.
*   **Soul Anchor (Restless only):** If a Restless familiar is resonating, there is a **20-50% chance** to save a fading spirit for the server, extending its life by 30 seconds.

**Trigger Chances (By Rarity):**
*   **Common:** 8% | **Uncommon:** 15% | **Rare:** 25% | **Legendary:** 40%

---

## 🕯️ Spectral Incense (Lures)
Players can burn stored minutes to bypass the random spawn timer.
*   **Essence Incense:** 100% Essence spawn every 60s.
*   **Spirit Incense:** 100% Spirit spawn every 60s.
*   **Pure Incense:** 100% spawn of a **specifically chosen element** every 60s.

---

## 🤝 Social & Cleanup Systems

### Social Taxes
*   **Gifting (`/bestow`):** Sender pays a 2% essence fee (or spirit fee based on rarity).
*   **Trading (`/transmute`):** Recipient pays a 5% essence fee (or spirit fee based on rarity).

### Resonance Surges (Releasing)
Releasing items isn't just deletion; it creates a server-wide event.
*   **Spirit Release:** 30% chance to respawn the spirit / 70% chance to spawn 3 essences.
*   **Familiar Release:** Spawns the original spirit **and** 5 random essences in a series.
*   **The Catch:** The player who released the item is blacklisted from capturing the resulting spawns.

---

## 🛠️ Command List Reference

| Command | Usage |
| :--- | :--- |
| `/inventory` | View loot, spirits, and stored Incense minutes. |
| `/familiars` | View your stable, status, and resonance timers. |
| `/familiar [name]` | Open a familiar card to Ignite Resonance or Switch Mode. |
| `/summon [name]` | Set your active companion. |
| `/ritual` | Create a new familiar. |
| `/incense` | Burn stored time to attract specific energies. |
| `/transmute` | Trade with another player using a secure UI. |
| `/bestow` | Gift items to another player. |
| `/release-spirit` | Delete a spirit to trigger a Resonance Surge. |
| `/release-familiar`| Delete a familiar to trigger a Prismatic Surge. |

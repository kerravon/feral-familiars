# 🐾 Feral Familiars: Master Game Overview

Feral Familiars is a social creature-collection and resource-management game played entirely within Discord. Players act as mystical binders who capture raw elemental energy (**Essences**) and wandering souls (**Spirits**) to perform ancient **Rituals**, creating permanent, unique **Familiars** with passive powers.

---

## 🌀 Core Mechanics

### 1. The Spawning System (The Pulse)
The game operates on a rhythmic "Pulse" that checks for spontaneous encounters.
*   **Dynamic Spawns:** Spawns occur periodically (Configurable via `SPAWN_INTERVAL_SECONDS`).
*   **The Heat System:** Chat activity increases the spawn chance by **+0.5% per message** (Max +20%).
*   **Pity System:** Every failed spawn check increases the next check's chance by **+2%**.
*   **Temporal Anchor:** If an **Arcane Familiar** is resonating, spawns stay active for an additional **+15 seconds**.

### 2. The Capture System (Binding)
Capturing items requires active attention and quick typing.
*   **Keywords:** Type `bind` for essences or `bind spirit` for spirits.
*   **Competitive:** Only the **first** person to correctly type the keyword wins the item.
*   **Anti-Macro:** A **1-second delay** is enforced to prevent automated captures.

---

## 🎒 Items & Ingredients

### Essences (80% Spawn Rate)
Essences are the fuel for rituals and the currency for social taxes.
*   **Elements:** Earth, Wind, Fire, Water, and the rare **Arcane**.
*   **Inventory Cap:** 500 per type (Configurable).

### Spirits (20% Spawn Rate)
Spirits are the core of a familiar. They possess a Type and a Rarity.
*   **Types:** Feline, Canine, Winged, Goblin, and the rare **Restless**.
*   **Rarity:** Common (60%), Uncommon (25%), Rare (12%), Legendary (3%).

---

## ✨ Familiars & Leveling

### The Creation Formula
Players use the `/ritual` command to combine 1 Spirit with matching Essences.
*   **Costs:** Common (10), Uncommon (20), Rare (40), Legendary (80).
*   **Restless:** Requires an additional infusion of **Arcane Essence** (5-25).

### Progression
Familiars gain **XP** through binding items or being **fed** essences.
*   **Max Level:** 10.
*   **Growth Rolls:** Each level grants a permanent **+0.5% to +2.0%** bonus to passive trigger chances.
*   **Unlocks:** New Resonance Modes unlock at Level 5 (**PULSE**) and Level 8 (**ATTRACT**).

---

## 🔥 Passive Powers (Resonance)

Passives are activated via the `/familiar` command and last for **4 hours**.
*   **ECHO (Lv. 1):** Chance to double matching captured essences.
*   **PULSE (Lv. 5):** Chance to gain a random different essence.
*   **ATTRACT (Lv. 8):** Chance to gain a specific, chosen element.
*   **Soul Anchor (Restless only):** Resonating Restless familiars have a chance to save fading spirits for the server.

---

## 🤝 Social & The Well

### The Well of Souls
All ritual fees from gifting and trading are collected into a community pot.
*   **Surge Trigger:** When the Well reaches **1,000 essences**, it triggers a **Prismatic Surge** (8 rapid spawns).
*   **Tax Rate:** Standardized **3% fee** on all essences gifted or traded.

### Resonance Surges (Releasing)
Releasing items triggers immediate spawns for the server. The releaser is blacklisted from these spawns.

---

## 🛠️ Command List Reference

| Command | Usage |
| :--- | :--- |
| `/help` | Interactive guide to all game systems. |
| `/inventory` | View loot, spirits, and stored Incense minutes. |
| `/familiars` | View your stable, status, and levels. |
| `/familiar [id]` | Manage a familiar, Ignite Resonance, or Switch Mode. |
| `/summon [id]` | Set your active companion. |
| `/ritual` | Create a new familiar. |
| `/feed` | Burn essences to give XP to your familiar. |
| `/vault` | Check the progress of the Well of Souls. |
| `/donate` | Manually contribute essences to the Well. |
| `/transmute` | Trade with another player. |
| `/bestow` | Gift items to another player. |
| `/ritual-guide` | Quick reference for costs and rules. |

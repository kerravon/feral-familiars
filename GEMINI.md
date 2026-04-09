# Feral Familiars: Technical & Design Overview

**Repository:** [kerravon/feral-familiars](https://github.com/kerravon/feral-familiars)

This document serves as the foundational reference for the "Feral Familiars" Discord bot. It captures the current state of development, architectural decisions, and the long-term vision for the game.

---

## 🌌 Core Concept
A Discord-based creature collection and ritual game where players capture mystical **Essences** and **Spirits** from chat to create unique **Familiars**.

---

## 🛠 Tech Stack
*   **Language:** Python 3.12
*   **Library:** discord.py (Latest with Slash Commands & Interactive UI)
*   **Database:** PostgreSQL (via SQLAlchemy 2.x Async)
*   **Deployment:** Docker + docker-compose
*   **ORM:** Declarative Base with Mapped Type Hints

---

## 🧪 Game Mechanics

### 1. Spawning System
*   **Dynamic Frequency:** Spawns occur on a rhythmic "Pulse" (Configurable via `SPAWN_INTERVAL_SECONDS`).
*   **Activity Bonus (Heat):** Active channels gain a "Heat" bonus. Each message increases the spawn chance by +0.5% (Max +20% bonus).
*   **Pity System:** Each failed spawn check increases the next check's chance by +2% bonus.
*   **Resets:** Both Heat and Pity reset to 0 upon a successful spawn.
*   **Activation:** Admins use `/toggle-channel` to enable/disable spawns.
*   **Incense (Lures):** Players can ignite **Spectral Incense** to guarantee spawns for a set duration.
    *   **Essence Incense:** 100% Essence spawn every 60s.
    *   **Spirit Incense:** 100% Spirit spawn every 60s.
    *   **Pure Incense:** 100% spawn of a **specifically chosen element** every 60s.
*   **Types:** 
    *   **Essences (80%):** Earth, Wind, Fire, Arcane, Water.
    *   **Spirits (20%):** Feline, Canine, Winged, Goblin, **Restless** (Rare).
*   **Rarity (Spirits only):** Common (60%), Uncommon (25%), Rare (12%), Legendary (3%).

### 2. Capture System (Keyword-Based)
*   **Keywords:** `bind` (essences) and `bind spirit` (spirits).
*   **Debug Command:** `!testspawn [essence/spirit] [subtype] [rarity]` (Admins only).
*   **Inventory Limits:**
    *   **Essences:** Cap of 500 (Configurable via `MAX_ESSENCES`).
    *   **Spirits:** Cap of 5 (Configurable via `MAX_SPIRITS`).
    *   **Familiars:** Initial stable limit of 3 (Configurable via `DEFAULT_STABLE_LIMIT`).
*   **Rules:**
    *   Anti-macro delay (Default 1s, configurable via `ANTI_MACRO_DELAY_SECONDS`).
    *   First-valid-message wins.
    *   Capture window: ~45s (Configurable via `CAPTURE_WINDOW_SECONDS`, extended to **60s** if an Arcane familiar is active).
    *   Visual Feedback: Original spawn message edits to show capturer and "Bound" artwork. Faded placeholder if missed.

### 3. Ritual System (Creation)
*   **Standard Formula:** 1 Spirit + X matching Essences = 1 Familiar.
*   **Restless Formula:** 1 Restless Spirit + X matching Essences + **Arcane Infusion** (+5 to +25).
*   **Costs:** Common (10), Uncommon (20), Rare (40), Legendary (80).
*   **Naming:** Dynamic word banks based on Type + Rarity (e.g., "Tectonic Wraith-Lord").

### 4. Passive Resonance (Power)
*   **Activation:** Must manually ignite via **/familiar [name]**.
*   **Duration:** **4 Hours** (Unlimited triggers during window).
*   **Player Limit:** **2 ignites per day** total across all familiars.
*   **Modes:**
    *   **ECHO:** Chance to double matching captured essence.
    *   **PULSE:** Chance to gain random different essence.
*   **Unique Passives:**
    *   **Arcane:** Universal Resonance (doubles ANY type) + Server Timer Bonus.
    *   **Restless:** Soul Anchor (% chance to save fading spirits for the server).

### 5. Social Systems
*   **The Well of Souls (Guild Pot):** 
    *   Taxes from gifting and trading are collected into a community pot (viewable via `/vault`).
    *   **Overflow Surge:** When the Well reaches its threshold (Default 1000 essences), it triggers a massive, server-wide Prismatic Surge (8 rapid spawns).
*   **`/bestow` (Gift):** 
    *   **Limit:** 1 Spirit / 50 Essences per day (Reset Midnight UTC).
    *   **Tax:** **Sender** pays 3% fee (Min 1) to the Well of Souls.
*   **`/transmute` (Trade):** 
    *   **UI:** "Cat Bot" style interactive buttons and modals.
    *   **Tax:** **Recipient** pays 3% essence fee (Min 1) and rarity-based spirit fee to the Well of Souls.
*   **Resonance Surges (Releasing):** Releasing items creates immediate spawns for the server. Releaser is blacklisted from the surge.

---

## 📁 Project Structure
```
bot/
├── main.py              # Entry point, Events, & Background Tasks
├── db.py                # Database connection & Session management
├── migrate.py           # Manual migration script for DB updates
├── commands/            # Slash Command Cogs (With Autocomplete for Spirits/Familiars)
├── models/              # Database Schemas (User, Essence, Spirit, Familiar, Encounter, Config, Trade)
├── services/            # Business Logic (Inventory, Ritual, Encounter, Bestow, Transmute, Passive)
├── utils/               
│   ├── constants.py     # Naming banks, Costs, & Image URLs
│   ├── config.py        # Centralized environment variable management
│   └── ui.py            # Interactive Discord Views and Modals
└── tools/               # Developer utility scripts (Asset optimization, Prompting, etc.)
```

---

## 🛠 Development Guidelines
*   **Git:** Always stage, commit, and push changes after completing a batch of requested modifications.
*   **Documentation:** Keep `GEMINI.md` and all files in `docs/` updated immediately to reflect any architectural, mechanical, or configuration changes.
*   **Testing:** Verify changes via available test suites or manual reproduction before committing.

---

## 🔮 Future Vision (Phase 2+)
*   **Monthly Missions:** A "Battlepass" style system where players complete challenges to earn rewards like Incense.
*   **Familiar Leveling:** Active familiars grow in power, increasing their passive trigger chances.
*   **Leaderboards:** Rankings for top collectors and most active hunters.
*   **Advanced Rituals:** Recipes for even more unique familiar types.

---

## 📝 Current Action Items
- [ ] Finalize artwork for Arcane essence and all Spirit types.
- [ ] Implement "Leveling" logic for active familiars.
- [ ] Add a leaderboard for top collectors.

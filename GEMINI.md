# Feral Familiars: Technical & Design Overview

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
*   **Frequency:** 25% chance every 2 minutes in active channels.
*   **Activation:** Admins use `/toggle-channel` to enable/disable spawns.
*   **Types:** 
    *   **Essences (80%):** Earth, Wind, Fire, Arcane, Water.
    *   **Spirits (20%):** Feline, Canine, Winged, Goblin.
*   **Rarity (Spirits only):** Common (60%), Uncommon (25%), Rare (12%), Legendary (3%).

### 2. Capture System (Keyword-Based)
*   **Keywords:** `bind` (essences) and `bind spirit` (spirits).
*   **Debug Command:** `!testspawn [essence/spirit] [subtype] [rarity]` (Admins only).
*   **Rules:**
    *   1-second anti-macro delay.
    *   First-valid-message wins.
    *   Capture window scales by rarity (~35s to ~50s).
    *   Visual Feedback: Original spawn message edits to show capturer and "Bound" artwork.

### 3. Ritual System (Creation)
*   **Formula:** 1 Spirit + X matching Essences = 1 Familiar.
*   **Costs:** Common (10), Uncommon (20), Rare (40), Legendary (80).
*   **Naming:** Dynamic word banks based on Type + Rarity (e.g., "Tectonic Alpha-Predator").

### 4. Social Systems
*   **`/bestow` (Gift):** 
    *   **Limit:** 1 Spirit / 50 Essences per day (Reset Midnight UTC).
    *   **Tax:** **Sender** pays 2% fee (Min 1).
*   **`/transmute` (Trade):** 
    *   **UI:** "Cat Bot" style interactive buttons and modals.
    *   **Tax:** **Recipient** pays 5% essence fee or rarity-based spirit fee.
*   **`/incense` (Lure):** 
    *   **Hero Mechanic:** High-intensity spawn window for the whole channel.
    *   **Storage:** Bought/earned in minute-blocks and burned as needed.

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
*   **Git:** Always stage and commit changes after completing a batch of requested modifications.
*   **Documentation:** Ensure `GEMINI.md` and related files in `docs/` are updated immediately whenever architectural or mechanical changes are made.
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

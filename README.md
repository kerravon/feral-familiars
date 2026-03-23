# 🐾 Feral Familiars

A mystical Discord creature-collection game. Capture essences and spirits, perform ancient rituals, and build your stable of unique familiars.

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- PostgreSQL
- Docker (optional)

### Installation
1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd feral-familiars
    ```
2.  **Environment Setup:**
    ```bash
    cp .env.example .env
    # Edit .env with your DISCORD_TOKEN and other settings
    ```
3.  **Run with Docker (Recommended):**
    ```bash
    docker-compose up --build
    ```
    *Or run manually:*
    ```bash
    pip install -r requirements.txt
    python bot/migrate.py
    python -m bot.main
    ```

## 🎮 How to Play
1.  **Activate Spawns:** An admin must use `/toggle-channel` to enable encounters.
2.  **Capture:** 
    *   When an **Essence** appears, type `bind`.
    *   When a **Spirit** appears, type `bind spirit`.
3.  **Ritual:** Use `/ritual spirit_id essence_type` to create your familiar.
4.  **Stable:** Use `/familiars` to see your collection and `/equip` to set an active familiar.

## 🛠 Tech Stack
- **Framework:** `discord.py`
- **Database:** `PostgreSQL` + `SQLAlchemy` (Async)
- **Migrations:** `Alembic`
- **Environment:** `Docker`

## 📖 Documentation
Detailed guides can be found in the [docs/](./docs) directory:
- [Gameplay Mechanics](./docs/GAMEPLAY.md)
- [Rituals & Taxes](./docs/RITUALS.md)
- [Development Guide](./docs/DEVELOPMENT.md)

# VisionCrafterAI Backend (Local Development)

## Prerequisites
- Python 3.12
- PostgreSQL (local)
- Create database `visioncrafter` and a user with privileges.

## Setup
```bash
cd visioncrafterai_be
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: set DATABASE_URL to local Postgres
```

## Initialize DB
```bash
python -m app.init_db
```
Runs [`app.database.create_db_and_tables`](visioncrafterai_be/app/database.py) via [`app.init_db.init_db`](visioncrafterai_be/app/init_db.py).

## Run API
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Entrypoint is [`app.main.app`](visioncrafterai_be/app/main.py).

## Reset DB (local)
```bash
./scripts/reset_database.sh
```
Calls [`scripts/clear_database.py`](visioncrafterai_be/scripts/clear_database.py).
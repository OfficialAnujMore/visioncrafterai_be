# VisionCrafterAI — Backend

## Tech Stack

- **Python 3.12+** with **FastAPI**
- **SQLAlchemy** (async) with **SQLModel** ORM
- **PostgreSQL** via Supabase (async driver: `asyncpg`)
- **Alembic** for database migrations
- **python-jose** for JWT authentication
- **Uvicorn** ASGI server

## Commands

```bash
# Run dev server
uvicorn app.main:app --reload
# Runs on http://localhost:8000

# Database migrations
alembic upgrade head          # Apply all migrations
alembic revision --autogenerate -m "description"  # Create new migration

# Tests
cd testOutputs && pytest

# Dependencies
pip install -r requirements.txt
```

## Directory Structure

```
app/
├── main.py           # FastAPI app init, CORS, exception handlers, startup
├── config.py         # Pydantic Settings (reads .env)
├── database.py       # Async SQLAlchemy engine and session factory
├── init_db.py        # DB table creation script
├── models/           # SQLModel ORM models (user.py, project.py)
├── routers/          # API route handlers (auth.py, project.py, imagekit.py)
├── schemas/          # Pydantic request/response schemas (auth, project, common)
├── utils/            # Utilities (security.py for JWT/auth, imagekit.py for file ops)
└── locale/           # i18n message strings

alembic/              # Migration scripts
testOutputs/tests/    # Test suite (pytest + httpx async tests)
```

## Database Schema

**`user` table**
- `id`, `google_id` (unique), `email` (unique), `name`, `picture`
- `is_active`, `created_at`, `last_login`
- Has many `projects`

**`projects` table**
- `id`, `file_id` (ImageKit), `user_id` (FK → user)
- `title`, `project_url`, `thumbnail_url`
- `width`, `height`, `file_type` (image/video)
- `canvas_state` (JSON string — full Fabric.js canvas state)
- `created_at`, `updated_at`

## API Endpoints

### Auth (`/auth`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/google` | Google OAuth login → creates user + sets JWT cookies |
| POST | `/auth/refresh` | Refresh access token using refresh token cookie |
| POST | `/auth/logout` | Clear auth cookies |

### Projects (`/api/projects`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/projects/create` | Create new project |
| GET | `/api/projects/{project_id}` | Get project (ownership verified) |
| GET | `/api/projects/user/{user_id}` | List user's projects |
| PUT | `/api/projects/{project_id}` | Full update |
| PATCH | `/api/projects/{project_id}` | Partial update (e.g., canvas_state) |
| DELETE | `/api/projects/{file_id}` | Delete project + ImageKit file |

### ImageKit (`/api/imagekit`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/imagekit/auth` | Get upload auth params (token, signature, expire) |

### Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Service status check |

## Authentication Flow

1. Frontend sends Google OAuth token to `POST /auth/google`
2. Backend validates token with Google's API
3. Creates or updates user in DB
4. Returns JWT access token (15 min) + refresh token (7 days) as HttpOnly cookies
5. Protected routes use `get_current_user_from_cookie()` dependency
6. Each project endpoint verifies the requesting user owns the resource

## Response Format

All API responses follow this structure:
```json
{"success": true, "message": "...", "data": {...}}
{"success": false, "message": "...", "error": "...", "statusCode": 400}
```

Implemented via `ApiResponse[T]` generic Pydantic model in `schemas/common.py`.

## Key Patterns

- **Async everywhere** — database sessions, HTTP calls (httpx), all route handlers
- **Dependency injection** — `Depends()` for DB sessions and auth
- **Ownership checks** — project routes verify `user_id` matches the authenticated user
- **ImageKit integration** — files stored/renamed/deleted via ImageKit API in `utils/imagekit.py`
- **Cookie security** — `httponly=True`, `secure=True`, `samesite="none"`

## Key Files

| File | Purpose |
|------|---------|
| `app/main.py` | App entry point, middleware, exception handlers |
| `app/utils/security.py` | JWT creation/verification, Google token validation |
| `app/utils/imagekit.py` | ImageKit API wrapper (upload auth, rename, delete) |
| `app/routers/project.py` | Project CRUD with ownership verification |
| `app/schemas/common.py` | Generic `ApiResponse[T]` wrapper |
| `app/database.py` | Async engine and session factory |

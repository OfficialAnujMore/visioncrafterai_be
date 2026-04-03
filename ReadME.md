# VisionCrafterAI Backend API

FastAPI-based backend service for VisionCrafterAI, a canvas editor platform for creating and managing images and videos with integrated asset management.

## 📋 Project Overview

VisionCrafterAI Backend is a modern, async-first REST API built with FastAPI that provides:
- **User Authentication**: Google OAuth 2.0 integration with JWT tokens
- **Project Management**: CRUD operations for canvas editing projects
- **File Management**: Integration with ImageKit for centralized asset storage
- **Real-time Capabilities**: WebSocket-ready architecture with async SQLAlchemy ORM
- **Security**: CORS protection, secure cookie handling, authorization checks

## 🛠 Technical Stack

| Layer | Technology |
|-------|-----------|
| **Framework** | FastAPI 0.100+ |
| **Server** | Uvicorn (ASGI) |
| **Database** | PostgreSQL 12+ with SQLAlchemy ORM |
| **Async Driver** | asyncpg, aiosqlite |
| **Authentication** | Google OAuth 2.0, JWT (python-jose) |
| **File Management** | ImageKit API (imagekitio) |
| **Validation** | Pydantic v2 |
| **Testing** | pytest, pytest-asyncio, httpx |
| **Environment** | python-dotenv, pydantic-settings |

## 📦 Prerequisites

- **Python**: 3.12 or higher
- **PostgreSQL**: 12+ (for production/local dev)
- **Git**: For version control
- **Virtual Environment**: Python venv or similar

## 🚀 Quick Start

### 1. Clone and Setup Environment

```bash
cd visioncrafterai_be
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# Database
DATABASE_URL=postgresql+asyncpg://USERNAME:PASSWORD@localhost:5432/visioncrafter

# JWT Configuration
JWT_SECRET_KEY=your-secure-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Google OAuth (from Google Cloud Console)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com

# Application
APP_NAME=VisionCrafterAI
DEBUG=false
CORS_ALLOW_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 3. Initialize Database

```bash
# Create database and tables
python -m app.init_db
```

This script:
- Creates tables from SQLAlchemy models
- Sets up required indexes
- Initializes schema (runs [`app.database.create_db_and_tables`](app/database.py))

### 4. Run Development Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Access the API:**
- API Server: `http://localhost:8000`
- Interactive Docs (Swagger UI): `http://localhost:8000/docs`
- Alternative Docs (ReDoc): `http://localhost:8000/redoc`

## 🧪 Testing

### Running Tests

The project includes comprehensive test coverage with 48+ unit tests organized by module.

```bash
# Run all tests
cd testOutputs
pytest -v

# Run specific test category
pytest -k "test_auth" -v          # Authentication tests
pytest -k "test_create" -v        # CRUD creation tests
pytest -k "test_integration" -v   # Integration tests
pytest -k "test_edge_cases" -v    # Edge case validation

# Run with coverage report
pytest --cov=app --cov-report=html

# Run single test file
pytest tests/test_auth.py -v
```

### Test Structure

```
testOutputs/
├── pytest.ini              # Pytest configuration
├── tests/
│   ├── test_auth.py       # Authentication endpoints (8 tests)
│   ├── test_projects.py   # Project CRUD operations (16 tests)
│   ├── test_imagekit.py   # ImageKit integration (2 tests)
│   ├── test_root.py       # Root status endpoint (1 test)
│   ├── test_edge_cases.py # Input validation & XSS prevention (5 tests)
│   ├── test_integration.py # Full workflow tests (1 test)
│   └── test_performance.py # Performance benchmarks (1 test)
```

### Test Features

- **48+ Comprehensive Unit Tests**
- **Async Testing**: Uses `httpx.AsyncClient` for testing async endpoints
- **Database Isolation**: In-memory SQLite for test isolation
- **Mocking**: External services (Google OAuth, ImageKit) are mocked
- **Authorization Checks**: Validates ownership and permissions
- **Security Testing**: XSS prevention, CSRF protection validation
- **Performance Testing**: Tests for concurrent operations

## 📁 Project Structure

```
visioncrafterai_be/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management (pydantic-settings)
│   ├── database.py          # SQLAlchemy setup & session management
│   ├── init_db.py           # Database initialization script
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── project.py
│   │   └── ...
│   ├── routers/             # API route handlers
│   │   ├── auth.py          # Google OAuth & JWT authentication
│   │   ├── projects.py      # Project CRUD operations
│   │   └── imagekit.py      # ImageKit file management
│   ├── schemas/             # Pydantic request/response models
│   │   ├── auth.py
│   │   ├── project.py
│   │   └── common.py
│   ├── services/            # Business logic layer
│   │   ├── auth_service.py
│   │   ├── project_service.py
│   │   └── imagekit_service.py
│   └── utils/               # Utility functions
│       ├── auth_utils.py
│       └── validators.py
├── scripts/
│   ├── reset_database.sh    # Reset DB (dev only)
│   └── clear_database.py    # Clear DB tables
├── testOutputs/             # Test suite
│   ├── pytest.ini
│   └── tests/
├── .env.example             # Environment variables template
├── requirements.txt         # Python dependencies
└── README.md
```

## 🔌 API Endpoints

### Authentication Routes (`/auth`)
- `POST /auth/google` - Google OAuth login
- `POST /auth/refresh` - Refresh JWT token
- `POST /auth/logout` - Logout (clear tokens)

### Projects Routes (`/projects`)
- `GET /projects` - List all user projects
- `GET /projects/{project_id}` - Get project details
- `POST /projects` - Create new project
- `PUT /projects/{project_id}` - Update project
- `DELETE /projects/{project_id}` - Delete project

### ImageKit Routes (`/imagekit`)
- `GET /imagekit/auth` - Get ImageKit authentication token
- `POST /imagekit/delete` - Delete image from ImageKit

### Root Route
- `GET /` - Check service status

## 🔐 Security Features

- **JWT Authentication**: 15-minute access tokens + 7-day refresh tokens
- **HttpOnly Cookies**: Tokens stored in secure, HttpOnly cookies
- **CORS Protection**: Configured allowed origins
- **SameSite Cookies**: Secure cookie handling with SameSite=None
- **Authorization**: Project ownership verification
- **Input Validation**: Pydantic schema validation for all inputs
- **XSS Protection**: HTML sanitization for user inputs

## 📊 Database Schema

Key tables:
- **users**: Google OAuth user data
- **projects**: Canvas editor projects with JSON canvas state
- **auth_sessions**: Active JWT tokens and refresh token tracking

## 🔧 Database Commands

### Initialize Database
```bash
python -m app.init_db
```

### Reset Database (Development Only)
```bash
./scripts/reset_database.sh
# or
python scripts/clear_database.py
```

### Create Migrations (Alembic)
```bash
# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## 📝 Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ | - | PostgreSQL connection string |
| `JWT_SECRET_KEY` | ✅ | - | Secret key for JWT signing |
| `ALGORITHM` | ✅ | HS256 | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ | 15 | Access token expiration |
| `REFRESH_TOKEN_EXPIRE_DAYS` | ❌ | 7 | Refresh token expiration |
| `GOOGLE_CLIENT_ID` | ✅ | - | Google OAuth client ID |
| `APP_NAME` | ❌ | VisionCrafterAI | Application name |
| `DEBUG` | ❌ | false | Debug mode |
| `CORS_ALLOW_ORIGINS` | ✅ | - | Comma-separated allowed origins |

## 🧵 Async Architecture

- **Async Database Access**: All DB operations use async SQLAlchemy with asyncpg
- **Async HTTP Requests**: External API calls use httpx.AsyncClient
- **Concurrent Request Handling**: Uvicorn with multiple worker threads
- **Non-blocking Operations**: All I/O operations are non-blocking

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Verify PostgreSQL is running
psql -U USERNAME -d visioncrafter -c "SELECT 1"

# Check DATABASE_URL format
postgresql+asyncpg://USERNAME:PASSWORD@HOST:PORT/DATABASE
```

### JWT Token Errors
- Ensure `JWT_SECRET_KEY` is set and consistent across restarts
- Check token expiration times in `.env`
- Verify CORS_ALLOW_ORIGINS includes your frontend URL

### Google OAuth Issues
- Verify `GOOGLE_CLIENT_ID` is correct from Google Cloud Console
- Ensure frontend callback URL is registered in OAuth application

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLAlchemy Async Guide](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [JWT Tokens](https://tools.ietf.org/html/rfc7519)
- [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)

## 📄 License

VisionCrafterAI Backend - Part of VisionCrafterAI Project
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.openapi.utils import get_openapi
from app.routers import auth_router, users_router
from app.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables on application startup
    print("🔄 Creating database tables...")
    await create_db_and_tables()
    print("✅ Database tables created successfully!")
    yield
    # Shutdown: Cleanup if needed
    print("👋 Shutting down application...")


app = FastAPI(
    title="VisionCrafterAI Backend",
    lifespan=lifespan,
    version="1.0.0",
    description="Backend API for VisionCrafterAI"
)

app.include_router(auth_router)
app.include_router(users_router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="VisionCrafterAI Backend",
        version="1.0.0",
        description="Backend API for VisionCrafterAI",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token"
        }
    }
    # Add security to protected endpoints
    openapi_schema["components"]["schemas"]["HTTPBearer"] = {
        "type": "object",
        "properties": {
            "scheme": {"type": "string"},
            "credentials": {"type": "string"}
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/")
def root():
    return {"service": "visioncrafterai_be", "status": "ok"}

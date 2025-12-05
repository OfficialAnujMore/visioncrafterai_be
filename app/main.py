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
    
    # Mark protected endpoints with security requirement
    protected_paths = [
        "/users/profile",
    ]
    
    for path in openapi_schema.get("paths", {}):
        if path in protected_paths:
            for method in openapi_schema["paths"][path]:
                if method in ["get", "put", "post", "delete"]:
                    if method in openapi_schema["paths"][path]:
                        openapi_schema["paths"][path][method]["security"] = [{"Bearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/")
def root():
    return {"service": "visioncrafterai_be", "status": "ok"}

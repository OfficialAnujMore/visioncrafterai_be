from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from contextlib import asynccontextmanager
from fastapi.openapi.utils import get_openapi
from app.routers import auth_router, users_router
from app.database import create_db_and_tables
from app.config import settings
from fastapi.middleware.cors import CORSMiddleware


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
    title=f"{settings.APP_NAME} Backend",
    lifespan=lifespan,
    version="1.0.0",
    description=f"Backend API for {settings.APP_NAME}"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom exception handler to ensure consistent error responses
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.detail,
            "statusCode": exc.status_code,
            "error": exc.detail
        },
    )


app.include_router(auth_router)
app.include_router(users_router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=f"{settings.APP_NAME} Backend",
        version="1.0.0",
        description=f"Backend API for {settings.APP_NAME}",
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
    return {"service": settings.APP_NAME, "status": "ok"}

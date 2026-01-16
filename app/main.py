from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from contextlib import asynccontextmanager
from app.routers import auth_router, project_router
from app.routers import imagekit
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
app.include_router(project_router)
app.include_router(imagekit.router)


@app.get("/")
def root():
    return {"service": settings.APP_NAME, "status": "ok"}

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException, RequestValidationError
from contextlib import asynccontextmanager
from app.routers import auth_router, project_router
from app.routers import imagekit
from app.database import create_db_and_tables
from app.config import settings
from app.schemas.common import ApiErrorResponse
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: optionally create tables (recommended only for local/dev)
    if settings.DB_CREATE_TABLES_ON_STARTUP:
        print("Creating database tables on startup...")
        try:
            await create_db_and_tables()
            print("Database tables created successfully")
        except Exception as exc:
            print(f"Startup database initialization failed: {exc}")
            if settings.DB_FAIL_FAST_ON_STARTUP_ERROR:
                raise
            print("Continuing startup because DB_FAIL_FAST_ON_STARTUP_ERROR is false")
    else:
        print("Skipping startup table creation; use Alembic migrations for schema changes")
    yield
    # Shutdown: Cleanup if needed
    print("Shutting down application...")


app = FastAPI(
    title=f"{settings.APP_NAME} Backend",
    lifespan=lifespan,
    version="1.0.0",
    description=f"Backend API for {settings.APP_NAME}"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom exception handler to ensure consistent error responses
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiErrorResponse(
            success=False,
            message=exc.detail,
            statusCode=exc.status_code
        ).model_dump()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ApiErrorResponse(
            success=False,
            message="Validation error",
            error=str(exc),
            statusCode=status.HTTP_422_UNPROCESSABLE_ENTITY
        ).model_dump()
    )


app.include_router(auth_router)
app.include_router(project_router)
app.include_router(imagekit.router)


@app.get("/")
def root():
    return {"service": settings.APP_NAME, "status": "ok"}

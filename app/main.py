from fastapi import FastAPI
from contextlib import asynccontextmanager
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
    lifespan=lifespan
)

app.include_router(auth_router)
app.include_router(users_router)


@app.get("/")
def root():
    return {"service": "visioncrafterai_be", "status": "ok"}

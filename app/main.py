from fastapi import FastAPI
from app.routers import auth_router, users_router

app = FastAPI(title="VisionCrafterAI Backend")

app.include_router(auth_router)
app.include_router(users_router)


@app.get("/")
def root():
    return {"service": "visioncrafterai_be", "status": "ok"}

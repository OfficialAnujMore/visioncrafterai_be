from fastapi import FastAPI
from app.routers import auth_router

app = FastAPI(title="VisionCrafterAI Backend")

@app.get("/")
def root():
    return {"service": "visioncrafterai_be", "status": "ok"}

app.include_router(auth_router)

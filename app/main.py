from fastapi import FastAPI

app = FastAPI(title="VisionCrafterAI Backend")

@app.get("/")
def root():
    return {"service": "visioncrafterai_be", "status": "ok"}

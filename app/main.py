from fastapi import FastAPI
from app.api.routes.health import router as health_router

app = FastAPI(
    title="medinyang-Agent",
    version="0.1.0",
    description="RAG-based medical consultation multi-agent system",
)

app.include_router(health_router)


@app.get("/")
def root():
    return {"service": "medinyang-Agent", "status": "ok"}

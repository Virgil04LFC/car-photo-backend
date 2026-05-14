import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import backgrounds, process

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title="Car Photo API",
    description="AI-powered car photo background replacement via Photoroom",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — open for now; lock to app domain when auth is added
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(process.router, tags=["Processing"])
app.include_router(backgrounds.router, tags=["Backgrounds"])


@app.get("/health", tags=["Meta"])
async def health() -> dict:
    """Liveness check — returns ok when the server is up."""
    return {"status": "ok", "version": app.version}

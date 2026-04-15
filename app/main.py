from fastapi import FastAPI

from app.api.routes_score import router as score_router
from app.api.routes_stats import router as stats_router
from app.api.routes_trials import router as trials_router
from app.api.routes_ui import router as ui_router
from app.core.config import get_settings
from app.core.logging import configure_logging

configure_logging()
settings = get_settings()

app = FastAPI(title=settings.project_name)
app.include_router(ui_router)
app.include_router(trials_router)
app.include_router(stats_router)
app.include_router(score_router)


@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {
        "status": "ok",
        "service": settings.project_name,
        "environment": settings.environment,
    }

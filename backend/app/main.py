from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api import health, cases, evidence, tracking, ai

settings = get_settings()

app = FastAPI(
    title="Alerta Cuenta API",
    description="Backend para la plataforma de orientación ciudadana ante fraude financiero.",
    version="0.1.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(cases.router, prefix="/api/cases", tags=["cases"])
app.include_router(evidence.router, prefix="/api/evidence", tags=["evidence"])
app.include_router(tracking.router, prefix="/api/tracking", tags=["tracking"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])

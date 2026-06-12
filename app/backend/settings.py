from __future__ import annotations

from dataclasses import dataclass
import os

from ai_real_estate_fund.production.settings import ProductionSettings


@dataclass(slots=True)
class Settings:
    app_name: str = "AI Real Estate Fund API"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    enable_demo_mode: bool = os.getenv("ENABLE_DEMO_MODE", "true").lower() == "true"
    production: ProductionSettings = ProductionSettings.from_env()


settings = Settings()

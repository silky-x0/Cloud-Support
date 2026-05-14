# pyrefly: ignore [missing-import]
from fastapi import FastAPI
from api.routes import router
from utils.logger import setup_logging


setup_logging()


app = FastAPI(
    title="CloudDash Customer Support API",
    version="1.0.0",
    description="Multi-agent AI support system for CloudDash SaaS platform.",
)

app.include_router(router)

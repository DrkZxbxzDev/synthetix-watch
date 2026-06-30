from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.scheduler import start_scheduler, stop_scheduler
from app.database.connection import init_db
from app.api.endpoints import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    start_scheduler(interval_minutes=5)
    yield
    stop_scheduler()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API de monitoreo QA automatizado con Playwright",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
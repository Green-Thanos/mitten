from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.core.config import settings
from app.api.v1.router import api_v1_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # init resources if needed
    yield
    # teardown

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    # Permissive during hackathon; tighten for prod
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_v1_router, prefix="/api/v1")
    return app

app = create_app()

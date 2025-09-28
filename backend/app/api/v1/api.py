from fastapi import APIRouter
from app.api.v1.endpoints import enviducate

api_router = APIRouter()

# Include Enviducate endpoints
api_router.include_router(enviducate.router, tags=["enviducate"])
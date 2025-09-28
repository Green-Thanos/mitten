from fastapi import APIRouter
from . import parse, locations, summary, endpoint

api_v1_router = APIRouter()
api_v1_router.include_router(parse.router, tags=["parse"])
api_v1_router.include_router(locations.router, tags=["locations"])
api_v1_router.include_router(summary.router, tags=["summary"])
api_v1_router.include_router(endpoint.router, tags=["endpoint"])

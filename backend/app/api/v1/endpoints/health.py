from fastapi import APIRouter
from datetime import datetime
from app.schemas.query import HealthResponse

router = APIRouter()

@router.get("/", response_model=HealthResponse)
async def health_check():
    """Simple health check endpoint to confirm backend is running"""
    return HealthResponse(
        status="ok",
        timestamp=datetime.utcnow().isoformat() + "Z"
    )

from fastapi import APIRouter, HTTPException
from datetime import datetime
import uuid
from app.schemas.query import QueryRequest, QueryResponse

router = APIRouter()

@router.post("/", response_model=QueryResponse)
async def submit_query(query_request: QueryRequest):
    """
    Accept a natural language environmental query from the frontend.
    
    This endpoint validates, normalizes, and prepares queries for downstream processing
    (Gemini, GEE, Leafmap) in the Enviducate sustainability education platform.
    """
    try:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Get current timestamp in ISO8601 format
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Basic query validation and normalization
        normalized_query = query_request.query.strip()
        
        if not normalized_query:
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty"
            )
        
        # TODO: Add more sophisticated query validation and normalization
        # - Check for Michigan-specific environmental terms
        # - Validate geographic references
        # - Normalize environmental terminology
        
        return QueryResponse(
            request_id=request_id,
            query=normalized_query,
            timestamp=timestamp
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid query: {str(e)}"
        )

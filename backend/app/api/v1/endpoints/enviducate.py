from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import uuid
from datetime import datetime

from app.schemas.enviducate import (
    HealthResponse, QueryRequest, QueryResponse, ErrorResponse
)
from app.services.enviducate_service import EnviducateService

router = APIRouter()

# Initialize Enviducate service
enviducate_service = EnviducateService()


# === HEALTH ENDPOINT ===

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="ok",
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


# === MAIN QUERY ENDPOINT ===

@router.post("/query", response_model=QueryResponse)
async def process_enviducate_query(request: QueryRequest):
    """
    Process natural language queries about Michigan environmental issues.
    
    This endpoint:
    - Accepts natural language queries about Michigan environmental issues
    - Uses Google Earth Engine with Michigan bounding box [-90, 41, -82, 48]
    - Integrates Gemini API with Google Search for real data + context
    - Returns simplified response with only environmental summary
    - Supports caching for repeated queries
    """
    try:
        # Validate input
        if not request.query.strip():
            raise HTTPException(
                status_code=400, 
                detail="Query cannot be empty",
                headers={"error_code": "VALIDATION_ERROR"}
            )
        
        # Process query with Enviducate service (simplified - no visualization)
        result = await enviducate_service.process_enviducate_query_simple(
            query=request.query
        )
        
        return QueryResponse(**result)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"Query processing error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}",
            headers={"error_code": "PROCESSING_ERROR"}
        )

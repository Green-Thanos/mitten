from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class QueryRequest(BaseModel):
    """Request schema for environmental query submission"""
    query: str = Field(
        ...,
        description="User's natural language question about Michigan environment",
        min_length=1,
        max_length=1000,
        example="Show me wildfire risk in the Upper Peninsula"
    )


class QueryResponse(BaseModel):
    """Response schema for environmental query submission"""
    request_id: str = Field(
        ...,
        description="Unique identifier for the query request",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    query: str = Field(
        ...,
        description="The submitted query",
        example="Show me wildfire risk in the Upper Peninsula"
    )
    timestamp: str = Field(
        ...,
        description="ISO8601 timestamp of when the query was received",
        example="2025-01-27T16:45:00Z"
    )


class HealthResponse(BaseModel):
    """Response schema for health check"""
    status: str = Field(
        ...,
        description="Health status of the API",
        example="ok"
    )
    timestamp: str = Field(
        ...,
        description="ISO8601 timestamp of the health check",
        example="2025-01-27T16:45:00Z"
    )

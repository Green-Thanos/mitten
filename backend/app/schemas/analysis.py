from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import date


class TimeRange(BaseModel):
    """Time range for environmental analysis"""
    start: str = Field(
        ...,
        description="Start date in YYYY-MM-DD format",
        example="2000-01-01"
    )
    end: str = Field(
        ...,
        description="End date in YYYY-MM-DD format", 
        example="2023-12-31"
    )


class AnalysisRequest(BaseModel):
    """Request schema for environmental analysis"""
    query: str = Field(
        ...,
        description="User natural language query about environmental data",
        min_length=1,
        max_length=1000,
        example="Show me deforestation trends in the Amazon since 2000"
    )
    region: str = Field(
        ...,
        description="GeoJSON polygon, bounding box, or region name",
        example="Amazon"
    )
    time_range: TimeRange = Field(
        ...,
        description="Time range for analysis"
    )


class EnvironmentalStats(BaseModel):
    """Environmental statistics extracted from analysis"""
    deforestation_rate: Optional[float] = Field(
        None,
        description="Percentage change in forest cover",
        example=15.3
    )
    biodiversity_index: Optional[float] = Field(
        None,
        description="Normalized biodiversity index value",
        example=0.75
    )
    wildfire_count: Optional[int] = Field(
        None,
        description="Number of wildfire hotspots detected",
        example=42
    )


class AnalysisResponse(BaseModel):
    """Response schema for environmental analysis"""
    summary: str = Field(
        ...,
        description="Gemini-generated human-readable explanation of findings",
        example="Analysis shows a 15.3% increase in deforestation in the Amazon region from 2000-2023, with 42 wildfire hotspots detected in the most recent year."
    )
    stats: EnvironmentalStats = Field(
        ...,
        description="Extracted environmental statistics"
    )
    image_url: str = Field(
        ...,
        description="Path or URL to generated Leafmap visualization",
        example="/static/images/analysis_123e4567-e89b-12d3-a456-426614174000.png"
    )


class AnalysisError(BaseModel):
    """Error response schema"""
    error: str = Field(
        ...,
        description="Error message",
        example="Invalid time range: start date must be before end date"
    )
    details: Optional[str] = Field(
        None,
        description="Additional error details"
    )

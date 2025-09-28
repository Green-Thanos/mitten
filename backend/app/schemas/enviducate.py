from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# === REQUEST SCHEMAS ===

class QueryRequest(BaseModel):
    """Request schema for Enviducate environmental queries"""
    query: str = Field(..., description="Natural language query about Michigan environmental issues", example="Biodiversity in Michigan wetlands")


# === RESPONSE SCHEMAS ===

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Health status", example="ok")
    timestamp: str = Field(..., description="ISO8601 timestamp", example="2025-01-27T16:45:00Z")


class MetricCategory(str, Enum):
    """Categories of environmental metrics"""
    VEGETATION = "vegetation"
    CLIMATE = "climate"
    WATER = "water"
    LAND_COVER = "land_cover"
    ATMOSPHERE = "atmosphere"
    FIRE = "fire"
    SOIL = "soil"
    URBAN = "urban"
    BIODIVERSITY = "biodiversity"
    HYDROLOGY = "hydrology"
    TOPOGRAPHY = "topography"
    AGRICULTURE = "agriculture"


class RelevantMetric(BaseModel):
    """Detailed information about a relevant GEE metric"""
    id: str = Field(..., description="Unique metric identifier", example="ndvi")
    name: str = Field(..., description="Human-readable metric name", example="Normalized Difference Vegetation Index")
    description: str = Field(..., description="What this metric measures", example="Vegetation health and density indicator")
    category: MetricCategory = Field(..., description="Metric category", example=MetricCategory.VEGETATION)
    relevance_score: float = Field(..., description="Relevance score from 0-1", example=0.85, ge=0.0, le=1.0)
    range: Optional[str] = Field(None, description="Expected value range", example="[-1, 1]")
    datasets: Optional[List[str]] = Field(None, description="GEE datasets that provide this metric", example=["LANDSAT/LC08/C02/T1_L2"])


class Stats(BaseModel):
    """Environmental statistics from GEE data"""
    area_affected: Optional[float] = Field(None, description="Area affected in square kilometers", example=1250.5)
    species_count: Optional[int] = Field(None, description="Number of species affected", example=45)
    risk_level: Optional[str] = Field(None, description="Risk level assessment", example="High")
    deforestation_rate: Optional[float] = Field(None, description="Deforestation rate percentage", example=12.5)
    biodiversity_index: Optional[float] = Field(None, description="Biodiversity index (0-1)", example=0.78)
    wildfire_count: Optional[int] = Field(None, description="Wildfire incidents count", example=15)


class Summary(BaseModel):
    """Summary combining real GEE data with Gemini-curated context"""
    text: str = Field(..., description="Human-readable summary combining real data with context")
    stats: Stats = Field(..., description="Key metrics from GEE data")
    sources: List[str] = Field(..., description="Citations and URLs from Gemini research")
    key_metrics: List[str] = Field(..., description="List of relevant GEE metric IDs", example=["ndvi", "ndwi", "habitat_diversity"])
    relevant_metrics: List[RelevantMetric] = Field(..., description="Detailed information about relevant metrics")


class Visualization(BaseModel):
    """Leafmap-generated visualization focused on Michigan"""
    url: str = Field(..., description="URL to static PNG image", example="/static/images/visualization_abc123.png")
    type: str = Field(..., description="Visualization type", example="heatmap")
    legend: Optional[Dict[str, str]] = Field(None, description="Color meanings for the visualization")


class Charity(BaseModel):
    """Charity or organization resource"""
    name: str = Field(..., description="Organization name", example="Michigan Nature Association")
    url: str = Field(..., description="Organization website", example="https://www.michigannature.org")
    description: str = Field(..., description="Organization description", example="Protecting Michigan's natural areas and wildlife habitats")


class Resources(BaseModel):
    """Actionable charities and organizations"""
    charities: List[Charity] = Field(..., description="Relevant charities and organizations")
    shareableUrl: str = Field(..., description="Unique URL to recreate results without login", example="https://enviducate.com/share/abc123")


class QueryResponse(BaseModel):
    """Simplified response with only summary"""
    summary: Summary = Field(..., description="Environmental summary with real data + Gemini context")
    request_id: str = Field(..., description="Unique request identifier", example="123e4567-e89b-12d3-a456-426614174000")
    timestamp: str = Field(..., description="ISO8601 timestamp", example="2025-01-27T16:45:00Z")


# === ERROR SCHEMAS ===

class ErrorResponse(BaseModel):
    """Error response"""
    detail: str = Field(..., description="Error message", example="Invalid query: Query cannot be empty")
    error_code: Optional[str] = Field(None, description="Error code", example="VALIDATION_ERROR")

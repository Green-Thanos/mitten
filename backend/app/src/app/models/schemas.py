from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Literal

# --------- /parse ---------
class ParseRequest(BaseModel):
    query: str = Field(..., example="biodiversity in Saginaw wetlands 2017-2024")

class CharityRecommendation(BaseModel):
    name: str
    description: str
    url: HttpUrl
    category: str
    scope: Literal["county", "regional", "state"]

class ParseResponse(BaseModel):
    topic: str
    location: str
    time_range: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    charities: List[CharityRecommendation] = []

# --------- /summary ---------
class Charity(BaseModel):
    name: str
    url: HttpUrl
    category: str
    scope: Literal["county", "state", "regional"]

class SummaryRequest(BaseModel):
    topic: str
    location: str
    time_range: Optional[str] = None

class SummaryResponse(BaseModel):
    summary: str

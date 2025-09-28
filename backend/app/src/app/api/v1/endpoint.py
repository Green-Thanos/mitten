from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import uuid4

from app.models.schemas import ParseRequest, ParseResponse, SummaryResponse, CharityRecommendation
from app.api.v1.parse import parse_query
from app.api.v1.summary import get_summary
from app.api.v1.charities import get_charity_recommendations, init_gemini
from app.api.v1.locations import get_locations_for_topic
import google.generativeai as genai
from app.core.config import settings

router = APIRouter()

# Extra mock data for demo (sources + locations)
MOCK_SOURCES = [
    "Michigan Department of Natural Resources 2025 Wetlands Report",
    "Great Lakes Biodiversity Project 2024 Findings",
    "USGS Great Lakes Program",
]

MOCK_LOCATIONS = [
    {
        "lat": 42.331429,
        "lng": -83.045753,
        "label": "Rouge River Contamination"
    },
    {
        "lat": 42.940762,
        "lng": -85.728843,
        "label": "Kent County Superfund Site"
    },
    {
        "lat": 43.591209,
        "lng": -84.773506,
        "label": "Mid-Michigan PFAS Zone"
    },
]

@router.post("/endpoint")
async def analyze(
    req: ParseRequest,
):
    """
    Orchestrate parse -> summary -> charities and return full JSON bundle.
    """
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(settings.GEMINI_MODEL)

    try:
        # 1. Parse the query
        parsed: ParseResponse = await parse_query(req, model)

        # 2. Generate summary
        summary_resp: SummaryResponse = await get_summary(parsed)

        # 3. Charities are already included in parse response,
        # but if you want fresh, call get_charity_recommendations again
        charities = parsed.charities

        # 4. Build location data
        locations = get_locations_for_topic(parsed.topic)

        # 4. Build final response
        return {
            "id": f"mock_{uuid4().hex[:6]}",
            "originalQuery": req.query,
            "category": parsed.topic,
            "summary": summary_resp.summary,
            "sources": MOCK_SOURCES,       # could later be Gemini-powered
            "charities": charities,
            "visualizations": [
                {
                    "type": "pinpoints",
                    "data": locations
                }
            ],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in analyze: {e}")

from fastapi import APIRouter, Depends, HTTPException
import re
from typing import Optional
from app.models.schemas import ParseRequest, ParseResponse, CharityRecommendation
from app.api.v1.charities import init_gemini, get_charity_recommendations
import os, json
import google.generativeai as genai
from app.core.config import settings

router = APIRouter()

async def get_gemini_model():
    """Dependency to get initialized Gemini model."""
    return init_gemini()

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel(settings.GEMINI_MODEL)


SYSTEM_PROMPT = """
You are a natural language parser for environmental data queries focused on Michigan. Extract the following fields:

- topic: Extract the main environmental topic. Common categories include but are not limited to:
  * water quality/pollution
  * air quality
  * biodiversity/wildlife
  * deforestation/forest management
  * wetlands
  * climate change
  * invasive species
  * soil contamination
  * waste management
  * renewable energy
  * habitat conservation
  * environmental justice
  * PFAS/chemical pollution
  * erosion/coastal issues
  * urban sustainability
  Keep the original environmental topic mentioned, don't try to map it to a fixed set.

- location: a Michigan city or region. If none specified, use "Michigan".
- time_range: a year or year range if present (e.g., "2020" or "2019-2022"). Return null if none.

Always respond with compact, valid JSON like:
{"topic": "water quality", "location": "Detroit", "time_range": "2020-2022"}

Example mappings:
- "How's the water quality in Flint?" -> {"topic": "water quality", "location": "Flint", "time_range": null}
- "Tell me about Lake Michigan pollution" -> {"topic": "water pollution", "location": "Lake Michigan", "time_range": null}
- "What's happening with PFAS in Grand Rapids?" -> {"topic": "PFAS contamination", "location": "Grand Rapids", "time_range": null}
- "Urban heat islands in Detroit 2020-2023" -> {"topic": "urban heat islands", "location": "Detroit", "time_range": "2020-2023"}
"""

def _parse_query(query: str) -> dict:
    full_prompt = f"{SYSTEM_PROMPT}\n\nQuery: {query}"

    try:
        response = model.generate_content(full_prompt)
        content = response.text.strip()

        # Validate JSON
        parsed = json.loads(content)
        return parsed

    except json.JSONDecodeError:
        print("Failed to parse JSON from Gemini response.")
        return {"topic": "unknown", "location": "Unknown", "time_range": None}
    
    except Exception as e:
        print(f"Gemini API error: {e}")
        return {"topic": "unknown", "location": "Unknown", "time_range": None}

@router.post("/parse", response_model=ParseResponse)
async def parse_query(
    req: ParseRequest,
    model: genai.GenerativeModel = Depends(get_gemini_model)
) -> ParseResponse:
    """Parse natural language query and get relevant Michigan charity recommendations."""
    try:
        # Get parsed query components
        parsed = _parse_query(req.query)
        topic = parsed.get("topic", "unknown")
        location = parsed.get("location", "Michigan")
        time_range = parsed.get("time_range")
        
        # Get charity recommendations from Gemini
        charities = await get_charity_recommendations(model, topic, location)
        
        # Convert charities to proper model, with validation
        charity_models = []
        for charity in charities:
            try:
                charity_models.append(CharityRecommendation(**charity))
            except Exception as e:
                print(f"Error parsing charity: {e}")
                print(f"Problematic charity data: {charity}")
                continue
        
        return ParseResponse(
            topic=topic,
            location=location,
            time_range=time_range,
            confidence=0.8,  # We'll improve this with Gemini's confidence scores later
            charities=charity_models
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

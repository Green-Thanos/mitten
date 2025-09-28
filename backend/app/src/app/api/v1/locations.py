from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Tuple, Optional
import google.generativeai as genai
import os
import json
from datetime import datetime

router = APIRouter()

# Michigan's bounding box coordinates
MI_BOUNDS = {
    "north": 45.858,  # Northern boundary
    "south": 41.696,  # Southern boundary
    "west": -88.418,  # Western boundary
    "east": -82.413   # Eastern boundary
}

LOCATION_PROMPT = """
You are an environmental incident tracker focused on Michigan. Based on the topic {topic}, provide 5 specific locations in Michigan where this environmental issue has actually occurred or is actively occurring.

Focus on:
- Specific incident sites (not monitoring stations)
- Places with documented environmental damage or impact
- Recent or ongoing environmental challenges
- Actual affected areas (not management offices or research centers)

For example:
- For biodiversity: Sites of significant species loss or habitat destruction
- For deforestation: Areas where significant tree loss has occurred
- For wildfire: Locations of actual fire incidents or severe burn areas

Return the response as a JSON array of objects, each with:
- latitude (between 41.696 and 45.858)
- longitude (between -88.418 and -82.413)
- name (location name)
- description (specific details about what happened/is happening at this site)

Example format:
[
    {{
        "lat": 42.331429,
        "lng": -83.045753,
        "label": "Belle Isle Wetlands"
    }}
]

Ensure all coordinates are within Michigan's boundaries and are precise to 6 decimal places."""

def get_locations_for_topic(topic: str) -> List[dict]:
    """Get coordinates and descriptions for environmental issue locations."""
    # Initialize Gemini
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-pro")
    
    try:
        # Generate prompt with specific topic
        prompt = LOCATION_PROMPT.format(topic=topic)
        response = model.generate_content(prompt)
        content = response.text.strip()
        
        # Parse JSON response
        locations = json.loads(content)
        
        # Validate coordinates are within Michigan
        validated_locations = []
        for loc in locations:
            lat = float(loc["latitude"])
            lng = float(loc["longitude"])
            
            if (MI_BOUNDS["south"] <= lat <= MI_BOUNDS["north"] and 
                MI_BOUNDS["west"] <= lng <= MI_BOUNDS["east"]):
                validated_locations.append(loc)
        
        return validated_locations[:5]  # Ensure we return at most 5 locations
        
    except Exception as e:
        print(f"Error getting locations: {e}")
        # Return some default locations based on topic
        return get_default_locations(topic)

def get_default_locations(topic: str) -> List[dict]:
    """Fallback locations if the API fails."""
    defaults = {
        "biodiversity": [
            {"lat": 42.331429, "lng": -83.045753, "label": "Belle Isle Fish Habitat"},
            {"lat": 43.591209, "lng": -84.773506, "label": "Saginaw Bay Wetlands"},
            {"lat": 42.940762, "lng": -85.728843, "label": "Grand River Watershed"},
            {"lat": 44.762131, "lng": -84.727684, "label": "Kirtland's Warbler Historic Range"},
            {"lat": 42.169799, "lng": -83.642687, "label": "River Raisin PCB Zone"}
        ],
        "deforestation": [
            {"lat": 44.314844, "lng": -85.602364, "label": "Pere Marquette Clear-Cut"},
            {"lat": 46.182541, "lng": -84.353402, "label": "Upper Peninsula Mining Site"},
            {"lat": 43.591209, "lng": -84.773506, "label": "Midland Flood Impact Zone"},
            {"lat": 45.571184, "lng": -84.733705, "label": "Cheboygan Storm Damage"},
            {"lat": 42.940762, "lng": -85.728843, "label": "Grand Rapids Urban Forest Loss"}
        ],
        "wildfire": [
            {"lat": 44.314844, "lng": -85.602364, "label": "Huron Forest Burn Site"},
            {"lat": 45.571184, "lng": -84.733705, "label": "Grayling Fire Zone"},
            {"lat": 46.182541, "lng": -84.353402, "label": "UP Peat Fire Location"},
            {"lat": 43.591209, "lng": -84.773506, "label": "State Game Area Burn"},
            {"lat": 44.762131, "lng": -84.727684, "label": "Au Sable River Fire"}
        ],
        "unknown": [
            {"lat": 42.331429, "lng": -83.045753, "label": "Rouge River Contamination"},
            {"lat": 42.940762, "lng": -85.728843, "label": "Kent County Superfund Site"},
            {"lat": 43.591209, "lng": -84.773506, "label": "Mid-Michigan PFAS Zone"},
            {"lat": 45.571184, "lng": -84.733705, "label": "Northern Pipeline Spill"},
            {"lat": 46.182541, "lng": -84.353402, "label": "UP Mine Drainage"}
        ]
    }
    return defaults.get(topic, defaults["unknown"])

@router.get("/locations/{topic}")
async def get_environmental_locations(topic: str):
    """Get locations for environmental issues by topic."""
        
    locations = get_locations_for_topic(topic)
    return {"locations": locations}
import google.generativeai as genai
from app.core.config import settings

def init_gemini():
    genai.configure(api_key=settings.GEMINI_API_KEY)
    return genai.GenerativeModel(settings.GEMINI_MODEL)

def get_charity_prompt(topic: str, location: str) -> str:
    return f"""You are a Michigan-focused environmental and social impact expert.
Given the environmental topic "{topic}" in {location}, Michigan, provide a structured list of 3-5 legitimate local charities or organizations that people could contribute to or volunteer with.

Focus on organizations that:
1. Are actually located in or directly serve {location} or the surrounding Michigan region
2. Have a clear connection to {topic}
3. Have verifiable web presence and contact information
4. Are registered non-profits or legitimate government/educational institutions

Return only JSON in this exact format:
{{
    "charities": [
        {{
            "name": "Organization Name",
            "description": "2-3 sentence description of their work related to {topic}",
            "url": "https://their-website.org",
            "category": "One of: biodiversity, forestry, wetlands, wildfire, education",
            "scope": "One of: county, regional, state"
        }}
    ]
}}"""

async def get_charity_recommendations(model: genai.GenerativeModel, topic: str, location: str) -> list[dict]:
    """Query Gemini for relevant Michigan charities based on topic and location."""
    prompt = get_charity_prompt(topic, location)
    response = await model.generate_content_async(prompt)
    
    # Extract JSON from response
    try:
        response_text = response.text
        # Clean up the response text to ensure it's valid JSON
        # Find the first { and last } to extract just the JSON part
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start >= 0 and end > start:
            import json
            json_str = response_text[start:end]
            data = json.loads(json_str)
            return data.get("charities", [])
    except (KeyError, ValueError, AttributeError) as e:
        print(f"Error parsing Gemini response: {e}")
        print(f"Raw response: {response_text if 'response_text' in locals() else response}")
        # Fallback to default charities if Gemini response isn't properly formatted
        return [{
            "name": "Michigan Environmental Council",
            "description": "Statewide coalition working to protect Michigan's water, land, and public health.",
            "url": "https://environmentalcouncil.org",
            "category": topic,
            "scope": "state"
        }]
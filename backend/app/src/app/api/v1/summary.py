from fastapi import APIRouter, HTTPException
from app.models.schemas import ParseResponse, SummaryResponse
import google.generativeai as genai
from app.core.config import settings

router = APIRouter()

# Initialize Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel(settings.GEMINI_MODEL)

SUMMARY_PROMPT = """
You are an environmental education specialist focused on Michigan's environmental challenges. 
Create a comprehensive yet concise educational summary about {topic} in {location}, Michigan.

Focus on:
1. Current state and trends
2. Local impact and significance
3. Connection to Michigan's broader ecosystem
4. Recent developments or changes{time_range}
5. Scientific context from Michigan DNR, EGLE, and NOAA Great Lakes data

Keep the tone educational but accessible. Include specific facts and figures where relevant.
Limit the response to 1 short paragraph.

Format the response as a single cohesive paragraph without bullet points or sections."""

def generate_environmental_summary(parse_result: ParseResponse) -> str:
    """Generate an educational summary using Gemini."""
    try:
        # Format time range context if provided
        time_context = f" (focusing on {parse_result.time_range})" if parse_result.time_range else ""
        
        # Generate prompt with specific details
        prompt = SUMMARY_PROMPT.format(
            topic=parse_result.topic,
            location=parse_result.location,
            time_range=time_context
        )
        
        print(f"Sending prompt to Gemini: {prompt}")
            
        # Get response from Gemini
        response = model.generate_content(prompt)
        if not response or not response.text:
            raise ValueError("Empty response from Gemini")
            
        summary = response.text.strip()
        print(f"Received summary from Gemini: {summary[:100]}...")
        return summary
        
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating summary: {str(e)}"
        )

@router.post("/summary", response_model=SummaryResponse)
async def get_summary(parse_result: ParseResponse) -> SummaryResponse:
    """Generate an educational summary about environmental issues in Michigan."""
    print(f"Received request with parse_result: {parse_result}")
    try:
        # Generate the summary using Gemini
        summary = generate_environmental_summary(parse_result)
        return SummaryResponse(summary=summary)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error in get_summary: {str(e)}"
        )
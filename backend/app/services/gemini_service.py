import google.generativeai as genai
from typing import Dict, Any
import json
import os
from app.core.config import settings


class GeminiService:
    """Service for interacting with Google Gemini AI"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def process_environmental_query(self, query: str, region: str, time_range: Dict[str, str]) -> Dict[str, Any]:
        """
        Process environmental query using Gemini to extract indicators and generate summary
        """
        prompt = f"""
        Analyze this environmental query and extract relevant indicators:
        
        Query: "{query}"
        Region: "{region}"
        Time Range: {time_range['start']} to {time_range['end']}
        
        Please provide a JSON response with:
        1. indicators: List of environmental indicators to analyze (e.g., deforestation, biodiversity, wildfire, air_quality, water_quality)
        2. summary: A human-readable explanation of what the analysis will show
        3. gee_datasets: List of Google Earth Engine datasets that would be relevant for this analysis
        
        Focus on Michigan environmental issues and use scientific terminology.
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text)
            
            return {
                "indicators": result.get("indicators", []),
                "summary": result.get("summary", ""),
                "gee_datasets": result.get("gee_datasets", [])
            }
        except Exception as e:
            # Fallback if JSON parsing fails
            return {
                "indicators": ["deforestation", "biodiversity", "wildfire"],
                "summary": f"Analysis of {query} for {region} from {time_range['start']} to {time_range['end']}",
                "gee_datasets": ["LANDSAT/LC08/C01/T1_SR", "MODIS/006/MOD13Q1"]
            }
    
    async def generate_analysis_summary(self, stats: Dict[str, Any], indicators: list) -> str:
        """
        Generate a human-readable summary of the analysis results
        """
        prompt = f"""
        Based on these environmental statistics, generate a clear, educational summary:
        
        Statistics: {json.dumps(stats, indent=2)}
        Indicators analyzed: {', '.join(indicators)}
        
        Write a 2-3 sentence summary that explains the findings in simple terms for environmental education.
        Focus on trends and implications for Michigan's environment.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Environmental analysis completed. Key findings: {json.dumps(stats, indent=2)}"

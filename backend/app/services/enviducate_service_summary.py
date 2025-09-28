"""
Enviducate Summary Service
Focused on Gemini-powered summary generation with pre-processed data
"""

import google.generativeai as genai
import json
import os
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.config import settings


class EnviducateSummaryService:
    """Service for generating environmental summaries using Gemini AI with pre-processed data"""
    
    def __init__(self):
        self.gemini_api_key = settings.GEMINI_API_KEY
        self.model = None
        self.initialized = False

    def _ensure_initialized(self):
        """Initialize Gemini service when needed"""
        if self.initialized:
            return
            
        if self.gemini_api_key and self.gemini_api_key.strip():
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
                self.initialized = True
                print("Gemini AI initialized successfully")
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini: {e}")
                self.model = None
        else:
            print("Warning: Gemini API key not configured")

    async def generate_summary_with_data(
        self, 
        query: str, 
        environmental_data: Dict[str, Any],
        sources: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate environmental summary using pre-processed data
        
        Args:
            query: Original user query
            environmental_data: Pre-processed environmental metrics
            sources: List of data sources
            
        Returns:
            Dictionary with summary text, stats, and metadata
        """
        self._ensure_initialized()
        
        if not self.model:
            return self._get_fallback_summary(query, environmental_data, sources or [])
        
        try:
            # Convert data to JSON string for prompt
            data_str = json.dumps(environmental_data, indent=2)
            sources_str = json.dumps(sources or [], indent=2)
            
            prompt = f"""
Answer the user's question about Michigan's environment using the provided data.

Question: "{query}"
Environmental Data: {data_str}
Sources: {sources_str}

Instructions:
1. Answer their specific question directly
2. Use the real data to support your answer
3. Explain technical terms in simple language
4. Focus on what the data actually shows
5. Be informative but accessible - avoid overwhelming jargon
6. If data is missing, explain what we know in general terms

Return a JSON object with this structure:
{{
    "text": "A direct answer to their question using the environmental data.",
    "key_insights": [
        "Key finding 1 from the data",
        "Key finding 2 from the data", 
        "Key finding 3 from the data"
    ],
    "recommendations": [
        "Actionable recommendation 1",
        "Actionable recommendation 2"
    ],
    "confidence": 0.85
}}

Focus on Michigan's environment, use simple language, and help people learn about protecting our natural world.
"""
            
            response = self.model.generate_content(prompt)
            
            # Clean the response text to extract JSON
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # Remove ```json
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # Remove ```
            response_text = response_text.strip()
            
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Cleaned response: {response_text[:200]}...")
                return self._get_fallback_summary(query, environmental_data, sources or [])
            
            # Process the result
            return {
                "text": result.get("text", f"Environmental analysis of {query} in Michigan."),
                "key_insights": result.get("key_insights", []),
                "recommendations": result.get("recommendations", []),
                "confidence": result.get("confidence", 0.8),
                "stats": self._extract_stats_from_data(environmental_data),
                "sources": sources or []
            }
            
        except Exception as e:
            print(f"Summary generation error: {e}")
            return self._get_fallback_summary(query, environmental_data, sources or [])

    def _extract_stats_from_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant statistics from environmental data"""
        stats = {}
        
        # Common environmental metrics
        metric_mapping = {
            'biodiversity_index': 'biodiversity_index',
            'deforestation_rate': 'deforestation_rate', 
            'wildfire_count': 'wildfire_count',
            'wetland_area_km2': 'wetland_area_km2',
            'water_quality_index': 'water_quality_index',
            'air_quality_index': 'air_quality_index',
            'species_count': 'species_count',
            'risk_level': 'risk_level',
            'area_affected': 'area_affected'
        }
        
        for key, value in data.items():
            if key in metric_mapping and value is not None:
                stats[metric_mapping[key]] = value
                
        return stats

    def _get_fallback_summary(self, query: str, data: Dict[str, Any], sources: List[str]) -> Dict[str, Any]:
        """Fallback summary when Gemini is not available"""
        return {
            "text": f"Environmental analysis of {query} in Michigan reveals important data about our natural environment. The region shows various environmental indicators that help us understand the health of our ecosystems.",
            "key_insights": [
                "Michigan's environment is diverse and important for wildlife",
                "Monitoring helps us protect natural resources",
                "Community action can make a positive difference"
            ],
            "recommendations": [
                "Learn more about local environmental issues",
                "Support conservation efforts in your area",
                "Practice sustainable living habits"
            ],
            "confidence": 0.6,
            "stats": self._extract_stats_from_data(data),
            "sources": sources
        }

    async def generate_contextual_summary(
        self,
        query: str,
        indicators: List[str],
        environmental_data: Dict[str, Any],
        recent_news: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate summary with additional context from recent news/sources
        
        Args:
            query: Original user query
            indicators: Environmental indicators identified
            environmental_data: Pre-processed environmental metrics
            recent_news: Recent news articles or sources
            
        Returns:
            Enhanced summary with context
        """
        self._ensure_initialized()
        
        if not self.model:
            return self._get_fallback_summary(query, environmental_data, [])
        
        try:
            # Prepare context data
            data_str = json.dumps(environmental_data, indent=2)
            indicators_str = json.dumps(indicators, indent=2)
            news_str = json.dumps(recent_news or [], indent=2)
            
            prompt = f"""
You are an environmental educator creating a comprehensive summary about Michigan's environment.

Query: "{query}"
Environmental Indicators: {indicators_str}
Environmental Data: {data_str}
Recent News/Sources: {news_str}

Create a JSON response with:
{{
    "text": "Comprehensive summary combining data with recent context",
    "key_insights": ["insight1", "insight2", "insight3"],
    "recommendations": ["action1", "action2"],
    "trends": "What trends are we seeing?",
    "urgency": "low/medium/high",
    "confidence": 0.85
}}

Requirements:
- Use recent news to add context and relevance
- Explain what the data means for Michigan residents
- Provide actionable recommendations
- Assess the urgency of environmental issues
- Keep language accessible and engaging
"""
            
            response = self.model.generate_content(prompt)
            
            # Clean and parse response
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"Contextual summary JSON decode error: {e}")
                return self._get_fallback_summary(query, environmental_data, [])
            
            return {
                "text": result.get("text", f"Environmental analysis of {query} in Michigan."),
                "key_insights": result.get("key_insights", []),
                "recommendations": result.get("recommendations", []),
                "trends": result.get("trends", "Data shows ongoing environmental patterns"),
                "urgency": result.get("urgency", "medium"),
                "confidence": result.get("confidence", 0.8),
                "stats": self._extract_stats_from_data(environmental_data),
                "sources": [item.get('source', 'Environmental Research') for item in (recent_news or [])]
            }
            
        except Exception as e:
            print(f"Contextual summary generation error: {e}")
            return self._get_fallback_summary(query, environmental_data, [])

    async def generate_quick_summary(self, query: str, data: Dict[str, Any]) -> str:
        """
        Generate a quick, simple summary without full processing
        
        Args:
            query: User query
            data: Environmental data
            
        Returns:
            Simple summary string
        """
        self._ensure_initialized()
        
        if not self.model:
            return f"Environmental analysis of {query} in Michigan using available data."
        
        try:
            prompt = f"""
Create a brief, friendly summary about this environmental topic in Michigan:

Query: "{query}"
Data: {json.dumps(data, indent=2)}

Write 2-3 sentences in simple language that anyone can understand. Be positive and educational.
"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"Quick summary error: {e}")
            return f"Environmental analysis of {query} in Michigan using available data."

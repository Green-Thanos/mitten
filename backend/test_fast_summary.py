#!/usr/bin/env python3
"""
Test the fast summary service with pre-processed data
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.enviducate_service_summary import EnviducateSummaryService

async def test_fast_summary():
    """Test the fast summary generation"""
    
    print("🚀 Testing Fast Summary Service")
    print("=" * 50)
    
    service = EnviducateSummaryService()
    
    # Pre-processed environmental data (simulating what would come from GEE)
    sample_data = {
        "biodiversity_index": 0.72,
        "wetland_area_km2": 1250.5,
        "water_quality_index": 0.68,
        "species_count": 85,
        "area_affected": 250493.0,
        "data_source": "Google Earth Engine",
        "region": "Michigan"
    }
    
    sources = [
        "Michigan DNR",
        "Google Earth Engine", 
        "US EPA"
    ]
    
    queries = [
        "Biodiversity in Michigan wetlands",
        "Water quality in Great Lakes",
        "Forest health in Upper Peninsula"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n🔍 Test {i}: '{query}'")
        print("-" * 40)
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Test basic summary generation
            result = await service.generate_summary_with_data(
                query=query,
                environmental_data=sample_data,
                sources=sources
            )
            
            end_time = asyncio.get_event_loop().time()
            response_time = end_time - start_time
            
            print(f"⏱️  Response Time: {response_time:.2f} seconds")
            print(f"✅ SUCCESS!")
            print(f"  Text: {result['text'][:100]}...")
            print(f"  Key Insights: {len(result.get('key_insights', []))}")
            print(f"  Recommendations: {len(result.get('recommendations', []))}")
            print(f"  Confidence: {result.get('confidence', 'N/A')}")
            print(f"  Stats: {len(result.get('stats', {}))} metrics")
            
            # Show key insights
            if result.get('key_insights'):
                print("  Insights:")
                for insight in result['key_insights'][:2]:
                    print(f"    • {insight}")
            
        except Exception as e:
            print(f"❌ FAILED - Error: {e}")
    
    print(f"\n🎉 Fast Summary Service Test Complete!")
    print(f"Key Benefits:")
    print(f"• No GEE processing delays")
    print(f"• Fast Gemini AI responses")
    print(f"• Pre-processed data input")
    print(f"• Modular and testable")

if __name__ == "__main__":
    asyncio.run(test_fast_summary())

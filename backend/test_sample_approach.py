#!/usr/bin/env python3
"""
Test the sample-based GEE approach
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.enviducate_service import EnviducateService

async def test_sample_approach():
    """Test the sample-based GEE analysis"""
    
    print("🧪 Testing Sample-Based GEE Approach")
    print("=" * 50)
    
    service = EnviducateService()
    
    # Test a simple query
    query = "Biodiversity in Michigan wetlands"
    
    try:
        print(f"Testing query: '{query}'")
        
        # Test the full pipeline
        result = await service.process_enviducate_query_simple(query)
        
        print("✅ SUCCESS - Summary created:")
        print(f"  Request ID: {result.get('request_id', 'N/A')}")
        
        summary = result.get('summary', {})
        print(f"  Text: {summary.get('text', 'N/A')[:100]}...")
        print(f"  Sources: {len(summary.get('sources', []))} sources")
        
        # Show stats
        stats = summary.get('stats', {})
        non_null_stats = {k: v for k, v in stats.items() if v is not None}
        print(f"  Stats: {len(non_null_stats)} non-null values")
        for key, value in non_null_stats.items():
            print(f"    {key}: {value}")
        
        print("\n🎉 Sample-based approach is working!")
        
    except Exception as e:
        print(f"❌ FAILED - Error: {e}")
        print(f"  Error type: {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(test_sample_approach())

#!/usr/bin/env python3
"""
Test with a much faster, simplified approach
"""

import time
import requests
import json

def test_fast_api():
    """Test with a simple query that should be faster"""
    
    print("🚀 Testing Fast API Response")
    print("=" * 40)
    
    url = "http://localhost:8000/api/v1/query"
    
    # Try a simpler query first
    simple_queries = [
        "Michigan forests",
        "Great Lakes water",
        "Detroit air quality"
    ]
    
    for query in simple_queries:
        print(f"\n🔍 Testing: '{query}'")
        
        payload = {"query": query}
        start_time = time.time()
        
        try:
            response = requests.post(url, json=payload, timeout=15)
            end_time = time.time()
            response_time = end_time - start_time
            
            print(f"  ⏱️  Time: {response_time:.2f}s")
            print(f"  📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                summary = data.get('summary', {})
                print(f"  ✅ Success! Text: {summary.get('text', '')[:50]}...")
                break
            else:
                print(f"  ❌ Error: {response.text[:100]}")
                
        except requests.exceptions.Timeout:
            print(f"  ❌ Timeout after 15s")
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    test_fast_api()

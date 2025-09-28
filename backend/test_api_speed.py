#!/usr/bin/env python3
"""
Test API response speed
"""

import time
import requests
import json

def test_api_speed():
    """Test how fast the API responds"""
    
    print("🚀 Testing API Response Speed")
    print("=" * 40)
    
    url = "http://localhost:8000/api/v1/query"
    payload = {
        "query": "Biodiversity in Michigan wetlands"
    }
    
    print(f"Making request to: {url}")
    print(f"Query: {payload['query']}")
    print()
    
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        print(f"⏱️  Response Time: {response_time:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            summary = data.get('summary', {})
            
            print(f"✅ SUCCESS!")
            print(f"  Request ID: {data.get('request_id', 'N/A')}")
            print(f"  Text Length: {len(summary.get('text', ''))} characters")
            print(f"  Sources: {len(summary.get('sources', []))}")
            print(f"  Stats: {len([k for k, v in summary.get('stats', {}).items() if v is not None])} non-null values")
            
            # Show first 100 chars of summary
            text = summary.get('text', '')
            print(f"  Preview: {text[:100]}...")
            
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT: Request took longer than 30 seconds")
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Server not running or not accessible")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_api_speed()

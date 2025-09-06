#!/usr/bin/env python3
"""
Test Google Custom Search API directly
"""
import os
import requests
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_google_search():
    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")
    
    print(f"API Key: {api_key[:20] if api_key else 'None'}...")
    print(f"CSE ID: {cse_id}")
    
    if not api_key or not cse_id:
        print("ERROR: Google API credentials not found")
        return
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': cse_id,
        'q': "trending topics news today",
        'num': 3,
        'safe': 'medium',
        'dateRestrict': 'w1'
    }
    
    try:
        print("Making Google Custom Search API request...")
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS: Google Custom Search API working!")
            
            if 'items' in data:
                print(f"Found {len(data['items'])} results:")
                for i, item in enumerate(data['items'][:2], 1):
                    print(f"  {i}. {item.get('title', 'No title')}")
                    print(f"     {item.get('link', 'No link')}")
            else:
                print("No items in response")
                
        else:
            print(f"ERROR: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_google_search())
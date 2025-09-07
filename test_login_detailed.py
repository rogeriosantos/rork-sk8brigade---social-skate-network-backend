#!/usr/bin/env python3

import asyncio
import httpx
import json

async def test_login_detailed():
    async with httpx.AsyncClient() as client:
        # Test login
        login_data = {
            "username_or_email": "dois",
            "password": "Com,,320"
        }
        
        try:
            print("Testing login endpoint...")
            response = await client.post(
                "http://10.10.42.149:8000/api/v1/auth/login",
                json=login_data,
                timeout=30.0
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            # Try to get response text first
            response_text = response.text
            print(f"Raw Response: {response_text[:500]}...")  # First 500 chars
            
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    print(f"JSON Response: {json.dumps(response_json, indent=2)}")
                except Exception as e:
                    print(f"Failed to parse JSON: {e}")
            else:
                print(f"Error Response: {response_text}")
                
        except Exception as e:
            print(f"Request Error: {e}")

        # Also test if backend is responding at all
        try:
            print("\nTesting health endpoint...")
            health_response = await client.get(
                "http://10.10.42.149:8000/docs",
                timeout=10.0
            )
            print(f"Docs endpoint status: {health_response.status_code}")
        except Exception as e:
            print(f"Health check error: {e}")

if __name__ == "__main__":
    asyncio.run(test_login_detailed())

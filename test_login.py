#!/usr/bin/env python3

import asyncio
import httpx

async def test_login():
    async with httpx.AsyncClient() as client:
        # Test login
        login_data = {
            "username_or_email": "dois",
            "password": "Com,,320"
        }
        
        try:
            response = await client.post(
                "http://10.10.42.149:8000/api/v1/auth/login",
                json=login_data,
                timeout=10.0
            )
            print(f"Login response status: {response.status_code}")
            print(f"Login response: {response.json()}")
            
            if response.status_code == 200:
                token = response.json().get("access_token")
                
                # Test /me endpoint
                headers = {"Authorization": f"Bearer {token}"}
                me_response = await client.get(
                    "http://10.10.42.149:8000/api/v1/auth/me",
                    headers=headers,
                    timeout=10.0
                )
                print(f"\n/me response status: {me_response.status_code}")
                print(f"/me response: {me_response.json()}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_login())

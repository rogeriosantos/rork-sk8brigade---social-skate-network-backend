#!/usr/bin/env python3

import requests
import json

def test_simple():
    try:
        # Simple GET request to docs
        print("Testing docs endpoint...")
        response = requests.get("http://10.10.42.149:8000/docs", timeout=5)
        print(f"Docs status: {response.status_code}")
        
        # Test login
        print("\nTesting login...")
        login_data = {
            "username_or_email": "dois",
            "password": "Com,,320"
        }
        
        response = requests.post(
            "http://10.10.42.149:8000/api/v1/auth/login",
            json=login_data,
            timeout=10
        )
        
        print(f"Login status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response text: {response.text[:200]}...")
        
        if response.status_code == 200:
            print(f"JSON: {response.json()}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_simple()

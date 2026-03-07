"""
Test script to verify /api/v1/risks endpoint works with authentication
"""
import requests

# Login first to get a token
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    data={
        "username": "admin@grc.com",
        "password": "Admin@123",  # Default admin password from seeder
    }
)

if login_response.status_code == 200:
    token_data = login_response.json()
    access_token = token_data["access_token"]
    print(f"✓ Login successful! Token: {access_token[:20]}...")
    
    # Now try to fetch risks
    print("\n📋 Fetching risks...")
    risks_response = requests.get(
        "http://localhost:8000/api/v1/risks",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"skip": 0, "limit": 20}
    )
    
    print(f"Status: {risks_response.status_code}")
    print(f"Response: {risks_response.json()}")
    
    if risks_response.status_code == 200:
        print("\n✅ SUCCESS! /api/v1/risks endpoint is working!")
    elif risks_response.status_code == 403:
        print("\n❌ FAILED: 403 Forbidden - User doesn't have risk:read permission")
        print("Check backend logs for detailed permission information")
    else:
        print(f"\n❌ FAILED: {risks_response.status_code}")
else:
    print(f"❌ Login failed: {login_response.status_code}")
    print(f"Response: {login_response.json()}")

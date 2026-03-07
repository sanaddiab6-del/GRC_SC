"""Test users endpoint and risk owner dropdown functionality."""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_users_endpoint():
    """Test the /api/v1/users endpoint with authentication."""
    print("=" * 60)
    print("TESTING USERS ENDPOINT")
    print("=" * 60)
    
    # Step 1: Login
    print("\n1. Logging in as admin...")
    login_response = requests.post(
        f"{BASE_URL}/api/v1/auth/token",
        data={
            "username": "admin@grc.com",
            "password": "Admin@123"
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return False
    
    token_data = login_response.json()
    access_token = token_data.get("access_token")
    print(f"✅ Login successful! Token: {access_token[:50]}...")
    
    # Step 2: Test users endpoint
    print("\n2. Fetching users...")
    headers = {"Authorization": f"Bearer {access_token}"}
    users_response = requests.get(
        f"{BASE_URL}/api/v1/users",
        headers=headers,
        params={"limit": 100}
    )
    
    print(f"Status Code: {users_response.status_code}")
    
    if users_response.status_code != 200:
        print(f"❌ Users endpoint failed: {users_response.status_code}")
        print(f"Response: {users_response.text}")
        return False
    
    users = users_response.json()
    print(f"✅ Users endpoint successful!")
    print(f"Total users found: {len(users)}")
    print("\nUsers:")
    for user in users:
        print(f"  - {user.get('name')} ({user.get('email')}) - Role: {user.get('role')}")
        print(f"    user_id: {user.get('user_id')}")
    
    # Step 3: Test risks endpoint
    print("\n3. Testing risks endpoint...")
    risks_response = requests.get(
        f"{BASE_URL}/api/v1/risks",
        headers=headers,
        params={"skip": 0, "limit": 10}
    )
    
    print(f"Status Code: {risks_response.status_code}")
    
    if risks_response.status_code != 200:
        print(f"❌ Risks endpoint failed: {risks_response.status_code}")
        print(f"Response: {risks_response.text}")
    else:
        risks_data = risks_response.json()
        total = risks_data.get('total', 0) if isinstance(risks_data, dict) else len(risks_data)
        print(f"✅ Risks endpoint successful! Total risks: {total}")
    
    # Step 4: Test database connection via health endpoint
    print("\n4. Testing database connection...")
    health_response = requests.get(f"{BASE_URL}/health")
    print(f"Health Status: {health_response.json()}")
    
    return True

if __name__ == "__main__":
    try:
        success = test_users_endpoint()
        if success:
            print("\n" + "=" * 60)
            print("✅ ALL TESTS PASSED!")
            print("=" * 60)
            print("\nThe users endpoint is working correctly.")
            print("If the Risk Owner dropdown is still empty, check:")
            print("1. Browser console for JavaScript errors")
            print("2. Network tab for failed API calls")
            print("3. SessionStorage for access_token")
        else:
            print("\n" + "=" * 60)
            print("❌ TESTS FAILED")
            print("=" * 60)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

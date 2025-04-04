import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_root():
    """Test the root endpoint"""
    response = requests.get(f"{BASE_URL}/")
    print(f"Root endpoint: {response.status_code}")
    print(response.json())
    print()

def test_test_endpoint():
    """Test the test endpoint"""
    response = requests.get(f"{BASE_URL}/test")
    print(f"Test endpoint: {response.status_code}")
    print(response.json())
    print()

def test_users_list():
    """Test getting all users"""
    response = requests.get(f"{BASE_URL}/users/")
    print(f"Users list endpoint: {response.status_code}")
    try:
        print(response.json())
    except:
        print(f"Response content: {response.content}")
    print()

def test_create_user():
    """Test creating a user"""
    user_data = {
        "fullname": "Test User",
        "email": "test@example.com",
        "phone": "1234567890",
        "aadhar": "123456789012",
        "dob": "1990-01-01"
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        f"{BASE_URL}/users/", 
        data=json.dumps(user_data),
        headers=headers
    )
    print(f"Create user endpoint: {response.status_code}")
    try:
        print(response.json())
    except:
        print(f"Response content: {response.content}")
    print()

if __name__ == "__main__":
    print("Testing MyChitFund API...")
    print("=========================")
    
    try:
        test_root()
        test_test_endpoint()
        test_users_list()
        
        # Uncomment to test user creation
        # test_create_user()
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the API server.")
        print("Make sure the server is running on http://localhost:8000")
        sys.exit(1)
    
    print("Tests completed.")
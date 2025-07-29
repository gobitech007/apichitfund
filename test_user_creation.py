#!/usr/bin/env python3
"""
Test script to verify user creation with optional email and aadhar
"""
import requests
import json
from datetime import date

BASE_URL = "http://localhost:8000/api"

def test_user_creation():
    """Test user creation with different scenarios"""
    
    print("Testing user creation with optional email and aadhar...")
    
    # Test 1: User with email and aadhar (both provided)
    print("\n1. Testing user creation with both email and aadhar...")
    user_data_1 = {
        "fullname": "John Doe",
        "email": "john.doe@example.com",
        "phone": "9876543210",
        "aadhar": "123456789012",
        "dob": "1990-01-01",
        "pin": 1234,
        "role": "user"
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=user_data_1)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✅ Success: User created with email and aadhar")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 2: User without email (email optional)
    print("\n2. Testing user creation without email...")
    user_data_2 = {
        "fullname": "Jane Smith",
        "phone": "9876543211",
        "aadhar": "123456789013",
        "dob": "1992-05-15",
        "pin": 5678,
        "role": "user"
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=user_data_2)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✅ Success: User created without email")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 3: User without aadhar (aadhar optional)
    print("\n3. Testing user creation without aadhar...")
    user_data_3 = {
        "fullname": "Bob Johnson",
        "email": "bob.johnson@example.com",
        "phone": "9876543212",
        "dob": "1988-12-25",
        "pin": 9012,
        "role": "user"
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=user_data_3)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✅ Success: User created without aadhar")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 4: User with neither email nor aadhar (both optional)
    print("\n4. Testing user creation without email and aadhar...")
    user_data_4 = {
        "fullname": "Alice Brown",
        "phone": "9876543213",
        "dob": "1995-03-10",
        "pin": 3456,
        "role": "user"
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=user_data_4)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✅ Success: User created without email and aadhar")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 5: User with empty email string (should be treated as None)
    print("\n5. Testing user creation with empty email string...")
    user_data_5 = {
        "fullname": "Charlie Wilson",
        "email": "",
        "phone": "9876543214",
        "aadhar": "",
        "dob": "1993-07-20",
        "pin": 7890,
        "role": "user"
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=user_data_5)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✅ Success: User created with empty email string")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Failed: {response.text}")

if __name__ == "__main__":
    test_user_creation()
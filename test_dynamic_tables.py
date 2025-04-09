import requests
import json
from pprint import pprint

# Base URL for the API
BASE_URL = "http://localhost:8000/api"

# Test user credentials
TEST_USER = {
    "email": "test@example.com",
    "password": "password123"
}

def get_auth_token():
    """Get authentication token for API requests"""
    response = requests.post(
        f"{BASE_URL}/auth/token",
        data={"username": TEST_USER["email"], "password": TEST_USER["password"]}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Failed to get auth token: {response.status_code}")
        print(response.json())
        return None

def create_test_table(token):
    """Create a test table with some columns"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Define table structure
    table_data = {
        "name": "customers",
        "description": "Customer information table",
        "columns": [
            {
                "name": "customer_id",
                "description": "Unique customer identifier",
                "column_type": "string",
                "is_required": True,
                "is_unique": True,
                "is_primary_key": True,
                "is_index": True,
                "max_length": 50
            },
            {
                "name": "name",
                "description": "Customer name",
                "column_type": "string",
                "is_required": True,
                "max_length": 100
            },
            {
                "name": "email",
                "description": "Customer email address",
                "column_type": "string",
                "is_required": True,
                "is_unique": True,
                "max_length": 100
            },
            {
                "name": "phone",
                "description": "Customer phone number",
                "column_type": "string",
                "is_required": False,
                "max_length": 20
            },
            {
                "name": "age",
                "description": "Customer age",
                "column_type": "integer",
                "is_required": False
            },
            {
                "name": "is_active",
                "description": "Whether the customer is active",
                "column_type": "boolean",
                "is_required": True,
                "default_value": "true"
            },
            {
                "name": "registration_date",
                "description": "Date when customer registered",
                "column_type": "date",
                "is_required": True
            },
            {
                "name": "notes",
                "description": "Additional notes about the customer",
                "column_type": "text",
                "is_required": False
            },
            {
                "name": "preferences",
                "description": "Customer preferences",
                "column_type": "json",
                "is_required": False
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/tables/",
        headers=headers,
        json=table_data
    )
    
    if response.status_code == 200:
        print("Table created successfully!")
        return response.json()
    else:
        print(f"Failed to create table: {response.status_code}")
        print(response.json())
        return None

def add_test_data(token, table_id):
    """Add some test data to the table"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Sample customer data
    customers = [
        {
            "data": {
                "customer_id": "CUST001",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "555-123-4567",
                "age": 35,
                "is_active": True,
                "registration_date": "2023-01-15",
                "notes": "VIP customer",
                "preferences": {
                    "newsletter": True,
                    "theme": "dark",
                    "categories": ["electronics", "books"]
                }
            }
        },
        {
            "data": {
                "customer_id": "CUST002",
                "name": "Jane Smith",
                "email": "jane.smith@example.com",
                "phone": "555-987-6543",
                "age": 28,
                "is_active": True,
                "registration_date": "2023-02-20",
                "preferences": {
                    "newsletter": False,
                    "theme": "light",
                    "categories": ["clothing", "home"]
                }
            }
        },
        {
            "data": {
                "customer_id": "CUST003",
                "name": "Bob Johnson",
                "email": "bob.johnson@example.com",
                "age": 42,
                "is_active": False,
                "registration_date": "2022-11-05",
                "notes": "Inactive since March 2023"
            }
        }
    ]
    
    results = []
    for customer in customers:
        response = requests.post(
            f"{BASE_URL}/tables/{table_id}/data",
            headers=headers,
            json=customer
        )
        
        if response.status_code == 200:
            print(f"Added customer {customer['data']['name']}")
            results.append(response.json())
        else:
            print(f"Failed to add customer {customer['data']['name']}: {response.status_code}")
            print(response.json())
    
    return results

def query_table_data(token, table_id):
    """Query data from the table with various filters"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get all rows
    response = requests.get(
        f"{BASE_URL}/tables/{table_id}/data",
        headers=headers
    )
    
    if response.status_code == 200:
        print("\nAll customers:")
        pprint(response.json())
    else:
        print(f"Failed to get customers: {response.status_code}")
        print(response.json())
    
    # Get active customers only
    filter_params = json.dumps({"is_active": True})
    response = requests.get(
        f"{BASE_URL}/tables/{table_id}/data?filter={filter_params}",
        headers=headers
    )
    
    if response.status_code == 200:
        print("\nActive customers only:")
        pprint(response.json())
    else:
        print(f"Failed to get active customers: {response.status_code}")
        print(response.json())
    
    # Sort by name
    response = requests.get(
        f"{BASE_URL}/tables/{table_id}/data?sort=name",
        headers=headers
    )
    
    if response.status_code == 200:
        print("\nCustomers sorted by name:")
        pprint(response.json())
    else:
        print(f"Failed to get sorted customers: {response.status_code}")
        print(response.json())

def update_customer(token, table_id, row_id):
    """Update a customer record"""
    headers = {"Authorization": f"Bearer {token}"}
    
    update_data = {
        "data": {
            "phone": "555-NEW-NUMBER",
            "age": 36,
            "notes": "VIP customer - Updated info"
        }
    }
    
    response = requests.put(
        f"{BASE_URL}/tables/{table_id}/data/{row_id}",
        headers=headers,
        json=update_data
    )
    
    if response.status_code == 200:
        print("\nCustomer updated successfully:")
        pprint(response.json())
    else:
        print(f"Failed to update customer: {response.status_code}")
        print(response.json())

def main():
    # Get authentication token
    token = get_auth_token()
    if not token:
        return
    
    # Create test table
    table = create_test_table(token)
    if not table:
        return
    
    table_id = table["id"]
    print(f"Created table with ID: {table_id}")
    
    # Add test data
    customers = add_test_data(token, table_id)
    if not customers:
        return
    
    # Query table data
    query_table_data(token, table_id)
    
    # Update a customer
    if customers:
        update_customer(token, table_id, customers[0]["id"])
    
    # Query again to see the update
    query_table_data(token, table_id)

if __name__ == "__main__":
    main()
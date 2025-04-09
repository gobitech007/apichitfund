# Dynamic Tables API

This API allows you to create and manage dynamic tables with custom columns and data. It provides a flexible way to define table structures and store data without having to modify the database schema.

## Features

- Create tables with custom columns
- Define column types, constraints, and validations
- Add, update, and delete rows of data
- Query data with filtering and sorting
- Full CRUD operations for tables, columns, and data

## Table of Contents

1. [API Endpoints](#api-endpoints)
2. [Table Definitions](#table-definitions)
3. [Column Types](#column-types)
4. [Data Operations](#data-operations)
5. [Examples](#examples)

## API Endpoints

All endpoints require authentication. You need to include an `Authorization` header with a valid JWT token.

### Table Management

- `POST /api/tables/` - Create a new table definition
- `GET /api/tables/` - List all table definitions
- `GET /api/tables/{table_id}` - Get a specific table definition
- `PUT /api/tables/{table_id}` - Update a table definition
- `DELETE /api/tables/{table_id}` - Delete a table definition

### Column Management

- `POST /api/tables/{table_id}/columns` - Add a column to a table
- `GET /api/tables/{table_id}/columns` - List all columns in a table
- `GET /api/tables/{table_id}/columns/{column_id}` - Get a specific column
- `PUT /api/tables/{table_id}/columns/{column_id}` - Update a column
- `DELETE /api/tables/{table_id}/columns/{column_id}` - Delete a column

### Data Management

- `POST /api/tables/{table_id}/data` - Add a row of data to a table
- `GET /api/tables/{table_id}/data` - List all rows in a table
- `GET /api/tables/{table_id}/data/{row_id}` - Get a specific row
- `PUT /api/tables/{table_id}/data/{row_id}` - Update a row
- `DELETE /api/tables/{table_id}/data/{row_id}` - Delete a row

## Table Definitions

When creating a table, you need to provide a name, optional description, and a list of column definitions.

Example:

```json
{
  "name": "customers",
  "description": "Customer information table",
  "columns": [
    {
      "name": "customer_id",
      "description": "Unique customer identifier",
      "column_type": "string",
      "is_required": true,
      "is_unique": true,
      "is_primary_key": true,
      "is_index": true,
      "max_length": 50
    },
    {
      "name": "name",
      "description": "Customer name",
      "column_type": "string",
      "is_required": true,
      "max_length": 100
    },
    // More columns...
  ]
}
```

## Column Types

The following column types are supported:

- `string` - Text with a maximum length
- `integer` - Whole numbers
- `float` - Decimal numbers
- `boolean` - True/false values
- `date` - Date values (YYYY-MM-DD)
- `datetime` - Date and time values
- `text` - Long text without length restrictions
- `json` - JSON objects or arrays

## Column Properties

Each column can have the following properties:

- `name` - The name of the column (required)
- `description` - A description of the column (optional)
- `column_type` - The data type of the column (required)
- `is_required` - Whether the column is required (default: false)
- `is_unique` - Whether the column values must be unique (default: false)
- `is_primary_key` - Whether the column is a primary key (default: false)
- `is_index` - Whether the column should be indexed (default: false)
- `default_value` - The default value for the column (optional)
- `max_length` - The maximum length for string/text columns (optional)

## Data Operations

### Adding Data

When adding data to a table, you need to provide a JSON object with the column names and values:

```json
{
  "data": {
    "customer_id": "CUST001",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "age": 35,
    "is_active": true,
    "registration_date": "2023-01-15"
  }
}
```

### Querying Data

You can filter and sort data when querying:

- `filter` - JSON string of filter criteria
- `sort` - Field to sort by
- `sort_dir` - Sort direction (asc or desc)
- `page` - Page number for pagination
- `page_size` - Number of items per page

Example:

```
GET /api/tables/1/data?filter={"is_active":true}&sort=name&sort_dir=asc&page=1&page_size=10
```

## Examples

### Creating a Table

```python
import requests

headers = {"Authorization": f"Bearer {token}"}

table_data = {
    "name": "products",
    "description": "Product catalog",
    "columns": [
        {
            "name": "product_id",
            "description": "Product identifier",
            "column_type": "string",
            "is_required": True,
            "is_unique": True,
            "is_primary_key": True
        },
        {
            "name": "name",
            "description": "Product name",
            "column_type": "string",
            "is_required": True
        },
        {
            "name": "price",
            "description": "Product price",
            "column_type": "float",
            "is_required": True
        }
    ]
}

response = requests.post(
    "http://localhost:8000/api/tables/",
    headers=headers,
    json=table_data
)

print(response.json())
```

### Adding Data

```python
import requests

headers = {"Authorization": f"Bearer {token}"}

product_data = {
    "data": {
        "product_id": "PROD001",
        "name": "Smartphone",
        "price": 599.99
    }
}

response = requests.post(
    "http://localhost:8000/api/tables/1/data",
    headers=headers,
    json=product_data
)

print(response.json())
```

### Querying Data

```python
import requests
import json

headers = {"Authorization": f"Bearer {token}"}

# Filter for products with price > 500
filter_params = json.dumps({"price": {"$gt": 500}})

response = requests.get(
    f"http://localhost:8000/api/tables/1/data?filter={filter_params}&sort=price&sort_dir=desc",
    headers=headers
)

print(response.json())
```

## Running the Test Script

A test script is provided to demonstrate the API functionality:

```bash
python test_dynamic_tables.py
```

This script will:
1. Create a test table with various column types
2. Add sample data to the table
3. Query the data with different filters
4. Update a record
5. Query again to show the updated data

Make sure you have a test user in the system before running the script.
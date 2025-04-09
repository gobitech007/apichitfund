# MyChitFund API

A FastAPI-based API for managing users in the MyChitFund application.

## Features

- User management (CRUD operations)
- Authentication with JWT tokens
- Auto-generated secure passwords
- MySQL database with SQLite fallback

## Installation

1. Clone the repository
2. Install dependencies using the setup script:

```bash
# Basic installation
python setup.py

# With debugging tools
python setup.py --with-debug
```

Alternatively, you can install dependencies manually:

```bash
# Core dependencies only
pip install -r requirements.txt

# For debugging with VS Code
pip install debugpy
```

## Running the Application

### Development Mode

```bash
python run.py --mode dev
```

### Debug Mode

```bash
python run.py --mode debug
```

### Production Mode

```bash
python run.py --mode prod
```

## API Documentation

Once the server is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /auth/token` - Get access token (OAuth2 form)
- `POST /auth/login` - Login with email/password
- `GET /auth/me` - Get current user info

### User Management

- `GET /users/` - List all users
- `POST /users/` - Create a new user
- `GET /users/{user_id}` - Get user by ID
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user

### Payments and Chits

- `GET /payments/chits/` - List all chits
- `GET /payments/chits/user/{user_id}` - List all chits for a specific user
- `POST /payments/chit_users/` - Create a new chit user association
- `PATCH /payments/chits/{chit_id}` - Update amount for a specific chit

#### Chit User Creation

To create a new chit user association:

```bash
POST /payments/chit_users/
```

Request body:
```json
{
  "user_id": 123,  # ID of an existing user
  "chit_no": 456,  # Chit number to associate with the user
  "amount": 10000  # Optional initial amount
}
```

Response:
```json
{
  "chit_id": 789,  # Generated chit ID
  "user_id": 123,
  "chit_no": 456,
  "amount": 10000
}
```

This endpoint will verify that the user exists before creating the association.

#### Chit Amount Update

To update the amount for a specific chit:

```bash
PATCH /payments/chits/{chit_id}
```

Request body:
```json
{
  "amount": 15000  # New amount for the chit
}
```

Response:
```json
{
  "chit_id": 789,
  "user_id": 123,
  "chit_no": 456,
  "amount": 15000
}
```

This endpoint will verify that the chit exists before updating the amount.

## Development

### Debugging with VS Code

To enable remote debugging with VS Code:

1. Uncomment the debugpy lines in `debug.py`
2. Run the application in debug mode
3. Connect VS Code to the debugger at `localhost:5678`
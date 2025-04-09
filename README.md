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

#### Payment Processing

- `POST /payments/process/` - Process a new payment
- `GET /payments/` - Get all payments
- `GET /payments/{pay_id}` - Get a specific payment by ID
- `GET /payments/user/{user_id}` - Get all payments for a specific user

#### Pay Details Management

- `POST /payments/chit_users/{chit_id}/pay_details/` - Create pay details for a chit
- `GET /payments/chit_users/{chit_id}/pay_details/` - Get pay details for a chit
- `PATCH /payments/chit_users/{chit_id}/pay_details/{week}` - Update pay detail status

To create pay details for a chit:

```bash
POST /payments/chit_users/{chit_id}/pay_details/
```

This endpoint will:
1. Verify that the chit exists
2. Check if pay details already exist for this chit (to prevent duplicates)
3. Create 54 weekly pay detail records with is_paid='N'

Response:
```json
[
  {
    "chit_id": 789,
    "week": 1,
    "is_paid": "N"
  },
  {
    "chit_id": 789,
    "week": 2,
    "is_paid": "N"
  },
  // ... and so on for all 54 weeks
]
```

If pay details already exist for the chit, the API will return a 400 Bad Request error.

To update a pay detail status:

```bash
PATCH /payments/chit_users/{chit_id}/pay_details/{week}?is_paid=Y
```

This endpoint will:
1. Verify that the week number is valid (1-54)
2. Verify that the is_paid value is valid ('Y' or 'N')
3. Check if the pay detail exists
4. If the pay detail is already marked as paid (is_paid='Y') and the request is to mark it as paid again, the API will return the current record without making changes
5. Otherwise, update the pay detail status

Response:
```json
{
  "details_id": 123,
  "chit_id": 789,
  "week": 3,
  "is_paid": "Y"
}
```

This validation ensures that unnecessary updates are avoided when a payment is already marked as paid.

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

#### Payment Processing

To process a new payment:

```bash
POST /payments/process/
```

Request body:
```json
{
  "user_id": 123,
  "chit_no": 456,
  "amount": 5000,
  "week_no": 3,
  "pay_type": "card",
  "pay_card": "credit",
  "pay_card_name": "John Doe",
  "pay_expiry_no": "12/25"
}
```

For UPI payments:
```json
{
  "user_id": 123,
  "chit_no": 456,
  "amount": 5000,
  "week_no": 3,
  "pay_type": "UPI",
  "pay_qr": "user@upi"
}
```

Response:
```json
{
  "pay_id": 1,
  "user_id": 123,
  "chit_no": 456,
  "amount": 5000,
  "week_no": 3,
  "pay_type": "card",
  "pay_card": "credit",
  "pay_card_name": "John Doe",
  "pay_expiry_no": "12/25",
  "pay_qr": null,
  "created_at": "2023-06-15T10:30:00",
  "updated_at": "2023-06-15T10:30:00",
  "created_by": 789,
  "updated_by": 789
}
```

This endpoint will:
1. Validate the payment data based on the payment type
2. Create a payment record with the current user as created_by and updated_by
3. Update the corresponding pay_detail to mark the week as paid

## Development

### Debugging with VS Code

To enable remote debugging with VS Code:

1. Uncomment the debugpy lines in `debug.py`
2. Run the application in debug mode
3. Connect VS Code to the debugger at `localhost:5678`
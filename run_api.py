import uvicorn

print("""
=======================================================
MyChitFund API Server
=======================================================

Starting the API server...

Once running, you can access:
- API Documentation (Swagger UI): http://localhost:8000/docs
- Alternative Documentation (ReDoc): http://localhost:8000/redoc
- API Root: http://localhost:8000/

Available endpoints:
- GET /users/ - List all users
- POST /users/ - Create a new user
- GET /users/{user_id} - Get a specific user
- PUT /users/{user_id} - Update a user
- DELETE /users/{user_id} - Delete a user

Press Ctrl+C to stop the server
=======================================================
""")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
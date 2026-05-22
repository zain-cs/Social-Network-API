# Testing Guide

## How to Test the API

1. Start the server: `uvicorn main:app --reload`
2. Open Swagger UI: http://localhost:8000/docs
3. Register a user via POST /register
4. Login via POST /login and copy the token
5. Click Authorize and paste your token
6. Now test any endpoint!

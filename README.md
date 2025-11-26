# Secure Inventory & Sales Management System - Backend

## Tech Stack
- Python (FastAPI)
- MongoDB (Motor)

## Setup
1. Create a virtual environment: `python -m venv venv`
2. Activate it: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Create `.env` file with:
   ```
   PORT=8000
   DB_HOST=localhost
   DB_USER=
   DB_PASS=
   DB_NAME=inventory_system
   JWT_SECRET=your_secret
   COOKIE_SECRET=your_cookie_secret
   ```
5. Run: `uvicorn src.main:app --reload`

## Security Features
- JWT in HttpOnly cookies
- RBAC (Admin/Employee)
- Input validation

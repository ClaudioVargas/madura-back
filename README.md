madura_back

Backend template: FastAPI + Uvicorn + SQLite + SQLAlchemy

Run locally:
1. python -m venv .venv
2. .\.venv\Scripts\activate
3. pip install -r requirements.txt
4. uvicorn main:app --reload --port 8000

Endpoints:
- /docs (OpenAPI)
- /redoc

Notes:
- Uses JWT auth (python-jose). Passwords hashed with passlib (bcrypt).
- DB: SQLite file located at database.db in project root.

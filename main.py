from fastapi import FastAPI
from database.db import get_connection
from routes.auth import router as auth_router
from routes.expenses import router as expense_router

app = FastAPI()

app.include_router(auth_router)

app.include_router(expense_router)

@app.get("/")
def home():
    try:
        conn = get_connection()
        conn.close()

        return {
            "message": "Connected to PostgreSQL successfully!"
        }

    except Exception as e:
        return {
            "error": str(e)
        }
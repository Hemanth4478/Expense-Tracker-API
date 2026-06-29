from fastapi import APIRouter, HTTPException
from models.user import UserCreate
from database.db import get_connection
from utilies.security import hash_password
from utilies.security import verify_password
from utilies.auth_utiles import create_access_token
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from utilies.auth_utiles import verify_token

security = HTTPBearer()
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)



@router.post("/signup")
def signup(user: UserCreate):

    conn = get_connection()
    cursor = conn.cursor()

    # Check if username already exists
    cursor.execute(
        "SELECT * FROM users WHERE username = %s",
        (user.username,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        conn.close()

        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    # Hash password
    hashed_password = hash_password(user.password)

    # Insert new user
    cursor.execute(
        """
        INSERT INTO users (username, password)
        VALUES (%s, %s)
        """,
        (user.username, hashed_password)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "success": True,
        "message": "User registered successfully"
    }


@router.post("/login")
def login(user: UserCreate):

    conn = get_connection()
    cursor = conn.cursor()

    # Check user
    cursor.execute(
        "SELECT * FROM users WHERE username = %s",
        (user.username,)
    )

    existing_user = cursor.fetchone()

    if not existing_user:
        cursor.close()
        conn.close()

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # Verify password
    if not verify_password(
        user.password,
        existing_user[2]
    ):
        cursor.close()
        conn.close()

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_access_token(
        {
            "user_id": existing_user[0],
            "username": existing_user[1]
        }
    )

    cursor.close()
    conn.close()

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/profile")
def profile(credentials=Depends(security)):

    token = credentials.credentials

    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    return {
        "success": True,
        "user": {
            "id": payload["user_id"],
            "username": payload["username"]
        }
    }

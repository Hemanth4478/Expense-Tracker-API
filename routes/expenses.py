from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer

from database.db import get_connection
from models.expense import ExpenseCreate
from utilies.auth_utiles import verify_token

router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"]
)

security = HTTPBearer()

@router.post("/")
def add_expense(
    expense: ExpenseCreate,
    credentials=Depends(security)
):
    # Get JWT token
    token = credentials.credentials

    # Decode token
    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user_id = payload["user_id"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO expenses
        (title, amount, category, user_id)
        VALUES (%s, %s, %s, %s)
        """,
        (
            expense.title,
            expense.amount,
            expense.category,
            user_id
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "message": "Expense added successfully"
    }

@router.get("/")
def get_expenses(credentials=Depends(security)):

    token = credentials.credentials

    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user_id = payload["user_id"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, title, amount, category, created_at
        FROM expenses
        WHERE user_id = %s
        ORDER BY created_at DESC
        """,
        (user_id,)
    )

    expenses = cursor.fetchall()

    cursor.close()
    conn.close()

    result = []

    for expense in expenses:
        result.append({
            "id": expense[0],
            "title": expense[1],
            "amount": float(expense[2]),
            "category": expense[3],
            "created_at": expense[4]
        })

    return result

@router.get("one,{id}")
def get_expenses(id:int,credentials=Depends(security)):

    token = credentials.credentials

    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user_id = payload["user_id"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, title, amount, category, created_at
        FROM expenses
        WHERE user_id = %s and id=%s
        """,
        (user_id,id)
    )

    expense = cursor.fetchone()

    cursor.close()
    conn.close()

    if not expense:
        raise HTTPException(status_code=401,detail="No data found")

    
    return {
            "id": expense[0],
            "title": expense[1],
            "amount": float(expense[2]),
            "category": expense[3],
            "created_at": expense[4]
        }

@router.put("/{expense_id}")
def update_expense(
    expense_id: int,
    expense: ExpenseCreate,
    credentials=Depends(security)
):

    token = credentials.credentials

    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user_id = payload["user_id"]

    conn = get_connection()
    cursor = conn.cursor()

    # Check ownership
    cursor.execute(
        """
        SELECT id
        FROM expenses
        WHERE id = %s
        AND user_id = %s
        """,
        (expense_id, user_id)
    )

    existing_expense = cursor.fetchone()

    if not existing_expense:
        cursor.close()
        conn.close()

        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    # Update expense
    cursor.execute(
        """
        UPDATE expenses
        SET title = %s,
            amount = %s,
            category = %s
        WHERE id = %s
        """,
        (
            expense.title,
            expense.amount,
            expense.category,
            expense_id
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "message": "Expense updated successfully"
    }

@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    credentials=Depends(security)
):

    token = credentials.credentials

    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user_id = payload["user_id"]

    conn = get_connection()
    cursor = conn.cursor()

    # Check ownership
    cursor.execute(
        """
        SELECT id
        FROM expenses
        WHERE id = %s
        AND user_id = %s
        """,
        (expense_id, user_id)
    )

    expense = cursor.fetchone()

    if not expense:
        cursor.close()
        conn.close()

        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    # Delete expense
    cursor.execute(
        """
        DELETE FROM expenses
        WHERE id = %s
        """,
        (expense_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "message": "Expense deleted successfully"
    }


@router.get("/total")
def total(
    credentials=Depends(security)
):

    token = credentials.credentials

    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user_id = payload["user_id"]

    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        """
        select sum(amount) from expenses where user_id=%s
        """,
        (user_id)
    )

    total = cursor.fetchone()[0]



    cursor.close()
    conn.close()

    return {
        "total_expense": total
    }

@router.get("/category-summary")
def category_summary(credentials=Depends(security)):

    token = credentials.credentials

    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user_id = payload["user_id"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT category, SUM(amount)
        FROM expenses
        WHERE user_id = %s
        GROUP BY category
        ORDER BY category;
        """,
        (user_id,)
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    result = []

    for row in rows:
        result.append({
            "category": row[0],
            "total": float(row[1])
        })

    return result

@router.get("/highest")
def highest_expense(credentials=Depends(security)):

    token = credentials.credentials

    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user_id = payload["user_id"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, title, amount, category, created_at
        FROM expenses
        WHERE user_id = %s
        ORDER BY amount DESC
        LIMIT 1
        """,
        (user_id,)
    )

    expense = cursor.fetchone()

    cursor.close()
    conn.close()

    if not expense:
        raise HTTPException(
            status_code=404,
            detail="No expenses found"
        )

    return {
        "id": expense[0],
        "title": expense[1],
        "amount": float(expense[2]),
        "category": expense[3],
        "created_at": expense[4]
    }

@router.get("/lowest")
def lowest_expense(credentials=Depends(security)):

    token = credentials.credentials

    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user_id = payload["user_id"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, title, amount, category, created_at
        FROM expenses
        WHERE user_id = %s
        ORDER BY amount Asc
        LIMIT 1
        """,
        (user_id,)
    )

    expense = cursor.fetchone()

    cursor.close()
    conn.close()

    if not expense:
        raise HTTPException(
            status_code=404,
            detail="No expenses found"
        )

    return {
        "id": expense[0],
        "title": expense[1],
        "amount": float(expense[2]),
        "category": expense[3],
        "created_at": expense[4]
    }

@router.get("/monthly-report")
def monthly_report(credentials=Depends(security)):

    token = credentials.credentials

    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user_id = payload["user_id"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            DATE_TRUNC('month', created_at) AS month,
            SUM(amount) AS total
        FROM expenses
        WHERE user_id = %s
        GROUP BY month
        ORDER BY month;
        """,
        (user_id,)
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    result = []

    for row in rows:
        result.append({
            "month": row[0].strftime("%Y-%m"),
            "total": float(row[1])
        })

    return result


@router.get("/limits")
def get_expenses(
    page: int = 1,
    limit: int = 5,
    credentials=Depends(security)
):
    token = credentials.credentials

    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user_id = payload["user_id"]

    offset = (page - 1) * limit

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, title, amount, category, created_at
        FROM expenses
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """,
        (user_id, limit, offset)
    )

    expenses = cursor.fetchall()

    cursor.close()
    conn.close()

    result = []

    for expense in expenses:
        result.append({
            "id": expense[0],
            "title": expense[1],
            "amount": float(expense[2]),
            "category": expense[3],
            "created_at": expense[4]
        })

    return  {
        "page": page,
        "limit": limit,
        "total_records": len(result),
        "expenses": result
    }  

@router.get("/")
def search_expenses(
    page: int = 1,
    limit: int = 5,
    search: str = "",
    credentials=Depends(security)
):

    token = credentials.credentials

    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user_id = payload["user_id"]

    offset = (page - 1) * limit

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            title,
            amount,
            category,
            created_at
        FROM expenses
        WHERE user_id=%s
        AND title ILIKE %s
        ORDER BY created_at DESC
        LIMIT %s
        OFFSET %s
        """,
        (
            user_id,
            f"%{search}%",
            limit,
            offset
        )
    )

    expenses = cursor.fetchall()

    cursor.close()
    conn.close()

    result = []

    for expense in expenses:

        result.append(
            {
                "id": expense[0],
                "title": expense[1],
                "amount": float(expense[2]),
                "category": expense[3],
                "created_at": expense[4]
            }
        )

    return {
        "page": page,
        "limit": limit,
        "search": search,
        "total_records": len(result),
        "expenses": result
    }
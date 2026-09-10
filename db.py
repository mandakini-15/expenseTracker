import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).parent / "expenses.db"

CATEGORIES = [
    "Food",
    "Shopping",
    "Transport",
    "Bills",
    "Entertainment",
    "Other",
]


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                note TEXT
            )
            """
        )


def add_expense(date, category, amount, note=""):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO expenses (date, category, amount, note) VALUES (?, ?, ?, ?)",
            (date, category, amount, note),
        )


def delete_expense(expense_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))


def get_all_expenses():
    with get_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM expenses ORDER BY date DESC, id DESC", conn)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df

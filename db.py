from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

CATEGORIES = [
    "Food",
    "Shopping",
    "Transport",
    "Bills",
    "Entertainment",
    "Other",
]

_engine = None


def _database_url():
    """Use a cloud Postgres DB if configured via secrets, otherwise a local SQLite file."""
    try:
        url = st.secrets["database"]["url"]
        if url:
            return url
    except Exception:
        pass
    return f"sqlite:///{Path(__file__).parent / 'expenses.db'}"


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(_database_url())
    return _engine


def init_db():
    engine = get_engine()
    id_column = (
        "id INTEGER PRIMARY KEY AUTOINCREMENT"
        if engine.dialect.name == "sqlite"
        else "id SERIAL PRIMARY KEY"
    )
    with engine.begin() as conn:
        conn.execute(
            text(
                f"""
                CREATE TABLE IF NOT EXISTS expenses (
                    {id_column},
                    date TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    note TEXT
                )
                """
            )
        )


def add_expense(date, category, amount, note=""):
    with get_engine().begin() as conn:
        conn.execute(
            text(
                "INSERT INTO expenses (date, category, amount, note) "
                "VALUES (:date, :category, :amount, :note)"
            ),
            {"date": date, "category": category, "amount": amount, "note": note},
        )


def delete_expense(expense_id):
    with get_engine().begin() as conn:
        conn.execute(text("DELETE FROM expenses WHERE id = :id"), {"id": expense_id})


def get_all_expenses():
    df = pd.read_sql_query(
        text("SELECT * FROM expenses ORDER BY date DESC, id DESC"), get_engine()
    )
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df

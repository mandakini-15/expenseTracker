# Expense Tracker

A simple, beginner-friendly expense tracker built with Streamlit and SQLite.

## Features

- Add expenses with a date, category, and amount
- Data stored locally in a SQLite database (`expenses.db`)
- Summary stats: total spent, transaction count, average per day
- Pie chart of spending by category
- Bar chart of monthly spending
- Delete expenses you no longer need

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

Then open the local URL Streamlit prints (usually http://localhost:8501).

# Expense Tracker

A simple, beginner-friendly expense tracker built with Streamlit.

## Features

- Add expenses with a date, category, and amount
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

## Run locally

```bash
streamlit run app.py
```

Then open the local URL Streamlit prints (usually http://localhost:8501).

With no extra config, data is stored locally in a SQLite file (`expenses.db`).

## Using it on your phone (deploy to Streamlit Community Cloud)

This gets you a public URL you can open from your phone's browser (and "Add
to Home Screen" so it behaves like an app icon).

### 1. Set up a free cloud database (so your data persists)

Streamlit Community Cloud's filesystem resets on redeploy/sleep, so plain
SQLite won't keep your data. Instead, create a free Postgres database:

1. Sign up at [supabase.com](https://supabase.com) (or [neon.tech](https://neon.tech)) and create a new project.
2. Find your database connection string (Supabase: Project Settings → Database → Connection string → URI).

### 2. Deploy the app

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Click "New app", pick this repo, branch, and set the main file to `app.py`.
3. Before/after deploying, open the app's "Settings → Secrets" and paste:
   ```toml
   [database]
   url = "postgresql://postgres:YOUR_PASSWORD@YOUR_HOST:5432/postgres"
   ```
   (see `.streamlit/secrets.toml.example` for reference)
4. Deploy. You'll get a URL like `yourapp.streamlit.app` — open it on your phone.

If you skip the secrets step, the app still works, but falls back to local
SQLite storage which won't persist reliably on the cloud.

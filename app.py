from datetime import date

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from db import CATEGORIES, add_expense, delete_expense, get_all_expenses, init_db

st.set_page_config(page_title="Expense Tracker", page_icon="💵", layout="centered")
init_db()

st.title("💵 Expense Tracker")
st.caption("Log your spending and automatically see where your money goes.")

# --- Add expense form ---
with st.expander("➕ Add an expense", expanded=False):
    with st.form("add_expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        expense_date = col1.date_input("Date", value=date.today())
        category = col2.selectbox("Category", CATEGORIES)
        amount = st.number_input("Amount ($)", min_value=0.0, step=1.0, format="%.2f")
        note = st.text_input("Note (optional)")
        submitted = st.form_submit_button("Add expense")
        if submitted:
            if amount <= 0:
                st.warning("Amount must be greater than 0.")
            else:
                add_expense(expense_date.isoformat(), category, amount, note)
                st.success("Expense added.")
                st.rerun()

df = get_all_expenses()

if df.empty:
    st.info("No expenses yet. Add your first one above.")
    st.stop()

today = pd.Timestamp(date.today())
this_month_df = df[(df["date"].dt.month == today.month) & (df["date"].dt.year == today.year)]

tab_month, tab_all, tab_category = st.tabs(["This Month", "All Time", "By Category"])


def render_summary(data: pd.DataFrame):
    total_spent = data["amount"].sum()
    num_transactions = len(data)
    num_days = max((data["date"].max() - data["date"].min()).days + 1, 1) if not data.empty else 1
    avg_per_day = total_spent / num_days

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Spent", f"${total_spent:,.0f}")
    col2.metric("Transactions", num_transactions)
    col3.metric("Avg per day", f"${avg_per_day:,.0f}")

    if data.empty:
        st.info("No expenses in this period.")
        return

    st.subheader("Spending by Category")
    category_totals = data.groupby("category")["amount"].sum().sort_values(ascending=False)

    fig, ax = plt.subplots()
    ax.pie(category_totals, labels=category_totals.index, autopct="%1.0f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

    st.subheader("Recent Transactions")
    st.dataframe(
        data[["date", "category", "amount", "note"]].assign(date=data["date"].dt.date),
        hide_index=True,
        use_container_width=True,
    )


with tab_month:
    render_summary(this_month_df)

with tab_all:
    render_summary(df)

    st.subheader("Monthly Spending")
    monthly = df.copy()
    monthly["month"] = monthly["date"].dt.to_period("M").astype(str)
    monthly_totals = monthly.groupby("month")["amount"].sum().sort_index()

    fig, ax = plt.subplots()
    ax.bar(monthly_totals.index, monthly_totals.values, color="#4CAF50")
    ax.set_ylabel("Amount ($)")
    ax.set_xlabel("Month")
    ax.set_title("Spending by Month")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig)

with tab_category:
    category_totals = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    st.subheader("Total Spending by Category")

    fig, ax = plt.subplots()
    category_totals.plot(kind="bar", color="#4CAF50", ax=ax)
    ax.set_title("Spending by Category")
    ax.set_ylabel("Amount ($)")
    ax.set_xlabel("Category")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig)

    st.dataframe(category_totals.reset_index().rename(columns={"amount": "Total"}), hide_index=True)

# --- Delete an expense ---
with st.expander("🗑️ Delete an expense"):
    options = {
        f"{row.date.date()} · {row.category} · ${row.amount:,.2f}": row.id
        for row in df.itertuples()
    }
    if options:
        selected_label = st.selectbox("Select an expense to delete", list(options.keys()))
        if st.button("Delete", type="secondary"):
            delete_expense(options[selected_label])
            st.success("Expense deleted.")
            st.rerun()

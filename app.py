from datetime import date

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from db import CATEGORIES, CURRENCIES, add_expense, delete_expense, get_all_expenses, init_db

st.set_page_config(page_title="Expense Tracker", page_icon="💵", layout="centered")
init_db()

st.title("💵 Expense Tracker")
st.caption("Log your spending and automatically see where your money goes.")


def format_amount(amount, currency):
    symbol = CURRENCIES.get(currency, "")
    return f"{symbol}{amount:,.2f}" if symbol else f"{amount:,.2f} {currency}"


def currency_options():
    return [f"{code} ({symbol})" for code, symbol in CURRENCIES.items()]


def currency_from_option(option):
    return option.split(" ")[0]


# --- Add expense form ---
with st.expander("➕ Add an expense", expanded=False):
    with st.form("add_expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        expense_date = col1.date_input("Date", value=date.today())
        category = col2.selectbox("Category", CATEGORIES)
        col3, col4 = st.columns(2)
        amount = col3.number_input("Amount", min_value=0.0, step=1.0, format="%.2f")
        currency_option = col4.selectbox("Currency", currency_options())
        note = st.text_input("Note (optional)")
        submitted = st.form_submit_button("Add expense")
        if submitted:
            if amount <= 0:
                st.warning("Amount must be greater than 0.")
            else:
                add_expense(
                    expense_date.isoformat(),
                    category,
                    amount,
                    currency_from_option(currency_option),
                    note,
                )
                st.success("Expense added.")
                st.rerun()

df = get_all_expenses()

if df.empty:
    st.info("No expenses yet. Add your first one above.")
    st.stop()

today = pd.Timestamp(date.today())
this_month_df = df[(df["date"].dt.month == today.month) & (df["date"].dt.year == today.year)]

tab_month, tab_all, tab_category = st.tabs(["This Month", "All Time", "By Category"])


def pick_currency(data: pd.DataFrame, key: str):
    """If the data spans multiple currencies, let the user pick which one to total/chart."""
    currencies_present = data["currency"].value_counts().index.tolist()
    if len(currencies_present) <= 1:
        return currencies_present[0]
    return st.selectbox(
        "Show totals in",
        currencies_present,
        format_func=lambda c: f"{c} ({CURRENCIES.get(c, c)})",
        key=key,
    )


def render_summary(data: pd.DataFrame, key: str):
    if data.empty:
        st.info("No expenses in this period.")
        return None, None

    currency = pick_currency(data, key)
    filtered = data[data["currency"] == currency]

    total_spent = filtered["amount"].sum()
    num_transactions = len(filtered)
    num_days = max((filtered["date"].max() - filtered["date"].min()).days + 1, 1)
    avg_per_day = total_spent / num_days

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Spent", format_amount(total_spent, currency))
    col2.metric("Transactions", num_transactions)
    col3.metric("Avg per day", format_amount(avg_per_day, currency))

    st.subheader("Spending by Category")
    category_totals = filtered.groupby("category")["amount"].sum().sort_values(ascending=False)

    fig, ax = plt.subplots()
    ax.pie(category_totals, labels=category_totals.index, autopct="%1.0f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

    st.subheader("Recent Transactions")
    display_df = data[["date", "category", "amount", "currency", "note"]].copy()
    display_df["date"] = display_df["date"].dt.date
    display_df["amount"] = data.apply(lambda r: format_amount(r["amount"], r["currency"]), axis=1)
    st.dataframe(
        display_df.drop(columns="currency"),
        hide_index=True,
        use_container_width=True,
    )

    return currency, filtered


with tab_month:
    render_summary(this_month_df, key="month_currency")

with tab_all:
    currency, filtered = render_summary(df, key="all_currency")

    if filtered is not None:
        st.subheader("Monthly Spending")
        monthly = filtered.copy()
        monthly["month"] = monthly["date"].dt.to_period("M").astype(str)
        monthly_totals = monthly.groupby("month")["amount"].sum().sort_index()

        fig, ax = plt.subplots()
        ax.bar(monthly_totals.index, monthly_totals.values, color="#4CAF50")
        ax.set_ylabel(f"Amount ({currency})")
        ax.set_xlabel("Month")
        ax.set_title("Spending by Month")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig)

with tab_category:
    currency = pick_currency(df, key="category_currency")
    filtered = df[df["currency"] == currency]

    category_totals = filtered.groupby("category")["amount"].sum().sort_values(ascending=False)
    st.subheader("Total Spending by Category")

    fig, ax = plt.subplots()
    category_totals.plot(kind="bar", color="#4CAF50", ax=ax)
    ax.set_title("Spending by Category")
    ax.set_ylabel(f"Amount ({currency})")
    ax.set_xlabel("Category")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig)

    st.dataframe(category_totals.reset_index().rename(columns={"amount": "Total"}), hide_index=True)

# --- Delete an expense ---
with st.expander("🗑️ Delete an expense"):
    options = {
        f"{row.date.date()} · {row.category} · {format_amount(row.amount, row.currency)}": row.id
        for row in df.itertuples()
    }
    if options:
        selected_label = st.selectbox("Select an expense to delete", list(options.keys()))
        if st.button("Delete", type="secondary"):
            delete_expense(options[selected_label])
            st.success("Expense deleted.")
            st.rerun()

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="KizunAI Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 KizunAI Inventory Dashboard")

try:

    df = pd.read_csv("data/inventory.csv")

    st.subheader("Inventory Overview")

    total_products = len(df)

    total_quantity = df["quantity"].sum()

    total_cost = (
        df["cost"] * df["quantity"]
    ).sum()

    total_value = (
        df["selling_price"] * df["quantity"]
    ).sum()

    total_profit = total_value - total_cost

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Products",
        total_products
    )

    col2.metric(
        "Quantity",
        int(total_quantity)
    )

    col3.metric(
        "Cost AED",
        f"{total_cost:.2f}"
    )

    col4.metric(
        "Value AED",
        f"{total_value:.2f}"
    )

    col5.metric(
        "Profit AED",
        f"{total_profit:.2f}"
    )

    st.divider()

    st.subheader("Inventory Table")

    st.dataframe(
        df,
        use_container_width=True
    )

except FileNotFoundError:

    st.warning(
        "No inventory found yet. Scan your first card."
    )
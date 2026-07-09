import streamlit as st
import pandas as pd

from services.portfolio_analytics import (
    calculate_portfolio_value,
    calculate_portfolio_cost,
    calculate_portfolio_profit,
    calculate_portfolio_margin
)


st.set_page_config(
    page_title="KizunAI Dashboard",
    page_icon="📊",
    layout="wide"
)


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.title("📊 KizunAI Portfolio Dashboard")

st.caption(
    "Real-time inventory analytics for your TCG collection."
)


try:

    # --------------------------------------------------
    # LOAD INVENTORY
    # --------------------------------------------------

    df = pd.read_csv("data/inventory.csv")

    if df.empty:
        st.warning(
            "Your inventory is empty. Scan your first card to begin."
        )
        st.stop()


    # --------------------------------------------------
    # CLEAN NUMERIC DATA
    # --------------------------------------------------

    numeric_columns = [
        "quantity",
        "cost",
        "selling_price"
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        ).fillna(0)


    # --------------------------------------------------
    # PORTFOLIO ANALYTICS
    # --------------------------------------------------

    total_products = len(df)

    total_quantity = int(
        df["quantity"].sum()
    )

    total_cost = calculate_portfolio_cost()

    total_value = calculate_portfolio_value()

    total_profit = calculate_portfolio_profit()

    portfolio_margin = calculate_portfolio_margin()


    # --------------------------------------------------
    # PORTFOLIO OVERVIEW
    # --------------------------------------------------

    st.subheader("Portfolio Overview")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            label="Collection Value",
            value=f"{total_value:,.2f} AED"
        )

    with col2:

        st.metric(
            label="Inventory Cost",
            value=f"{total_cost:,.2f} AED"
        )

    with col3:

        st.metric(
            label="Potential Profit",
            value=f"{total_profit:,.2f} AED"
        )


    col4, col5, col6 = st.columns(3)

    with col4:

        st.metric(
            label="Portfolio Margin",
            value=f"{portfolio_margin:.2f}%"
        )

    with col5:

        st.metric(
            label="Products",
            value=total_products
        )

    with col6:

        st.metric(
            label="Total Units",
            value=total_quantity
        )


    st.divider()


    # --------------------------------------------------
    # PORTFOLIO DISTRIBUTION
    # --------------------------------------------------

    st.subheader("Portfolio Distribution")

    chart_col1, chart_col2 = st.columns(2)


    # --------------------------------------------------
    # VALUE BY TCG
    # --------------------------------------------------

    with chart_col1:

        st.markdown("#### Value by TCG")

        df["inventory_value"] = (
            df["selling_price"] *
            df["quantity"]
        )

        value_by_tcg = (
            df.groupby("tcg")["inventory_value"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(
            value_by_tcg,
            use_container_width=True
        )


    # --------------------------------------------------
    # QUANTITY BY TCG
    # --------------------------------------------------

    with chart_col2:

        st.markdown("#### Units by TCG")

        quantity_by_tcg = (
            df.groupby("tcg")["quantity"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(
            quantity_by_tcg,
            use_container_width=True
        )


    st.divider()


    # --------------------------------------------------
    # TOP HOLDINGS
    # --------------------------------------------------

    st.subheader("Top Holdings")

    holdings_df = df.copy()

    holdings_df["inventory_value"] = (
        holdings_df["selling_price"] *
        holdings_df["quantity"]
    )

    holdings_df["potential_profit"] = (
        (
            holdings_df["selling_price"] -
            holdings_df["cost"]
        )
        *
        holdings_df["quantity"]
    )

    top_holdings = (
        holdings_df.sort_values(
            by="inventory_value",
            ascending=False
        )
        .head(5)
    )

    top_holdings_display = top_holdings[
        [
            "sku",
            "english_name",
            "tcg",
            "quantity",
            "cost",
            "selling_price",
            "inventory_value",
            "potential_profit"
        ]
    ]

    st.dataframe(
        top_holdings_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "sku": "SKU",
            "english_name": "Product",
            "tcg": "TCG",
            "quantity": "Units",
            "cost": st.column_config.NumberColumn(
                "Cost",
                format="%.2f AED"
            ),
            "selling_price": st.column_config.NumberColumn(
                "Selling Price",
                format="%.2f AED"
            ),
            "inventory_value": st.column_config.NumberColumn(
                "Total Value",
                format="%.2f AED"
            ),
            "potential_profit": st.column_config.NumberColumn(
                "Potential Profit",
                format="%.2f AED"
            )
        }
    )


    st.divider()


    # --------------------------------------------------
    # INVENTORY TABLE
    # --------------------------------------------------

    st.subheader("Inventory")

    st.caption(
        f"{total_products} products · {total_quantity} total units"
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


except FileNotFoundError:

    st.warning(
        "No inventory found yet. Scan your first card."
    )


except Exception as error:

    st.error(
        f"Dashboard error: {str(error)}"
    )

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
    page_icon="◆",
    layout="wide"
)


st.markdown(
    """
    <style>
    .block-container {
        max-width: 1180px;
        padding-top: 3rem;
        padding-bottom: 4rem;
    }

    .kizunai-hero {
        padding: 2rem 2rem;
        border: 1px solid rgba(120, 140, 255, 0.22);
        border-radius: 24px;
        background: linear-gradient(135deg, rgba(18, 24, 45, 0.95), rgba(7, 10, 20, 0.95));
        box-shadow: 0 18px 55px rgba(0, 0, 0, 0.35);
        margin-bottom: 2rem;
    }

    .kizunai-label {
        font-size: 0.75rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: #91a4ff;
        font-weight: 700;
        margin-bottom: 0.45rem;
    }

    .kizunai-title {
        font-size: 3rem;
        line-height: 1;
        font-weight: 850;
        color: #f7f8ff;
        margin-bottom: 0.6rem;
    }

    .kizunai-subtitle {
        font-size: 1rem;
        color: #b8c0d9;
        max-width: 760px;
    }

    .metric-card {
        padding: 1.2rem 1.2rem;
        border-radius: 18px;
        border: 1px solid rgba(145, 164, 255, 0.18);
        background: rgba(18, 25, 45, 0.72);
        min-height: 126px;
    }

    .metric-label {
        color: #91a4ff;
        font-size: 0.72rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        font-weight: 800;
        margin-bottom: 0.4rem;
    }

    .metric-value {
        color: #f7f8ff;
        font-size: 1.75rem;
        font-weight: 850;
        line-height: 1.05;
        margin-bottom: 0.35rem;
    }

    .metric-text {
        color: #aab4d4;
        font-size: 0.85rem;
    }

    .section-title {
        font-size: 1.5rem;
        font-weight: 820;
        color: #f7f8ff;
        margin-top: 1.5rem;
        margin-bottom: 0.4rem;
    }

    .section-text {
        color: #aab4d4;
        margin-bottom: 1rem;
    }

    .chart-card {
        padding: 1.2rem;
        border-radius: 18px;
        border: 1px solid rgba(145, 164, 255, 0.16);
        background: rgba(18, 25, 45, 0.55);
        min-height: 320px;
    }

    .chart-title {
        color: #f7f8ff;
        font-weight: 850;
        margin-bottom: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="kizunai-hero">
        <div class="kizunai-label">UMAMI VAULT AI OPERATIONS SYSTEM</div>
        <div class="kizunai-title">Portfolio Dashboard</div>
        <div class="kizunai-subtitle">
            Real-time inventory analytics for your TCG collection. Track portfolio value, cost basis, potential profit and collection distribution from the same deterministic calculation engine used by the KizunAI Agent.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


try:
    df = pd.read_csv("data/inventory.csv")

    if df.empty:
        st.warning("Your inventory is empty. Scan your first card to begin.")
        st.stop()

    for column in ["quantity", "cost", "selling_price"]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        ).fillna(0)

    total_products = len(df)
    total_quantity = int(df["quantity"].sum())
    total_cost = calculate_portfolio_cost()
    total_value = calculate_portfolio_value()
    total_profit = calculate_portfolio_profit()
    portfolio_margin = calculate_portfolio_margin()

    st.markdown('<div class="section-title">Portfolio Overview</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-text">A financial snapshot of your current saved inventory.</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Collection Value</div>
                <div class="metric-value">{total_value:,.2f} AED</div>
                <div class="metric-text">Total selling price × quantity</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Inventory Cost</div>
                <div class="metric-value">{total_cost:,.2f} AED</div>
                <div class="metric-text">Total cost basis across inventory</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Potential Profit</div>
                <div class="metric-value">{total_profit:,.2f} AED</div>
                <div class="metric-text">Unrealized profit at selling price</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")

    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Portfolio Margin</div>
                <div class="metric-value">{portfolio_margin:.2f}%</div>
                <div class="metric-text">Potential profit ÷ collection value</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col5:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Products</div>
                <div class="metric-value">{total_products}</div>
                <div class="metric-text">Unique inventory records</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col6:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Total Units</div>
                <div class="metric-value">{total_quantity}</div>
                <div class="metric-text">Total quantity across all products</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('<div class="section-title">Portfolio Distribution</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-text">Understand where portfolio value and units are concentrated.</div>',
        unsafe_allow_html=True
    )

    df["inventory_value"] = df["selling_price"] * df["quantity"]

    chart_col1, chart_col2 = st.columns(2, gap="large")

    with chart_col1:
        st.markdown('<div class="chart-card"><div class="chart-title">Value by TCG</div>', unsafe_allow_html=True)

        value_by_tcg = (
            df.groupby("tcg")["inventory_value"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(
            value_by_tcg,
            use_container_width=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with chart_col2:
        st.markdown('<div class="chart-card"><div class="chart-title">Units by TCG</div>', unsafe_allow_html=True)

        quantity_by_tcg = (
            df.groupby("tcg")["quantity"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(
            quantity_by_tcg,
            use_container_width=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Top Holdings</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-text">Highest value records in the current inventory.</div>',
        unsafe_allow_html=True
    )

    holdings_df = df.copy()

    holdings_df["potential_profit"] = (
        (holdings_df["selling_price"] - holdings_df["cost"])
        * holdings_df["quantity"]
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

    st.markdown('<div class="section-title">Inventory Table</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="section-text">{total_products} products · {total_quantity} total units</div>',
        unsafe_allow_html=True
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


except FileNotFoundError:
    st.warning("No inventory found yet. Scan your first card.")

except Exception as error:
    st.error(f"Dashboard error: {str(error)}")

import streamlit as st
import pandas as pd

from services.inventory_ai import answer_inventory_question


st.set_page_config(
    page_title="KizunAI Inventory",
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
        min-height: 118px;
        margin-bottom: 1rem;
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

    .stButton > button {
        border-radius: 12px;
        font-weight: 750;
        border: 1px solid rgba(145, 164, 255, 0.35);
        background: linear-gradient(135deg, #5d6dff, #7c4dff);
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="kizunai-hero">
        <div class="kizunai-label">UMAMI VAULT AI OPERATIONS SYSTEM</div>
        <div class="kizunai-title">Inventory Search</div>
        <div class="kizunai-subtitle">
            Explore your saved TCG inventory using filters, keyword search and AI-powered inventory questions.
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

    filtered_df = df.copy()

    st.markdown(
        '<div class="section-title">Quick Filters</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-text">Search across product name, SKU, set name, card number, language, condition or TCG.</div>',
        unsafe_allow_html=True
    )

    search_text = st.text_input(
        "Search inventory",
        placeholder="Search by product, SKU, set, card number, language or condition..."
    )

    if search_text:
        search_text = search_text.lower()

        filtered_df = filtered_df[
            filtered_df.astype(str)
            .apply(
                lambda row: row.str.lower().str.contains(search_text).any(),
                axis=1
            )
        ]

    col1, col2, col3 = st.columns(3)

    with col1:
        language_filter = st.selectbox(
            "Language",
            ["All"] + sorted(df["language"].dropna().unique().tolist())
        )

    with col2:
        condition_filter = st.selectbox(
            "Condition",
            ["All"] + sorted(df["condition"].dropna().unique().tolist())
        )

    with col3:
        tcg_filter = st.selectbox(
            "TCG",
            ["All"] + sorted(df["tcg"].dropna().unique().tolist())
        )

    if language_filter != "All":
        filtered_df = filtered_df[
            filtered_df["language"] == language_filter
        ]

    if condition_filter != "All":
        filtered_df = filtered_df[
            filtered_df["condition"] == condition_filter
        ]

    if tcg_filter != "All":
        filtered_df = filtered_df[
            filtered_df["tcg"] == tcg_filter
        ]

    total_records = len(df)
    matching_records = len(filtered_df)

    total_units = 0
    matching_value = 0

    if "quantity" in filtered_df.columns:
        filtered_df["quantity"] = pd.to_numeric(
            filtered_df["quantity"],
            errors="coerce"
        ).fillna(0)

        total_units = int(filtered_df["quantity"].sum())

    if "selling_price" in filtered_df.columns and "quantity" in filtered_df.columns:
        filtered_df["selling_price"] = pd.to_numeric(
            filtered_df["selling_price"],
            errors="coerce"
        ).fillna(0)

        matching_value = (
            filtered_df["selling_price"] *
            filtered_df["quantity"]
        ).sum()

    st.markdown(
        '<div class="section-title">Search Results</div>',
        unsafe_allow_html=True
    )

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    with metric_col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Matching Products</div>
                <div class="metric-value">{matching_records}</div>
                <div class="metric-text">Out of {total_records} saved records</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with metric_col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Matching Units</div>
                <div class="metric-value">{total_units}</div>
                <div class="metric-text">Total quantity in filtered results</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with metric_col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Filtered Value</div>
                <div class="metric-value">{matching_value:,.2f} AED</div>
                <div class="metric-text">Selling price × quantity</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        '<div class="section-title">AI Inventory Assistant</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-text">Ask natural language questions about your inventory data.</div>',
        unsafe_allow_html=True
    )

    ai_question = st.text_input(
        "Ask KizunAI about your inventory",
        placeholder="Example: Which cards have the highest potential profit?"
    )

    if st.button("Ask Inventory AI", key="ask_inventory_ai_button"):

        if ai_question:

            with st.spinner("KizunAI is checking your inventory..."):
                ai_answer = answer_inventory_question(ai_question)

            st.success(ai_answer)

        else:
            st.warning("Please write a question first.")


except FileNotFoundError:
    st.warning("No inventory found yet. Scan and approve your first card first.")

except Exception as error:
    st.error(f"Inventory Search error: {str(error)}")

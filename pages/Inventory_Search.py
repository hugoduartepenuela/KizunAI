import streamlit as st
import pandas as pd

from services.inventory_ai import answer_inventory_question


st.set_page_config(
    page_title="KizunAI Inventory Search",
    page_icon="🔎",
    layout="wide"
)

st.title("🔎 KizunAI Inventory Search")
st.write("Ask questions or filter your saved TCG inventory.")

try:
    df = pd.read_csv("data/inventory.csv")

    st.subheader("Quick Filters")

    search_text = st.text_input(
        "Search by product name, SKU, set name, card number, language or condition"
    )

    filtered_df = df.copy()

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

    st.divider()

    st.subheader("Search Results")

    st.metric(
        "Matching Products",
        len(filtered_df)
    )

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

    st.divider()

    st.subheader("AI Inventory Assistant")

    ai_question = st.text_input(
        "Ask KizunAI about your inventory",
        placeholder="Example: How many Japanese Pikachu cards do I own?"
    )

    if st.button("Ask AI", key="ask_inventory_ai_button"):

        if ai_question:

            with st.spinner("KizunAI is checking your inventory..."):

                ai_answer = answer_inventory_question(ai_question)

            st.write(ai_answer)

        else:
            st.warning("Please write a question first.")

except FileNotFoundError:
    st.warning(
        "No inventory found yet. Scan and approve your first card first."
    )
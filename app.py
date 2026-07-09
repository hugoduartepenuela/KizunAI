import streamlit as st
import os

from PIL import Image
from services.scanner import scan_card
from services.sku_generator import generate_sku
from services.inventory import save_card


st.set_page_config(
    page_title="KizunAI Scanner",
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
        max-width: 720px;
    }

    .feature-card {
        padding: 1.2rem 1.2rem;
        border-radius: 18px;
        border: 1px solid rgba(145, 164, 255, 0.18);
        background: rgba(18, 25, 45, 0.72);
        min-height: 126px;
    }

    .feature-title {
        color: #f7f8ff;
        font-weight: 800;
        margin-bottom: 0.25rem;
    }

    .feature-text {
        color: #aab4d4;
        font-size: 0.9rem;
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

    div[data-testid="stFileUploader"] {
        border: 1px dashed rgba(145, 164, 255, 0.35);
        border-radius: 18px;
        padding: 1rem;
        background: rgba(18, 25, 45, 0.55);
    }

    div[data-testid="stMetricValue"] {
        color: #f7f8ff;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="kizunai-hero">
        <div class="kizunai-label">UMAMI VAULT AI OPERATIONS SYSTEM</div>
        <div class="kizunai-title">KizunAI Scanner</div>
        <div class="kizunai-subtitle">
            Scan. Identify. Price. Vault. Turn a TCG card image into structured inventory data with AI vision, human verification and deterministic SKU generation.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-title">Vision Extraction</div>
            <div class="feature-text">Reads visible card information and returns structured product data.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-title">Human Verification</div>
            <div class="feature-text">AI output is reviewed before being saved into inventory.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-title">SKU Automation</div>
            <div class="feature-text">Creates consistent inventory SKUs using deterministic business rules.</div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.markdown('<div class="section-title">Card Scanner</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-text">Upload a JPG or PNG card image. KizunAI will analyze it and prepare the inventory record for approval.</div>',
    unsafe_allow_html=True
)


if "scan_result" not in st.session_state:
    st.session_state.scan_result = None

if "uploaded_card_preview" not in st.session_state:
    st.session_state.uploaded_card_preview = None


left_col, right_col = st.columns([0.42, 0.58], gap="large")

with left_col:
    uploaded_file = st.file_uploader(
        "Upload TCG card image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file:
        st.session_state.uploaded_card_preview = uploaded_file
        st.image(
            uploaded_file,
            caption="Uploaded Card",
            use_container_width=True
        )

        if st.button("Scan Card", key="scan_card_button", use_container_width=True):
            with st.spinner("KizunAI Vision is analyzing the card..."):
                st.session_state.scan_result = scan_card(uploaded_file)

with right_col:
    st.markdown('<div class="section-title">Extraction Pipeline</div>', unsafe_allow_html=True)

    pipeline_col1, pipeline_col2 = st.columns(2)

    with pipeline_col1:
        st.info("1. Image Upload")
        st.info("2. OpenAI Vision")
        st.info("3. Structured Data")

    with pipeline_col2:
        st.info("4. Human Review")
        st.info("5. SKU Generation")
        st.info("6. Inventory Save")


if st.session_state.scan_result:

    result = st.session_state.scan_result

    if "error" in result:
        st.error(result["error"])

    else:
        st.divider()

        st.markdown('<div class="section-title">AI Scan Result</div>', unsafe_allow_html=True)
        st.json(result)

        st.markdown('<div class="section-title">Human Verification</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-text">Review and correct the extracted data before approving the card.</div>',
            unsafe_allow_html=True
        )

        form_left, form_right = st.columns(2, gap="large")

        with form_left:
            product_name = st.text_input(
                "Product Name",
                value=result.get("product_name", "")
            )

            english_name = st.text_input(
                "English Name for SKU",
                value=result.get(
                    "english_name",
                    result.get("product_name", "")
                )
            )

            tcg = st.text_input(
                "TCG",
                value=result.get("tcg", "")
            )

            set_name = st.text_input(
                "Set Name",
                value=result.get("set_name", "")
            )

            card_number = st.text_input(
                "Card Number",
                value=result.get("card_number", "")
            )

            language = st.text_input(
                "Language",
                value=result.get("language", "")
            )

        with form_right:
            rarity = st.text_input(
                "Rarity",
                value=result.get("rarity", "")
            )

            condition = st.selectbox(
                "Condition",
                [
                    "Near Mint",
                    "Excellent",
                    "Light Play",
                    "Moderate Play",
                    "Heavy Play"
                ]
            )

            raw_or_slab = st.selectbox(
                "Raw or Slab",
                ["Raw", "PSA", "BGS", "CGC", "Other"],
                index=0
            )

            grade = st.text_input(
                "Grade",
                value="" if result.get("grade") is None else str(result.get("grade"))
            )

            quantity = st.number_input(
                "Quantity",
                min_value=1,
                value=1
            )

            cost = st.number_input(
                "Cost AED",
                min_value=0.0,
                value=0.0
            )

            selling_price = st.number_input(
                "Selling Price AED",
                min_value=0.0,
                value=0.0
            )

        sku = generate_sku(
            product_name=english_name,
            raw_or_slab=raw_or_slab,
            grade=grade
        )

        st.markdown('<div class="section-title">Generated SKU</div>', unsafe_allow_html=True)

        sku_col1, sku_col2, sku_col3 = st.columns([0.45, 0.25, 0.30])

        with sku_col1:
            st.text_input(
                "SKU",
                value=sku,
                disabled=True
            )

        with sku_col2:
            st.metric("Quantity", quantity)

        with sku_col3:
            estimated_profit = selling_price - cost
            st.metric("Estimated Profit AED", f"{estimated_profit:,.2f}")

        if st.button("Approve and Save Card", key="approve_card_button", use_container_width=True):

            os.makedirs("data/card_images", exist_ok=True)

            image_path = f"data/card_images/{sku}.jpg"

            image = Image.open(uploaded_file)
            image.save(image_path)

            card_data = {
                "sku": sku,
                "product_name": product_name,
                "english_name": english_name,
                "tcg": tcg,
                "set_name": set_name,
                "card_number": card_number,
                "language": language,
                "rarity": rarity,
                "condition": condition,
                "raw_or_slab": raw_or_slab,
                "grade": grade,
                "quantity": quantity,
                "cost": cost,
                "selling_price": selling_price,
                "image_path": image_path
            }

            save_card(card_data)

            st.success("Card approved and saved successfully.")

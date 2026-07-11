import io
import os

import streamlit as st
from PIL import Image, UnidentifiedImageError

from services.inventory import save_card
from services.scanner import scan_card
from services.sku_generator import generate_sku


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="KizunAI Scanner",
    page_icon="◆",
    layout="wide",
)


# =========================================================
# CUSTOM STYLES
# =========================================================

st.markdown(
    """
    <style>
        .block-container {
            max-width: 1180px;
            padding-top: 3rem;
            padding-bottom: 4rem;
        }

        .kizunai-hero {
            padding: 2rem;
            border: 1px solid rgba(120, 140, 255, 0.22);
            border-radius: 24px;
            background: linear-gradient(
                135deg,
                rgba(18, 24, 45, 0.95),
                rgba(7, 10, 20, 0.95)
            );
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
            padding: 1.2rem;
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
    unsafe_allow_html=True,
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def open_image_from_bytes(image_bytes: bytes) -> Image.Image:
    """
    Validate uploaded bytes and return an independent PIL image.

    Image.load() forces Pillow to decode the file immediately, so invalid
    uploads fail here instead of later inside st.image().
    """
    image = Image.open(io.BytesIO(image_bytes))
    image.load()
    return image


def create_scanner_file(image_bytes: bytes, filename: str) -> io.BytesIO:
    """
    Create a fresh file-like object for scan_card().

    This prevents the scanner from consuming the same file object used by
    Streamlit or Pillow.
    """
    scanner_file = io.BytesIO(image_bytes)
    scanner_file.name = filename
    scanner_file.seek(0)
    return scanner_file


def save_uploaded_image(
    image_bytes: bytes,
    sku: str,
    original_format: str | None = None,
) -> str:
    """
    Save the approved image as a standard RGB JPEG.

    Converting to RGB avoids errors with PNG transparency, palette images,
    CMYK images and other formats that cannot be saved directly as JPEG.
    """
    image_directory = "data/card_images"
    os.makedirs(image_directory, exist_ok=True)

    safe_sku = "".join(
        character
        for character in sku
        if character.isalnum() or character in ("-", "_")
    )

    if not safe_sku:
        raise ValueError("A valid SKU is required before saving the image.")

    image_path = os.path.join(image_directory, f"{safe_sku}.jpg")

    image = open_image_from_bytes(image_bytes)

    if image.mode != "RGB":
        image = image.convert("RGB")

    image.save(
        image_path,
        format="JPEG",
        quality=95,
        optimize=True,
    )

    return image_path


def clear_current_scan() -> None:
    """Clear the current upload and extracted result."""
    st.session_state.scan_result = None
    st.session_state.uploaded_image_bytes = None
    st.session_state.uploaded_filename = None
    st.session_state.uploaded_file_signature = None


# =========================================================
# SESSION STATE
# =========================================================

if "scan_result" not in st.session_state:
    st.session_state.scan_result = None

if "uploaded_image_bytes" not in st.session_state:
    st.session_state.uploaded_image_bytes = None

if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None

if "uploaded_file_signature" not in st.session_state:
    st.session_state.uploaded_file_signature = None


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div class="kizunai-hero">
        <div class="kizunai-label">
            UMAMI VAULT AI OPERATIONS SYSTEM
        </div>

        <div class="kizunai-title">
            KizunAI Scanner
        </div>

        <div class="kizunai-subtitle">
            Scan. Identify. Price. Vault. Turn a TCG card image into
            structured inventory data with AI vision, human verification
            and deterministic SKU generation.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# FEATURE CARDS
# =========================================================

feature_col_1, feature_col_2, feature_col_3 = st.columns(3)

with feature_col_1:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-title">Vision Extraction</div>
            <div class="feature-text">
                Reads visible card information and returns structured
                product data.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with feature_col_2:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-title">Human Verification</div>
            <div class="feature-text">
                AI output is reviewed before being saved into inventory.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with feature_col_3:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-title">SKU Automation</div>
            <div class="feature-text">
                Creates consistent inventory SKUs using deterministic
                business rules.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# SCANNER
# =========================================================

st.markdown(
    '<div class="section-title">Card Scanner</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-text">
        Upload a JPG or PNG card image. KizunAI will analyze it and
        prepare the inventory record for approval.
    </div>
    """,
    unsafe_allow_html=True,
)

left_col, right_col = st.columns([0.42, 0.58], gap="large")


# =========================================================
# IMAGE UPLOAD
# =========================================================

with left_col:
    uploaded_file = st.file_uploader(
        "Upload TCG card image",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=False,
    )

    valid_image = False
    preview_image = None

    if uploaded_file is not None:
        try:
            # Read the upload once and keep immutable bytes in session state.
            current_bytes = uploaded_file.getvalue()

            if not current_bytes:
                raise ValueError("The uploaded file is empty.")

            # Signature changes when either the name or content size changes.
            current_signature = (
                uploaded_file.name,
                len(current_bytes),
            )

            if (
                st.session_state.uploaded_file_signature
                != current_signature
            ):
                st.session_state.uploaded_image_bytes = current_bytes
                st.session_state.uploaded_filename = uploaded_file.name
                st.session_state.uploaded_file_signature = current_signature

                # Clear the old scan when a different image is uploaded.
                st.session_state.scan_result = None

            preview_image = open_image_from_bytes(
                st.session_state.uploaded_image_bytes
            )

            st.image(
                preview_image,
                caption="Uploaded Card",
                use_container_width=True,
            )

            valid_image = True

        except (
            UnidentifiedImageError,
            OSError,
            ValueError,
        ) as error:
            st.session_state.uploaded_image_bytes = None
            st.session_state.uploaded_filename = None
            st.session_state.uploaded_file_signature = None
            st.session_state.scan_result = None

            st.error(
                "The uploaded file could not be read as a valid image. "
                "Please upload a standard JPG, JPEG or PNG file."
            )

            with st.expander("Technical details"):
                st.code(str(error))

    scan_clicked = st.button(
        "Scan Card",
        key="scan_card_button",
        use_container_width=True,
        disabled=not valid_image,
    )

    if scan_clicked:
        try:
            scanner_file = create_scanner_file(
                image_bytes=st.session_state.uploaded_image_bytes,
                filename=st.session_state.uploaded_filename,
            )

            with st.spinner(
                "KizunAI Vision is analyzing the card..."
            ):
                st.session_state.scan_result = scan_card(scanner_file)

        except Exception as error:
            st.session_state.scan_result = {
                "error": (
                    "The card could not be analyzed. "
                    f"Technical detail: {error}"
                )
            }

    if st.session_state.uploaded_image_bytes is not None:
        if st.button(
            "Clear Upload",
            key="clear_upload_button",
            use_container_width=True,
        ):
            clear_current_scan()
            st.rerun()


# =========================================================
# PIPELINE
# =========================================================

with right_col:
    st.markdown(
        '<div class="section-title">Extraction Pipeline</div>',
        unsafe_allow_html=True,
    )

    pipeline_col_1, pipeline_col_2 = st.columns(2)

    with pipeline_col_1:
        st.info("1. Image Upload")
        st.info("2. OpenAI Vision")
        st.info("3. Structured Data")

    with pipeline_col_2:
        st.info("4. Human Review")
        st.info("5. SKU Generation")
        st.info("6. Inventory Save")


# =========================================================
# SCAN RESULT
# =========================================================

if st.session_state.scan_result is not None:
    result = st.session_state.scan_result

    if not isinstance(result, dict):
        st.error(
            "The scanner returned an unexpected response format."
        )

    elif result.get("error"):
        st.error(result["error"])

    else:
        st.divider()

        st.markdown(
            '<div class="section-title">AI Scan Result</div>',
            unsafe_allow_html=True,
        )

        with st.expander(
            "View raw structured output",
            expanded=False,
        ):
            st.json(result)

        st.markdown(
            '<div class="section-title">Human Verification</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="section-text">
                Review and correct the extracted data before approving
                the card.
            </div>
            """,
            unsafe_allow_html=True,
        )

        form_left, form_right = st.columns(2, gap="large")

        with form_left:
            product_name = st.text_input(
                "Product Name",
                value=str(result.get("product_name") or ""),
            )

            english_name = st.text_input(
                "English Name for SKU",
                value=str(
                    result.get("english_name")
                    or result.get("product_name")
                    or ""
                ),
            )

            tcg = st.text_input(
                "TCG",
                value=str(result.get("tcg") or ""),
            )

            set_name = st.text_input(
                "Set Name",
                value=str(result.get("set_name") or ""),
            )

            card_number = st.text_input(
                "Card Number",
                value=str(result.get("card_number") or ""),
            )

            language = st.text_input(
                "Language",
                value=str(result.get("language") or ""),
            )

        with form_right:
            rarity = st.text_input(
                "Rarity",
                value=str(result.get("rarity") or ""),
            )

            condition_options = [
                "Near Mint",
                "Excellent",
                "Light Play",
                "Moderate Play",
                "Heavy Play",
            ]

            detected_condition = str(
                result.get("condition") or "Near Mint"
            )

            condition_index = (
                condition_options.index(detected_condition)
                if detected_condition in condition_options
                else 0
            )

            condition = st.selectbox(
                "Condition",
                condition_options,
                index=condition_index,
            )

            slab_options = [
                "Raw",
                "PSA",
                "BGS",
                "CGC",
                "Other",
            ]

            detected_state = str(
                result.get("raw_or_slab") or "Raw"
            )

            slab_index = (
                slab_options.index(detected_state)
                if detected_state in slab_options
                else 0
            )

            raw_or_slab = st.selectbox(
                "Raw or Slab",
                slab_options,
                index=slab_index,
            )

            grade = st.text_input(
                "Grade",
                value=(
                    ""
                    if result.get("grade") is None
                    else str(result.get("grade"))
                ),
                disabled=raw_or_slab == "Raw",
            )

            quantity = st.number_input(
                "Quantity",
                min_value=1,
                value=1,
                step=1,
            )

            cost = st.number_input(
                "Cost AED",
                min_value=0.0,
                value=0.0,
                step=1.0,
                format="%.2f",
            )

            selling_price = st.number_input(
                "Selling Price AED",
                min_value=0.0,
                value=0.0,
                step=1.0,
                format="%.2f",
            )

        # Raw cards do not need a grade.
        normalized_grade = (
            None
            if raw_or_slab == "Raw"
            else grade.strip() or None
        )

        try:
            sku = generate_sku(
                product_name=english_name.strip(),
                raw_or_slab=raw_or_slab,
                grade=normalized_grade,
            )
        except Exception as error:
            sku = ""
            st.error(f"SKU generation failed: {error}")

        st.markdown(
            '<div class="section-title">Generated SKU</div>',
            unsafe_allow_html=True,
        )

        sku_col_1, sku_col_2, sku_col_3 = st.columns(
            [0.45, 0.25, 0.30]
        )

        with sku_col_1:
            st.text_input(
                "SKU",
                value=sku,
                disabled=True,
            )

        with sku_col_2:
            st.metric(
                "Quantity",
                quantity,
            )

        with sku_col_3:
            estimated_profit_per_unit = selling_price - cost
            estimated_total_profit = (
                estimated_profit_per_unit * quantity
            )

            st.metric(
                "Estimated Profit AED",
                f"{estimated_total_profit:,.2f}",
            )

        can_save = all(
            [
                product_name.strip(),
                english_name.strip(),
                sku,
                st.session_state.uploaded_image_bytes,
            ]
        )

        approve_clicked = st.button(
            "Approve and Save Card",
            key="approve_card_button",
            use_container_width=True,
            disabled=not can_save,
        )

        if approve_clicked:
            try:
                image_path = save_uploaded_image(
                    image_bytes=(
                        st.session_state.uploaded_image_bytes
                    ),
                    sku=sku,
                )

                card_data = {
                    "sku": sku,
                    "product_name": product_name.strip(),
                    "english_name": english_name.strip(),
                    "tcg": tcg.strip(),
                    "set_name": set_name.strip(),
                    "card_number": card_number.strip(),
                    "language": language.strip(),
                    "rarity": rarity.strip(),
                    "condition": condition,
                    "raw_or_slab": raw_or_slab,
                    "grade": (
                        ""
                        if normalized_grade is None
                        else normalized_grade
                    ),
                    "quantity": int(quantity),
                    "cost": float(cost),
                    "selling_price": float(selling_price),
                    "image_path": image_path,
                }

                save_card(card_data)

                st.success(
                    f"Card approved and saved successfully. SKU: {sku}"
                )

                st.balloons()

            except (
                UnidentifiedImageError,
                OSError,
                ValueError,
            ) as error:
                st.error(
                    "The card data was not saved because the uploaded "
                    "image could not be processed."
                )

                with st.expander("Technical details"):
                    st.code(str(error))

            except Exception as error:
                st.error(
                    "The card could not be saved to inventory."
                )

                with st.expander("Technical details"):
                    st.code(str(error))

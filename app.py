import streamlit as st
import os

from PIL import Image
from services.scanner import scan_card
from services.sku_generator import generate_sku
from services.inventory import save_card


st.set_page_config(
    page_title="KizunAI Scanner",
    page_icon="🎴",
    layout="centered"
)

st.title("🎴 KizunAI Scanner")
st.write("Scan. Identify. Price. Vault.")

if "scan_result" not in st.session_state:
    st.session_state.scan_result = None

uploaded_file = st.file_uploader(
    "Upload a TCG card image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    st.image(
        uploaded_file,
        caption="Uploaded Card",
        use_container_width=True
    )

    if st.button("Scan Card", key="scan_card_button"):
        with st.spinner("KizunAI is analyzing the card..."):
            st.session_state.scan_result = scan_card(uploaded_file)

if st.session_state.scan_result:

    result = st.session_state.scan_result

    if "error" in result:
        st.error(result["error"])

    else:
        st.subheader("AI Scan Result")
        st.json(result)

        st.subheader("Human Verification")

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
        

        raw_or_slab = st.selectbox(
            "Raw or Slab",
            ["Raw", "PSA", "BGS", "CGC", "Other"],
            index=0
        )

        grade = st.text_input(
            "Grade",
            value="" if result.get("grade") is None else str(result.get("grade"))
        )
        sku = generate_sku(
            product_name=english_name,
            raw_or_slab=raw_or_slab,
            grade=grade
        )

        st.text_input(
            "SKU",
            value=sku,
            disabled=True
        )

        if st.button("Approve Card", key="approve_card_button"):
            
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

            st.success("Card saved successfully!")

from services.agent import ask_agent, set_current_video_url


st.divider()

st.header("🤖 KizunAI Agent Chat")
st.write("Ask about your inventory or a YouTube video.")

if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = []

youtube_url = st.text_input(
    "YouTube URL",
    placeholder="Paste a YouTube video URL here"
)

if st.button("Process YouTube Video"):
    if youtube_url:
        set_current_video_url(youtube_url)
        st.success("YouTube video connected to KizunAI Agent.")
    else:
        st.warning("Please paste a YouTube URL first.")


for message in st.session_state.agent_messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


user_question = st.chat_input("Ask KizunAI something...")

if user_question:
    st.session_state.agent_messages.append(
        {
            "role": "user",
            "content": user_question
        }
    )

    with st.chat_message("user"):
        st.write(user_question)

    with st.chat_message("assistant"):
        with st.spinner("KizunAI is thinking..."):
            answer = ask_agent(user_question)
            st.write(answer)

    st.session_state.agent_messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
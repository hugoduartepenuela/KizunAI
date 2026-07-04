from openai import OpenAI, APIConnectionError, RateLimitError, AuthenticationError
from dotenv import load_dotenv
import os
import base64
import json

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def scan_card(uploaded_file):

    image_bytes = uploaded_file.getvalue()

    base64_image = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    prompt = """
You are KizunAI, an expert TCG inventory scanner for Pokemon, One Piece, Yu-Gi-Oh and collectible cards.

Analyze the uploaded image and return ONLY valid JSON.

Return this exact structure:

{
  "product_name": "",
  "english_name": "",
  "tcg": "",
  "set_name": "",
  "set_name_source": "unknown",
  "set_name_visible": false,
  "card_number": "",
  "card_number_visible": false,
  "language": "",
  "rarity": "",
  "condition": "Unknown",
  "raw_or_slab": "Raw",
  "grade": null,
  "product_type": "Single Card",
  "confidence": 0,
  "ai_notes": ""
}

IMPORTANT:

- Return ONLY valid JSON.
- Do NOT include markdown.
- Do NOT use ```json.
- Do NOT wrap the response in code blocks.
- Do NOT add explanations before or after the JSON.
- The response must start with { and end with }.

CARD IDENTIFICATION RULES:

- Return only information visible in the image.
- Never guess information that is not visible.
- Never invent a set name.
- Never invent a card number.
- Never invent a grade.
- If a field cannot be determined, return "Unknown".
- Detect the card language from visible text.
- Detect whether the product is Raw or Slab.
- If the product is a PSA, BGS, CGC or other graded slab, extract the grade if visible.
- Confidence must be an integer between 0 and 100.
- ai_notes should briefly explain what information was visible in the image.

SET NAME RULES:

- If the set name is clearly printed as readable text on the card, slab label, packaging, or visible product label, return it in set_name.
- If the set name is clearly visible, set set_name_visible to true and set set_name_source to "visible".
- If the set name is not printed but you can identify it with high confidence from visible card name, card number, language, promo code, regulation mark, or other visible identifiers, you may return the best inferred set name.
- If the set name is inferred, set set_name_visible to false and set set_name_source to "inferred".
- If the set name is inferred, needs_human_review must be true.
- Do NOT assign random expansion sets based only on artwork style.
- Do NOT infer famous collaboration promo cards into normal expansion sets.
- For museum promos, event promos, campaign promos, limited promos, and collaboration cards, prefer "Unknown" unless the promo identity is clearly visible or highly recognizable.
- If unsure, return "Unknown" and set set_name_source to "unknown".
- It is better to return "Unknown" than an incorrect set name.

CARD NUMBER RULES:

- Return card_number only if it is clearly visible.
- Set card_number_visible to true only when the card number is clearly visible.
- If unsure, return "Unknown".

NAME RULES:

- If the card name is in Japanese, also provide the closest English name in english_name.
- If the card name is already in English, english_name must match product_name.
- english_name is used internally for SKU generation.

PRODUCT TYPE EXAMPLES:

- Single Card
- PSA Slab
- BGS Slab
- CGC Slab
- Booster Box
- Premium Collection
- Deck
- Other
"""

    try:

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    ]
                }
            ]
        )

        text_result = response.output_text

        text_result = text_result.replace(
            "```json",
            ""
        )

        text_result = text_result.replace(
            "```",
            ""
        )

        text_result = text_result.strip()

        try:

            data = json.loads(text_result)

            if data.get("set_name_source") not in ["visible", "inferred"]:
                data["set_name"] = "Unknown"
                data["set_name_source"] = "unknown"

            if not data.get("card_number_visible", False):
                data["card_number"] = "Unknown"

            return data

        except json.JSONDecodeError:

            return {
                "product_name": "Unknown",
                "english_name": "Unknown",
                "tcg": "Unknown",
                "set_name": "Unknown",
                "set_name_visible": False,
                "card_number": "Unknown",
                "card_number_visible": False,
                "language": "Unknown",
                "rarity": "Unknown",
                "condition": "Unknown",
                "raw_or_slab": "Raw",
                "grade": None,
                "product_type": "Unknown",
                "confidence": 0,
                "ai_notes": text_result
            }

    except AuthenticationError:

        return {
            "error": "Authentication error. Check OPENAI_API_KEY."
        }

    except RateLimitError:

        return {
            "error": "Rate limit reached or billing issue."
        }

    except APIConnectionError:

        return {
            "error": "Connection error. Check internet connection."
        }

    except Exception as e:

        return {
            "error": str(e)
        }
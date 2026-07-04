import csv
import os
from datetime import datetime


INVENTORY_FILE = "data/inventory.csv"


def save_card(card_data):

    os.makedirs("data", exist_ok=True)

    file_exists = os.path.isfile(INVENTORY_FILE)

    fieldnames = [
        "sku",
        "product_name",
        "english_name",
        "tcg",
        "set_name",
        "card_number",
        "language",
        "rarity",
        "condition",
        "raw_or_slab",
        "grade",
        "quantity",
        "cost",
        "selling_price",
        "image_path",
        "date_added"
    ]

    with open(
        INVENTORY_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        if not file_exists:
            writer.writeheader()

        card_data["date_added"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        writer.writerow(card_data)
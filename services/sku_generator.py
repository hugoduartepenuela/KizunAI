import csv
import os
import re


INVENTORY_FILE = "data/inventory.csv"


def clean_text(text):
    if not text:
        return "UNKNOWN"

    text = str(text).upper()
    text = re.sub(r"[^A-Z0-9 ]", "", text)
    text = text.strip()

    if not text:
        return "UNKNOWN"

    return text


def create_title_code(product_name):
    text = clean_text(product_name)

    if text == "UNKNOWN":
        return "UNKNOWN"

    words = text.split()

    if len(words) == 1:
        return words[0][:8]

    code_parts = []

    for word in words:
        code_parts.append(word[:3])

    return "".join(code_parts)[:10]


def create_grade_code(raw_or_slab, grade):
    raw_or_slab = clean_text(raw_or_slab)
    grade = clean_text(grade)

    if raw_or_slab == "RAW" or grade == "UNKNOWN":
        return "RAW"

    if raw_or_slab == "PSA":
        return f"PSA{grade}"

    if raw_or_slab == "BGS":
        return f"BGS{grade.replace('.', '')}"

    if raw_or_slab == "CGC":
        return f"CGC{grade.replace('.', '')}"

    return raw_or_slab


def get_next_counter(base_sku):
    if not os.path.isfile(INVENTORY_FILE):
        return 1

    counter = 1

    with open(INVENTORY_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            existing_sku = row.get("sku", "")

            if existing_sku.startswith(base_sku):
                counter += 1

    return counter


def generate_sku(product_name, raw_or_slab="Raw", grade=None):
    title_code = create_title_code(product_name)
    grade_code = create_grade_code(raw_or_slab, grade)

    base_sku = f"{title_code}{grade_code}"
    counter = get_next_counter(base_sku)

    if grade_code == "RAW":
        return f"{base_sku}{counter:03d}"

    return f"{base_sku}-{counter:02d}"
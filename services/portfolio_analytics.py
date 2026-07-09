import pandas as pd


INVENTORY_FILE = "data/inventory.csv"


def load_inventory():
    return pd.read_csv(INVENTORY_FILE)


def calculate_portfolio_value():
    df = load_inventory()

    df["selling_price"] = pd.to_numeric(
        df["selling_price"],
        errors="coerce"
    ).fillna(0)

    df["quantity"] = pd.to_numeric(
        df["quantity"],
        errors="coerce"
    ).fillna(0)

    total_value = (
        df["selling_price"] * df["quantity"]
    ).sum()

    return round(float(total_value), 2)


def calculate_portfolio_cost():
    df = load_inventory()

    df["cost"] = pd.to_numeric(
        df["cost"],
        errors="coerce"
    ).fillna(0)

    df["quantity"] = pd.to_numeric(
        df["quantity"],
        errors="coerce"
    ).fillna(0)

    total_cost = (
        df["cost"] * df["quantity"]
    ).sum()

    return round(float(total_cost), 2)


def calculate_portfolio_profit():
    total_value = calculate_portfolio_value()
    total_cost = calculate_portfolio_cost()

    return round(total_value - total_cost, 2)


def calculate_portfolio_margin():
    total_value = calculate_portfolio_value()
    total_profit = calculate_portfolio_profit()

    if total_value == 0:
        return 0

    margin = (
        total_profit / total_value
    ) * 100

    return round(margin, 2)


def get_portfolio_summary():
    total_value = calculate_portfolio_value()
    total_cost = calculate_portfolio_cost()
    total_profit = calculate_portfolio_profit()
    margin = calculate_portfolio_margin()

    return f"""
Portfolio Analytics

Total Collection Value: {total_value:,.2f} AED
Total Inventory Cost: {total_cost:,.2f} AED
Potential Profit: {total_profit:,.2f} AED
Portfolio Margin: {margin:.2f}%
"""

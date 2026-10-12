"""
loader.py — Data loading, cleaning, and joining for E-Commerce AI Engine.
"""
import os
import pandas as pd


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load Orders.csv and Details.csv, clean types, and return:
      (orders, details, merged)
    """
    orders = pd.read_csv(
        os.path.join(DATASET_DIR, "Orders.csv"),
        parse_dates=["Order Date"],
        dayfirst=True,
    )
    details = pd.read_csv(os.path.join(DATASET_DIR, "Details.csv"))

    # --- Clean Orders ---
    orders.columns = orders.columns.str.strip()
    orders["Order Date"] = pd.to_datetime(
        orders["Order Date"], dayfirst=True, errors="coerce"
    )
    orders["Month"] = orders["Order Date"].dt.month
    orders["Month Name"] = orders["Order Date"].dt.strftime("%b")
    orders["Quarter"] = orders["Order Date"].dt.quarter

    # --- Clean Details ---
    details.columns = details.columns.str.strip()
    details["Amount"] = pd.to_numeric(details["Amount"], errors="coerce").fillna(0)
    details["Profit"] = pd.to_numeric(details["Profit"], errors="coerce").fillna(0)
    details["Quantity"] = pd.to_numeric(details["Quantity"], errors="coerce").fillna(0)

    # Derive margin flag
    details["Is_Loss"] = details["Profit"] < 0
    details["Margin_Pct"] = (details["Profit"] / details["Amount"].replace(0, pd.NA)) * 100

    # --- Merge ---
    merged = pd.merge(details, orders, on="Order ID", how="left")

    return orders, details, merged

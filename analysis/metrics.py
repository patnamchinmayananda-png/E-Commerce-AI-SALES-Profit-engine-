"""
metrics.py — KPI calculations, RFM segmentation, and all dimensional breakdowns.
"""
import pandas as pd
import numpy as np


# ──────────────────────────────────────────────
# TOP-LINE KPIs
# ──────────────────────────────────────────────
def top_kpis(merged: pd.DataFrame) -> dict:
    total_revenue = merged["Amount"].sum()
    total_profit = merged["Profit"].sum()
    total_orders = merged["Order ID"].nunique()
    total_qty = merged["Quantity"].sum()
    total_customers = merged["CustomerName"].nunique()
    loss_txns = merged[merged["Is_Loss"]]["Profit"].sum()
    profit_margin = (total_profit / total_revenue * 100) if total_revenue else 0
    true_aov = total_revenue / total_orders if total_orders else 0

    return {
        "gross_revenue": round(total_revenue, 2),
        "net_profit": round(total_profit, 2),
        "profit_margin_pct": round(profit_margin, 2),
        "true_aov": round(true_aov, 2),
        "total_orders": int(total_orders),
        "total_customers": int(total_customers),
        "total_qty": int(total_qty),
        "loss_bleed": round(loss_txns, 2),
        "loss_txn_count": int(merged["Is_Loss"].sum()),
        "loss_txn_pct": round(merged["Is_Loss"].mean() * 100, 1),
    }


# ──────────────────────────────────────────────
# MONTHLY TRENDS
# ──────────────────────────────────────────────
MONTH_ORDER = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def monthly_trends(merged: pd.DataFrame) -> pd.DataFrame:
    df = (
        merged.groupby("Month Name", observed=True)
        .agg(Revenue=("Amount", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
        .reindex(MONTH_ORDER)
        .reset_index()
        .rename(columns={"Month Name": "Month"})
    )
    df["Margin_Pct"] = (df["Profit"] / df["Revenue"].replace(0, np.nan) * 100).round(1)
    return df


# ──────────────────────────────────────────────
# CATEGORY / SUB-CATEGORY BREAKDOWN
# ──────────────────────────────────────────────
def category_breakdown(merged: pd.DataFrame) -> pd.DataFrame:
    return (
        merged.groupby("Category", observed=True)
        .agg(Revenue=("Amount", "sum"), Profit=("Profit", "sum"), Qty=("Quantity", "sum"))
        .reset_index()
        .assign(Margin_Pct=lambda d: (d["Profit"] / d["Revenue"] * 100).round(1))
        .sort_values("Revenue", ascending=False)
    )


def subcategory_breakdown(merged: pd.DataFrame) -> pd.DataFrame:
    return (
        merged.groupby(["Category", "Sub-Category"], observed=True)
        .agg(Revenue=("Amount", "sum"), Profit=("Profit", "sum"), Qty=("Quantity", "sum"))
        .reset_index()
        .assign(Margin_Pct=lambda d: (d["Profit"] / d["Revenue"] * 100).round(1))
        .sort_values("Profit")
    )


# ──────────────────────────────────────────────
# PAYMENT MODE BREAKDOWN
# ──────────────────────────────────────────────
def payment_breakdown(merged: pd.DataFrame) -> pd.DataFrame:
    return (
        merged.groupby("PaymentMode", observed=True)
        .agg(Revenue=("Amount", "sum"), Profit=("Profit", "sum"), Qty=("Quantity", "sum"), Orders=("Order ID", "nunique"))
        .reset_index()
        .assign(Revenue_Pct=lambda d: (d["Revenue"] / d["Revenue"].sum() * 100).round(1))
        .sort_values("Revenue", ascending=False)
    )


# ──────────────────────────────────────────────
# STATE / CITY GEO BREAKDOWN
# ──────────────────────────────────────────────
def state_breakdown(merged: pd.DataFrame) -> pd.DataFrame:
    return (
        merged.groupby("State", observed=True)
        .agg(Revenue=("Amount", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
        .reset_index()
        .assign(Margin_Pct=lambda d: (d["Profit"] / d["Revenue"] * 100).round(1))
        .sort_values("Revenue", ascending=False)
    )


def city_breakdown(merged: pd.DataFrame) -> pd.DataFrame:
    return (
        merged.groupby(["State", "City"], observed=True)
        .agg(Revenue=("Amount", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
        .reset_index()
        .assign(Margin_Pct=lambda d: (d["Profit"] / d["Revenue"] * 100).round(1))
        .sort_values("Revenue", ascending=False)
    )


# ──────────────────────────────────────────────
# CUSTOMER BREAKDOWN
# ──────────────────────────────────────────────
def customer_breakdown(merged: pd.DataFrame) -> pd.DataFrame:
    cust = (
        merged.groupby("CustomerName", observed=True)
        .agg(Revenue=("Amount", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"), Qty=("Quantity", "sum"))
        .reset_index()
        .assign(Margin_Pct=lambda d: (d["Profit"] / d["Revenue"] * 100).round(1))
        .sort_values("Revenue", ascending=False)
    )
    return cust


# ──────────────────────────────────────────────
# RFM SEGMENTATION
# ──────────────────────────────────────────────
def rfm_segmentation(merged: pd.DataFrame) -> pd.DataFrame:
    snapshot_date = merged["Order Date"].max() + pd.Timedelta(days=1)

    rfm = (
        merged.groupby("CustomerName", observed=True)
        .agg(
            Recency=("Order Date", lambda x: (snapshot_date - x.max()).days),
            Frequency=("Order ID", "nunique"),
            Monetary=("Amount", "sum"),
        )
        .reset_index()
    )

    # Score 1–5 (5 = best)
    rfm["R_Score"] = pd.qcut(rfm["Recency"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["M_Score"] = pd.qcut(rfm["Monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["RFM_Score"] = rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]

    def segment(row):
        if row["RFM_Score"] >= 13:
            return "Champions"
        elif row["R_Score"] >= 4 and row["F_Score"] >= 3:
            return "Loyal Customers"
        elif row["R_Score"] >= 3 and row["F_Score"] <= 2:
            return "Potential Loyalists"
        elif row["R_Score"] <= 2 and row["F_Score"] >= 3:
            return "At Risk"
        elif row["R_Score"] <= 2 and row["M_Score"] >= 4:
            return "Can't Lose Them"
        elif row["RFM_Score"] <= 5:
            return "Lost"
        else:
            return "Needs Attention"

    rfm["Segment"] = rfm.apply(segment, axis=1)
    return rfm


# ──────────────────────────────────────────────
# LOSS DIAGNOSTIC
# ──────────────────────────────────────────────
def loss_diagnostic(merged: pd.DataFrame) -> dict:
    losses = merged[merged["Is_Loss"]]
    profitable = merged[~merged["Is_Loss"]]

    worst_subcats = (
        losses.groupby("Sub-Category")["Profit"].sum()
        .sort_values()
        .head(8)
        .reset_index()
        .rename(columns={"Profit": "Loss"})
    )
    worst_states = (
        losses.groupby("State")["Profit"].sum()
        .sort_values()
        .head(5)
        .reset_index()
        .rename(columns={"Profit": "Loss"})
    )

    return {
        "loss_total": round(losses["Profit"].sum(), 2),
        "profit_total": round(profitable["Profit"].sum(), 2),
        "loss_txn_count": len(losses),
        "worst_subcats": worst_subcats,
        "worst_states": worst_states,
    }

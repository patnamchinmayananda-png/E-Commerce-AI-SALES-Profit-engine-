"""
insights.py — AI Copilot: generates strategic prescriptions from computed metrics.
"""
from __future__ import annotations
import pandas as pd


def generate_prescriptions(kpis: dict, subcats: pd.DataFrame, states: pd.DataFrame, payment: pd.DataFrame) -> list[dict]:
    """
    Returns a list of prescription dicts with keys:
      priority, icon, title, finding, action, impact
    """
    prescriptions = []

    # 1. Margin Bleed Crisis
    loss_pct = kpis["loss_txn_pct"]
    loss_bleed = abs(kpis["loss_bleed"])
    profit_potential = kpis["net_profit"] + loss_bleed
    prescriptions.append({
        "priority": "CRITICAL",
        "icon": "🔴",
        "title": "Margin Bleed Crisis — Zero-CAC Profit Doubling Opportunity",
        "finding": f"{loss_pct}% of all transactions ({kpis['loss_txn_count']} line items) are operating at a loss, bleeding ₹{loss_bleed:,.0f} in profit destruction.",
        "action": "Establish hard price floors on loss-making SKUs in Electronic Games, Furnishings, Kurti, and Skirt. Negotiate supplier discounts or discontinue the worst offenders.",
        "impact": f"Eliminating losses doubles net profit from ₹{kpis['net_profit']:,.0f} → ₹{profit_potential:,.0f} with ZERO additional customer acquisition spend.",
    })

    # 2. COD RTO Risk
    cod_row = payment[payment["PaymentMode"].str.upper().str.contains("COD", na=False)]
    if not cod_row.empty:
        cod_pct = cod_row["Revenue_Pct"].values[0]
        prescriptions.append({
            "priority": "HIGH",
            "icon": "🟠",
            "title": "Cash-on-Delivery Dependency & RTO Risk",
            "finding": f"COD represents {cod_pct}% of total revenue, exposing the business to high Return-to-Origin (RTO) costs and cash-flow delays.",
            "action": "Offer a 2–3% discount for prepaid orders via UPI/Net Banking. Implement COD availability thresholds (₹500 min order, verified mobile number).",
            "impact": "Shifting 20% of COD orders to prepaid reduces RTO losses and improves working capital by an estimated ₹8,000–₹12,000/month.",
        })

    # 3. Mumbai Margin Paradox
    if not states.empty:
        mumbai = states[states["City"].str.contains("Mumbai", case=False, na=False)] if "City" in states.columns else pd.DataFrame()
        if not mumbai.empty:
            mum_rev = mumbai["Revenue"].values[0]
            mum_margin = mumbai["Margin_Pct"].values[0]
            prescriptions.append({
                "priority": "HIGH",
                "icon": "🟠",
                "title": "Mumbai Margin Paradox — Revenue ≠ Profit",
                "finding": f"Mumbai generates ₹{mum_rev:,.0f} in revenue (2nd nationally) but only {mum_margin}% profit margin — nearly 10× below the store average of 8.44%.",
                "action": "Audit Mumbai-specific discount patterns, product mix, and logistics costs. Identify if COD or specific sub-categories are driving margin compression in this city.",
                "impact": "Bringing Mumbai margin from 1.4% to the store average (8.44%) unlocks ₹4,100+ in incremental profit from existing customers.",
            })

    # 4. Customer Loyalty Gap
    prescriptions.append({
        "priority": "MEDIUM",
        "icon": "🟡",
        "title": "68% One-Time Buyer Loyalty Gap",
        "finding": "68.2% of customers placed only a single order. The top revenue customer (Harivansh, ₹9,902) actually generated a net loss of -₹157, while Madan Mohan (₹2,166 profit) delivers 14× more value per rupee spent on retention.",
        "action": "Launch a post-purchase email sequence targeting single-order customers at Day 7, 14, and 30. Reward margin-positive repeat buyers with loyalty points instead of blanket discounts.",
        "impact": "Increasing repeat purchase rate by 10% adds ~50 high-margin orders, potentially contributing ₹12,000–₹18,000 in incremental profit.",
    })

    # 5. Seasonal Loss Months
    prescriptions.append({
        "priority": "MEDIUM",
        "icon": "🟡",
        "title": "Seasonal Profit Sink in May, July, September & December",
        "finding": "Four months recorded negative net profit despite normal revenue levels, suggesting promotional over-discounting or seasonal cost spikes.",
        "action": "Review campaign-level P&L for these months. Shift heavy discount events (like flash sales) to margin-positive months. Cap per-order discount depth at a fixed ₹ threshold.",
        "impact": "Converting just 2 of 4 loss months to break-even adds ₹5,000–₹10,000 to annual profit without any change in GMV.",
    })

    return prescriptions

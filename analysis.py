"""
E-Commerce Store Analytics Engine & Insights Generator
Analyzes Orders.csv and Details.csv, computes accurate DAX-equivalent metrics,
RFM customer segmentation, basket affinity, and exports structured JSON for dashboard consumption.
"""

import csv
import json
from collections import defaultdict
from datetime import datetime

ORDERS_FILE = "dataset/Orders.csv"
DETAILS_FILE = "dataset/Details.csv"
OUTPUT_JSON = "dashboard_data.json"

def run_analysis():
    # 1. Load Orders
    orders_by_id = {}
    with open(ORDERS_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            oid = row["Order ID"].strip()
            if oid:
                orders_by_id[oid] = {
                    "order_id": oid,
                    "order_date": row["Order Date"].strip(),
                    "customer_name": row["CustomerName"].strip(),
                    "state": row["State"].strip(),
                    "city": row["City"].strip()
                }

    # 2. Load Details
    details = []
    with open(DETAILS_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            oid = row["Order ID"].strip()
            if oid:
                amount = float(row["Amount"])
                profit = float(row["Profit"])
                quantity = int(row["Quantity"])
                details.append({
                    "order_id": oid,
                    "amount": amount,
                    "profit": profit,
                    "quantity": quantity,
                    "category": row["Category"].strip(),
                    "sub_category": row["Sub-Category"].strip(),
                    "payment_mode": row["PaymentMode"].strip()
                })

    # Core Metrics
    total_revenue = sum(d["amount"] for d in details)
    total_profit = sum(d["profit"] for d in details)
    total_quantity = sum(d["quantity"] for d in details)
    unique_orders = len(orders_by_id)
    unique_customers = len(set(o["customer_name"] for o in orders_by_id.values()))
    
    true_aov = total_revenue / unique_orders if unique_orders else 0
    profit_margin = (total_profit / total_revenue * 100) if total_revenue else 0
    avg_unit_price = total_revenue / total_quantity if total_quantity else 0

    # Profitable vs Loss-making transactions
    profitable_tx = [d for d in details if d["profit"] >= 0]
    loss_tx = [d for d in details if d["profit"] < 0]
    gross_profit = sum(d["profit"] for d in profitable_tx)
    gross_loss = sum(d["profit"] for d in loss_tx)

    # Monthly Trends
    month_data = {m: {"sales": 0.0, "profit": 0.0, "orders": set(), "quantity": 0} for m in range(1, 13)}
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # Category & Sub-Category
    category_data = defaultdict(lambda: {"sales": 0.0, "profit": 0.0, "quantity": 0, "loss_count": 0, "total_count": 0})
    subcat_data = defaultdict(lambda: {"category": "", "sales": 0.0, "profit": 0.0, "quantity": 0, "loss_count": 0, "total_count": 0})

    # Payment Mode
    pm_data = defaultdict(lambda: {"sales": 0.0, "profit": 0.0, "quantity": 0, "orders": set()})

    # State & City
    state_data = defaultdict(lambda: {"sales": 0.0, "profit": 0.0, "orders": set(), "cities": set()})
    city_data = defaultdict(lambda: {"state": "", "sales": 0.0, "profit": 0.0, "orders": set()})

    # Customer Aggregations
    cust_orders = defaultdict(lambda: {"orders": set(), "sales": 0.0, "profit": 0.0, "last_date": None, "state": "", "city": ""})

    # Order Multi-item check for Basket Analysis
    order_subcats = defaultdict(list)

    for d in details:
        oid = d["order_id"]
        amt = d["amount"]
        prof = d["profit"]
        qty = d["quantity"]
        cat = d["category"]
        subcat = d["sub_category"]
        pm = d["payment_mode"]

        o = orders_by_id.get(oid, {})
        cname = o.get("customer_name", "Unknown")
        state = o.get("state", "Unknown")
        city = o.get("city", "Unknown")
        odate_str = o.get("order_date", "")

        dt = datetime.strptime(odate_str, "%d-%m-%Y") if odate_str else None
        if dt:
            m = dt.month
            month_data[m]["sales"] += amt
            month_data[m]["profit"] += prof
            month_data[m]["quantity"] += qty
            month_data[m]["orders"].add(oid)

        category_data[cat]["sales"] += amt
        category_data[cat]["profit"] += prof
        category_data[cat]["quantity"] += qty
        category_data[cat]["total_count"] += 1
        if prof < 0:
            category_data[cat]["loss_count"] += 1

        subcat_data[subcat]["category"] = cat
        subcat_data[subcat]["sales"] += amt
        subcat_data[subcat]["profit"] += prof
        subcat_data[subcat]["quantity"] += qty
        subcat_data[subcat]["total_count"] += 1
        if prof < 0:
            subcat_data[subcat]["loss_count"] += 1

        pm_data[pm]["sales"] += amt
        pm_data[pm]["profit"] += prof
        pm_data[pm]["quantity"] += qty
        pm_data[pm]["orders"].add(oid)

        state_data[state]["sales"] += amt
        state_data[state]["profit"] += prof
        state_data[state]["orders"].add(oid)
        state_data[state]["cities"].add(city)

        city_data[city]["state"] = state
        city_data[city]["sales"] += amt
        city_data[city]["profit"] += prof
        city_data[city]["orders"].add(oid)

        cust_orders[cname]["orders"].add(oid)
        cust_orders[cname]["sales"] += amt
        cust_orders[cname]["profit"] += prof
        cust_orders[cname]["state"] = state
        cust_orders[cname]["city"] = city
        if dt:
            if cust_orders[cname]["last_date"] is None or dt > cust_orders[cname]["last_date"]:
                cust_orders[cname]["last_date"] = dt

        order_subcats[oid].append(subcat)

    # Co-occurrence / Market Basket pairs
    co_occurrences = defaultdict(int)
    for oid, sublist in order_subcats.items():
        unique_subs = sorted(list(set(sublist)))
        for i in range(len(unique_subs)):
            for j in range(i + 1, len(unique_subs)):
                co_occurrences[f"{unique_subs[i]} + {unique_subs[j]}"] += 1

    top_basket_pairs = sorted(co_occurrences.items(), key=lambda x: x[1], reverse=True)[:10]

    # Customer RFM Segmentation
    # Reference date: End of 2018 (2018-12-31)
    ref_date = datetime(2018, 12, 31)
    customers_rfm = []
    for cname, cinfo in cust_orders.items():
        recency_days = (ref_date - cinfo["last_date"]).days if cinfo["last_date"] else 365
        freq = len(cinfo["orders"])
        monetary = cinfo["sales"]
        profit = cinfo["profit"]

        # Simple RFM classification
        if freq >= 3 and monetary >= 2000:
            segment = "Champion / VIP"
        elif freq >= 2 and profit > 0:
            segment = "Loyal Customer"
        elif monetary >= 2500 and profit < 0:
            segment = "High Volume, Negative Margin"
        elif recency_days > 180 and freq == 1:
            segment = "Dormant / Single Buyer"
        else:
            segment = "Promising / Occasional"

        customers_rfm.append({
            "name": cname,
            "recency_days": recency_days,
            "orders_count": freq,
            "sales": round(monetary, 2),
            "profit": round(profit, 2),
            "margin_pct": round(profit / monetary * 100, 1) if monetary else 0,
            "state": cinfo["state"],
            "city": cinfo["city"],
            "segment": segment
        })

    # Prepare export JSON structure
    export_payload = {
        "kpis": {
            "total_revenue": round(total_revenue, 2),
            "total_profit": round(total_profit, 2),
            "gross_profit": round(gross_profit, 2),
            "gross_loss": round(gross_loss, 2),
            "profit_margin_pct": round(profit_margin, 2),
            "total_quantity": total_quantity,
            "distinct_orders": unique_orders,
            "distinct_customers": unique_customers,
            "true_aov": round(true_aov, 2),
            "avg_unit_price": round(avg_unit_price, 2),
            "loss_transactions_count": len(loss_tx),
            "loss_transactions_pct": round(len(loss_tx) / len(details) * 100, 2),
            "repeat_customers_count": sum(1 for c in customers_rfm if c["orders_count"] > 1),
            "repeat_customers_pct": round(sum(1 for c in customers_rfm if c["orders_count"] > 1) / unique_customers * 100, 2)
        },
        "monthly_trend": [
            {
                "month_num": m,
                "month_name": month_names[m-1],
                "sales": round(month_data[m]["sales"], 2),
                "profit": round(month_data[m]["profit"], 2),
                "quantity": month_data[m]["quantity"],
                "orders": len(month_data[m]["orders"]),
                "margin_pct": round(month_data[m]["profit"] / month_data[m]["sales"] * 100, 2) if month_data[m]["sales"] else 0
            }
            for m in range(1, 13)
        ],
        "categories": [
            {
                "category": cat,
                "sales": round(v["sales"], 2),
                "profit": round(v["profit"], 2),
                "quantity": v["quantity"],
                "margin_pct": round(v["profit"] / v["sales"] * 100, 2) if v["sales"] else 0,
                "loss_rate_pct": round(v["loss_count"] / v["total_count"] * 100, 2) if v["total_count"] else 0
            }
            for cat, v in sorted(category_data.items(), key=lambda x: x[1]["sales"], reverse=True)
        ],
        "sub_categories": [
            {
                "sub_category": sub,
                "category": v["category"],
                "sales": round(v["sales"], 2),
                "profit": round(v["profit"], 2),
                "quantity": v["quantity"],
                "margin_pct": round(v["profit"] / v["sales"] * 100, 2) if v["sales"] else 0,
                "loss_rate_pct": round(v["loss_count"] / v["total_count"] * 100, 2) if v["total_count"] else 0
            }
            for sub, v in sorted(subcat_data.items(), key=lambda x: x[1]["profit"], reverse=True)
        ],
        "payment_modes": [
            {
                "payment_mode": pm,
                "sales": round(v["sales"], 2),
                "profit": round(v["profit"], 2),
                "quantity": v["quantity"],
                "orders": len(v["orders"]),
                "sales_pct": round(v["sales"] / total_revenue * 100, 2) if total_revenue else 0,
                "margin_pct": round(v["profit"] / v["sales"] * 100, 2) if v["sales"] else 0
            }
            for pm, v in sorted(pm_data.items(), key=lambda x: x[1]["sales"], reverse=True)
        ],
        "states": [
            {
                "state": st,
                "sales": round(v["sales"], 2),
                "profit": round(v["profit"], 2),
                "orders": len(v["orders"]),
                "city_count": len(v["cities"]),
                "margin_pct": round(v["profit"] / v["sales"] * 100, 2) if v["sales"] else 0
            }
            for st, v in sorted(state_data.items(), key=lambda x: x[1]["sales"], reverse=True)
        ],
        "top_cities": [
            {
                "city": ct,
                "state": v["state"],
                "sales": round(v["sales"], 2),
                "profit": round(v["profit"], 2),
                "orders": len(v["orders"]),
                "margin_pct": round(v["profit"] / v["sales"] * 100, 2) if v["sales"] else 0
            }
            for ct, v in sorted(city_data.items(), key=lambda x: x[1]["sales"], reverse=True)
        ],
        "customers": sorted(customers_rfm, key=lambda x: x["sales"], reverse=True),
        "basket_affinities": [
            {"pair": pair, "count": count} for pair, count in top_basket_pairs
        ],
        "orders_raw": [
            {
                "order_id": d["order_id"],
                "customer_name": orders_by_id[d["order_id"]]["customer_name"],
                "state": orders_by_id[d["order_id"]]["state"],
                "city": orders_by_id[d["order_id"]]["city"],
                "order_date": orders_by_id[d["order_id"]]["order_date"],
                "category": d["category"],
                "sub_category": d["sub_category"],
                "amount": d["amount"],
                "profit": d["profit"],
                "quantity": d["quantity"],
                "payment_mode": d["payment_mode"]
            }
            for d in details
        ]
    }

    with open(OUTPUT_JSON, mode="w", encoding="utf-8") as f:
        json.dump(export_payload, f, indent=2)

    print(f"=== Analysis Completed Successfully ===")
    print(f"Total Revenue: ₹{total_revenue:,.2f}")
    print(f"Total Profit:  ₹{total_profit:,.2f} ({profit_margin:.2f}% Margin)")
    print(f"True AOV:      ₹{true_aov:.2f} (Previously miscalculated as 121K)")
    print(f"Gross Loss:   ₹{gross_loss:,.2f} across {len(loss_tx)} items ({len(loss_tx)/len(details)*100:.1f}%)")
    print(f"Exported clean dashboard payload to: {OUTPUT_JSON}")

if __name__ == "__main__":
    run_analysis()

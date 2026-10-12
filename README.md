# 🤖 E-Commerce AI Sales & Profit Engine

[![🌐 Live Demo](https://img.shields.io/badge/🌐_Live_Demo-Render.com-22C55E?style=for-the-badge&logo=render&logoColor=white)](https://github.com/patnamchinmayananda-png/E-Commerce-AI-SALES-Profit-engine-)
[![CI Validation](https://github.com/patnamchinmayananda-png/E-Commerce-AI-SALES-Profit-engine-/actions/workflows/deploy.yml/badge.svg)](https://github.com/patnamchinmayananda-png/E-Commerce-AI-SALES-Profit-engine-/actions/workflows/deploy.yml)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Dash](https://img.shields.io/badge/Dash-Plotly-0081C8?style=for-the-badge&logo=plotly&logoColor=white)](https://dash.plotly.com)
[![Power BI](https://img.shields.io/badge/Power_BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)](https://powerbi.microsoft.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

An end-to-end **fully Python** analytical study, AI diagnostic copilot, and autonomous business decision engine for an Indian E-Commerce retail store operating across pan-India territories in FY 2018 (500 orders, 1,500 line items).

Built entirely in **Python** using **Dash + Plotly** — no JavaScript frameworks, no HTML files.

---

## 🌐 Live Demo

> **✅ Deployed on Render.com**  
> 👉 **Deploy your own free instance in one click** → [Render.com](https://render.com) → New Web Service → Connect this GitHub repo

**Local run:**
```bash
python3 app.py
# Opens at http://localhost:8050
```

---

## 📈 Dashboard Showcase

### 🌟 Python Dash AI Sales & Profit Engine

<details>
<summary><b>🔍 View Legacy Power BI Dashboard (With 121K AOV Bug & Hidden Losses)</b></summary>
<br>

![Legacy Dashboard](assets/original_dashboard_buggy.png)
*Audited flaws: Displayed "121K AOV" due to a `SUM()` on row-level ratios; hid 35.3% loss transactions; celebrated Harivansh as #1 customer despite his net negative margin (-₹157).*
</details>

---

## 🎯 Executive KPI Summary

| Metric | Measured Value | Notes & Calibration |
| :--- | :---: | :--- |
| **Gross Revenue** | **₹437,771.00** | Total sales volume generated across 500 orders |
| **Net Profit** | **₹36,963.00** | Net earnings after negative-margin transactions |
| **Net Profit Margin** | **8.44%** | Store-wide margin efficiency |
| **True AOV (Average Order Value)** | **₹875.54** | Correct calculation: Total Revenue / Distinct Orders |
| **Average Item Price** | **₹77.96** | Revenue / Total Units Sold (5,615 units) |
| **Total Orders / Customers** | **500 / 336** | 68.2% single-order, 31.8% repeat customers |
| **Loss Transactions Bleed** | **-₹38,079.00** | **35.3% of items** (529 transactions) operated at a loss! |

---

## 🔍 Key Strategic Findings & Interview Highlights

1. **The 35.3% Margin Bleed Crisis (Zero-CAC Profit Doubling)**:
   - The store made **+₹75,042** on profitable transactions, but **lost -₹38,079** on unprofitable items.
   - Eliminating or establishing price floors on negative-margin SKUs in *Electronic Games* (-₹644), *Furnishings* (-₹806), *Kurti* (-₹401), and *Skirt* (-₹315) will **double net profit to ₹75K** without spending any customer acquisition budget (Zero CAC).
2. **The "Harivansh Paradox" (Revenue is Vanity, Margin is Sanity)**:
   - The #1 spender by gross revenue (Harivansh, ₹9,902 spend) resulted in a **net loss of -₹157**, while customer Madan Mohan produced **+₹2,166 in net profit**.
3. **The "Mumbai Margin Paradox"**:
   - **Mumbai** generated the 2nd highest revenue nationwide (**₹58,886**), but yielded only **₹803 profit (1.4% margin)**.
   - In comparison, **Pune** generated **₹43,612** in sales with **₹6,160 in profit (14.1% margin)**—**7.7x more profit** on lower sales volume.
4. **Cash-on-Delivery (COD) Dependency**:
   - COD accounts for **35.4% of total sales** (₹155.2K) and **44% of quantity**, exposing operations to high courier Return to Origin (RTO) risks.

👉 **Interview Preparation:** See the full [INTERVIEW_PLAYBOOK.md](INTERVIEW_PLAYBOOK.md)  
👉 **Executive Business Report:** See [BUSINESS_INSIGHTS.md](BUSINESS_INSIGHTS.md)

---

## 🗂️ Project Structure

```bash
├── app.py                        # 🐍 Main Dash application (all charts, callbacks, layout)
├── analysis/
│   ├── __init__.py
│   ├── loader.py                 # Data loading, cleaning & joining (Orders + Details)
│   ├── metrics.py                # KPI engine: AOV, RFM, monthly trends, loss diagnostic
│   └── insights.py               # AI Copilot: generates strategic prescriptions
├── assets/
│   └── custom.css                # Dark glassmorphism design system (served by Dash)
├── dataset/
│   ├── Orders.csv                # Order ID, Order Date, Customer, State, City
│   └── Details.csv               # Order ID, Amount, Profit, Quantity, Category, Sub-Category, Payment
├── analysis.py                   # Standalone Python analytical engine (legacy CLI)
├── ecommerce_analysis.ipynb      # Jupyter Notebook for EDA & RFM data science
├── E-commerce Sales Dashboard.pbix # Power BI Dashboard (with audited bugs documented)
├── requirements.txt              # Python dependencies: dash, plotly, pandas, numpy, gunicorn
├── Procfile                      # Production deployment (Render/Heroku/Railway)
├── runtime.txt                   # Python 3.13.6
├── .github/workflows/deploy.yml  # CI: validates data load, metrics & Dash imports
├── INTERVIEW_PLAYBOOK.md         # Interview pitch strategies, STAR answers & cheat sheet
├── DAX_MEASURES.md               # Production DAX measures & Star Schema guide
├── BUSINESS_INSIGHTS.md          # Executive diagnostic report
├── results.txt                   # Quick-reference executive results
└── README.md                     # This file
```

---

## 🚀 How to Run

### 1. Clone & Install
```bash
git clone https://github.com/patnamchinmayananda-png/E-Commerce-AI-SALES-Profit-engine-.git
cd E-Commerce-AI-SALES-Profit-engine-
pip install -r requirements.txt
```

### 2. Run the Dash Dashboard
```bash
python3 app.py
# 🚀 Opens at http://localhost:8050
```

### 3. Jupyter Notebook (Python EDA)
```bash
jupyter notebook ecommerce_analysis.ipynb
```

### 4. Microsoft Power BI Desktop (Windows)
1. Open `E-commerce Sales Dashboard.pbix` in Microsoft Power BI Desktop.
2. Review [DAX_MEASURES.md](DAX_MEASURES.md) for corrected DAX formulas.

---

## 🚀 Deploy to Render.com (Free)

1. Fork this repo
2. Go to [Render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repo
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:server`
   - **Environment:** Python 3
5. Click **Deploy** — live in ~2 minutes!

---

## 🛠️ Tools & Technologies Used

| Layer | Tech |
|-------|------|
| **Dashboard** | Dash 2.18 + Plotly 5.24 (100% Python) |
| **Data Processing** | Pandas 2.2, NumPy 2.3 |
| **Segmentation** | Custom RFM scoring (Recency, Frequency, Monetary) |
| **Deployment** | Gunicorn + Render/Heroku/Railway |
| **CI/CD** | GitHub Actions (validates data + Dash imports on every push) |
| **BI Tool** | Microsoft Power BI (audited & corrected DAX) |
| **Design** | Dark Glassmorphism CSS (Inter + JetBrains Mono fonts) |

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).

---

<div align="center">

**⭐ Star this repo if you found it useful!**

[🐍 Dash App](https://github.com/patnamchinmayananda-png/E-Commerce-AI-SALES-Profit-engine-) · [📊 Repository](https://github.com/patnamchinmayananda-png/E-Commerce-AI-SALES-Profit-engine-) · [🐛 Issues](https://github.com/patnamchinmayananda-png/E-Commerce-AI-SALES-Profit-engine-/issues)

</div>

"""
app.py — E-Commerce AI Sales & Profit Engine
Fully Python-powered interactive dashboard built with Dash + Plotly.

Run locally:
    python app.py

Deploy:
    gunicorn app:server --bind 0.0.0.0:$PORT
"""
import os
import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from analysis.loader import load_data
from analysis.metrics import (
    top_kpis,
    monthly_trends,
    category_breakdown,
    subcategory_breakdown,
    payment_breakdown,
    state_breakdown,
    city_breakdown,
    customer_breakdown,
    rfm_segmentation,
    loss_diagnostic,
)
from analysis.insights import generate_prescriptions

# ══════════════════════════════════════════════════════════════════
# DATA LOAD (once at startup)
# ══════════════════════════════════════════════════════════════════
orders_df, details_df, merged_df = load_data()

STATES = sorted(merged_df["State"].dropna().unique().tolist())
CATEGORIES = sorted(merged_df["Category"].dropna().unique().tolist())
PAYMENT_MODES = sorted(merged_df["PaymentMode"].dropna().unique().tolist())

# ══════════════════════════════════════════════════════════════════
# PLOTLY THEME
# ══════════════════════════════════════════════════════════════════
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#94a3b8", size=11),
    margin=dict(l=10, r=10, t=36, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#94a3b8"),
    colorway=["#6366f1", "#10b981", "#f59e0b", "#06b6d4", "#f43f5e", "#8b5cf6", "#ec4899"],
)

AXIS_STYLE = dict(
    gridcolor="rgba(255,255,255,0.05)",
    zerolinecolor="rgba(255,255,255,0.08)",
    linecolor="rgba(255,255,255,0.05)",
    tickfont=dict(color="#475569", size=10),
    title_font=dict(color="#64748b", size=11),
)

# ══════════════════════════════════════════════════════════════════
# APP INIT
# ══════════════════════════════════════════════════════════════════
app = dash.Dash(
    __name__,
    title="E-Commerce AI Sales & Profit Engine",
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "description", "content": "AI-powered e-commerce analytics dashboard with RFM segmentation, profit diagnostics, and strategic prescriptions."},
    ],
    suppress_callback_exceptions=True,
)
server = app.server  # Expose Flask server for gunicorn


# ══════════════════════════════════════════════════════════════════
# HELPER: build KPI card
# ══════════════════════════════════════════════════════════════════
def kpi_card(icon, label, value, cls="", delta=""):
    return html.Div([
        html.Div(icon, className="kpi-icon"),
        html.Div(label, className="kpi-label"),
        html.Div(value, className=f"kpi-value {cls}"),
        html.Div(delta, className="kpi-delta") if delta else None,
    ], className=f"kpi-card {'critical' if cls == 'red' else ('positive' if cls == 'green' else '')}")


# ══════════════════════════════════════════════════════════════════
# LAYOUT
# ══════════════════════════════════════════════════════════════════
app.layout = html.Div([

    # ── NAVBAR ──────────────────────────────────────────────────
    html.Nav([
        html.Div([
            html.Span("🤖", style={"fontSize": "1.3rem"}),
            html.Span([
                html.Span("AI Sales ", className="accent"),
                "& Profit Engine",
            ]),
            html.Span("E-Commerce · FY 2018 · India", className="nav-badge"),
        ], className="navbar-brand"),
        html.Div([
            html.A("Overview",       href="#overview",    className="nav-link"),
            html.A("P&L Diagnosis",  href="#pnl",         className="nav-link"),
            html.A("Geo Analysis",   href="#geo",         className="nav-link"),
            html.A("Customers",      href="#customers",   className="nav-link"),
            html.A("AI Copilot",     href="#copilot",     className="nav-link"),
        ], className="nav-links"),
    ], className="navbar"),

    # ── STORE (shared filter state) ─────────────────────────────
    dcc.Store(id="filter-store"),

    # ── MAIN CONTENT ────────────────────────────────────────────
    html.Div([

        # ── PAGE HEADER ─────────────────────────────────────────
        html.Div([
            html.H1("E-Commerce AI Sales & Profit Engine", className="page-title"),
            html.P(
                "End-to-end analytical study of 500 orders · 1,500 line items · pan-India territories · FY 2018",
                className="page-subtitle",
            ),
        ], className="page-header", id="overview"),

        # ── GLOBAL FILTERS ──────────────────────────────────────
        html.Div([
            html.Span("🔍 Filters", className="filter-label", style={"marginRight": "6px"}),
            html.Div([
                html.Div("State", className="filter-label"),
                dcc.Dropdown(
                    id="filter-state", options=[{"label": s, "value": s} for s in STATES],
                    multi=True, placeholder="All States",
                    style={"minWidth": "200px", "background": "transparent"},
                    className="dark-dropdown",
                ),
            ]),
            html.Div([
                html.Div("Category", className="filter-label"),
                dcc.Dropdown(
                    id="filter-category", options=[{"label": c, "value": c} for c in CATEGORIES],
                    multi=True, placeholder="All Categories",
                    style={"minWidth": "170px"},
                ),
            ]),
            html.Div([
                html.Div("Payment", className="filter-label"),
                dcc.Dropdown(
                    id="filter-payment", options=[{"label": p, "value": p} for p in PAYMENT_MODES],
                    multi=True, placeholder="All Modes",
                    style={"minWidth": "170px"},
                ),
            ]),
        ], className="filters-bar"),

        # ── KPI CARDS ───────────────────────────────────────────
        html.Div(id="kpi-cards", className="kpi-grid"),

        # ── ROW 1: Monthly Trends + Category Donut ───────────────
        html.Div([
            html.Div([
                html.Div([
                    html.Span("📅 Monthly Revenue & Profit Trends", className="card-title"),
                ], className="card-header"),
                dcc.Graph(id="chart-monthly", config={"displayModeBar": False}),
            ], className="chart-card span-2"),

            html.Div([
                html.Div([
                    html.Span("🛍️ Revenue by Category", className="card-title"),
                ], className="card-header"),
                dcc.Graph(id="chart-category-donut", config={"displayModeBar": False}),
            ], className="chart-card"),
        ], className="chart-grid-3", id="pnl"),

        # ── ROW 2: Sub-Category Profit Diverging + Payment ─────
        html.Div([
            html.Div([
                html.Div([
                    html.Span("⚡ Sub-Category Profit / Loss Breakdown", className="card-title"),
                    html.Div("Loss items highlighted in red", className="card-subtitle"),
                ], className="card-header"),
                dcc.Graph(id="chart-subcategory", config={"displayModeBar": False}),
            ], className="chart-card"),

            html.Div([
                html.Div([
                    html.Span("💳 Payment Mode Analysis", className="card-title"),
                ], className="card-header"),
                dcc.Graph(id="chart-payment", config={"displayModeBar": False}),
            ], className="chart-card"),
        ], className="chart-grid-2"),

        # ── ROW 3: State Map (bar) + City Table ─────────────────
        html.Div([
            html.Div([
                html.Div([
                    html.Span("🗺️ Revenue by State", className="card-title"),
                ], className="card-header"),
                dcc.Graph(id="chart-state", config={"displayModeBar": False}),
            ], className="chart-card span-2"),

            html.Div([
                html.Div([
                    html.Span("🏙️ Top Cities", className="card-title"),
                ], className="card-header"),
                html.Div(id="table-city", className="data-table-container"),
            ], className="chart-card"),
        ], className="chart-grid-3", id="geo"),

        # ── ROW 4: Loss Diagnostic ──────────────────────────────
        html.Div([
            html.Div([
                html.Div([
                    html.Span("🩸 Loss Bleed by Sub-Category", className="card-title"),
                    html.Div("Worst loss-making segments", className="card-subtitle"),
                ], className="card-header"),
                dcc.Graph(id="chart-loss-subcats", config={"displayModeBar": False}),
            ], className="chart-card"),

            html.Div([
                html.Div([
                    html.Span("📊 Profit Pool: Profitable vs Loss Transactions", className="card-title"),
                ], className="card-header"),
                dcc.Graph(id="chart-profit-pool", config={"displayModeBar": False}),
            ], className="chart-card"),
        ], className="chart-grid-2"),

        # ── ROW 5: Customer Intelligence ────────────────────────
        html.Div([

            html.Div([
                html.Div([
                    html.Span("👤 Top 15 Customers — Revenue vs Profit", className="card-title"),
                    html.Div("Harivansh Paradox: highest revenue, net loss", className="card-subtitle"),
                ], className="card-header"),
                dcc.Graph(id="chart-customers", config={"displayModeBar": False}),
            ], className="chart-card span-2"),

            html.Div([
                html.Div([
                    html.Span("🎯 RFM Segment Distribution", className="card-title"),
                ], className="card-header"),
                dcc.Graph(id="chart-rfm", config={"displayModeBar": False}),
            ], className="chart-card"),

        ], className="chart-grid-3", id="customers"),

        # ── RFM TABLE ───────────────────────────────────────────
        html.Div([
            html.Div([
                html.Div([
                    html.Span("🧬 Full RFM Customer Segmentation Table", className="card-title"),
                    html.Div("Recency · Frequency · Monetary scoring (1–5)", className="card-subtitle"),
                ], className="card-header"),
                html.Div(id="table-rfm", className="data-table-container", style={"maxHeight": "400px", "overflowY": "auto"}),
            ], className="chart-card"),
        ], className="chart-grid-full"),

        # ── AI COPILOT ──────────────────────────────────────────
        html.Div([
            html.Div([
                html.Div("🤖", className="copilot-avatar"),
                html.Div([
                    html.Div("AI Sales Copilot", className="copilot-name"),
                    html.Div("Active · 5 Strategic Prescriptions Ready", className="copilot-status"),
                ]),
            ], className="copilot-header"),
            html.Div(id="ai-prescriptions"),
        ], id="copilot"),

    ], className="main-wrapper"),

    # ── FOOTER ──────────────────────────────────────────────────
    html.Footer([
        html.Span("E-Commerce AI Sales & Profit Engine · FY 2018 · Built with "),
        html.A("Dash + Plotly", href="https://dash.plotly.com", target="_blank"),
        html.Span(" · "),
        html.A("GitHub", href="https://github.com/patnamchinmayananda-png/E-Commerce-AI-SALES-Profit-engine-", target="_blank"),
    ], className="footer"),

], style={"minHeight": "100vh"})


# ══════════════════════════════════════════════════════════════════
# CALLBACKS
# ══════════════════════════════════════════════════════════════════
def filter_data(states, categories, payments):
    """Apply global filters and return filtered merged dataframe."""
    df = merged_df.copy()
    if states:
        df = df[df["State"].isin(states)]
    if categories:
        df = df[df["Category"].isin(categories)]
    if payments:
        df = df[df["PaymentMode"].isin(payments)]
    return df


# ── KPI Cards ────────────────────────────────────────────────────
@callback(
    Output("kpi-cards", "children"),
    Input("filter-state", "value"),
    Input("filter-category", "value"),
    Input("filter-payment", "value"),
)
def update_kpis(states, categories, payments):
    df = filter_data(states, categories, payments)
    k = top_kpis(df)
    return [
        kpi_card("💰", "Gross Revenue",   f"₹{k['gross_revenue']:,.0f}",   "indigo", f"{k['total_orders']} orders"),
        kpi_card("📈", "Net Profit",       f"₹{k['net_profit']:,.0f}",       "green",  f"{k['profit_margin_pct']}% margin"),
        kpi_card("🎯", "True AOV",         f"₹{k['true_aov']:,.2f}",         "cyan",   "Revenue / Orders"),
        kpi_card("📦", "Units Sold",       f"{k['total_qty']:,}",            "amber",  f"{k['total_customers']} customers"),
        kpi_card("🩸", "Loss Bleed",       f"₹{abs(k['loss_bleed']):,.0f}",  "red",    f"{k['loss_txn_pct']}% of transactions"),
    ]


# ── Monthly Chart ────────────────────────────────────────────────
@callback(
    Output("chart-monthly", "figure"),
    Input("filter-state", "value"),
    Input("filter-category", "value"),
    Input("filter-payment", "value"),
)
def update_monthly(states, categories, payments):
    df = filter_data(states, categories, payments)
    mon = monthly_trends(df)

    fig = go.Figure()
    fig.add_bar(
        x=mon["Month"], y=mon["Revenue"],
        name="Revenue", marker_color="#6366f1",
        marker_line_width=0, opacity=0.85,
    )
    fig.add_bar(
        x=mon["Month"], y=mon["Profit"],
        name="Profit",
        marker_color=[("#10b981" if v >= 0 else "#f43f5e") for v in mon["Profit"]],
        marker_line_width=0, opacity=0.9,
    )
    fig.add_scatter(
        x=mon["Month"], y=mon["Margin_Pct"],
        name="Margin %", yaxis="y2",
        mode="lines+markers",
        line=dict(color="#f59e0b", width=2, dash="dot"),
        marker=dict(size=6, color="#f59e0b"),
    )
    fig.add_hline(y=0, line_dash="dot", line_color="rgba(255,255,255,0.2)", line_width=1)
    fig.update_layout(
        **PLOTLY_LAYOUT,
        barmode="group",
        height=320,
        xaxis=dict(**AXIS_STYLE),
        yaxis=dict(**AXIS_STYLE, title="₹ Amount"),
        yaxis2=dict(
            overlaying="y", side="right", title="Margin %",
            tickfont=dict(color="#f59e0b", size=10),
            title_font=dict(color="#f59e0b"),
            gridcolor="rgba(0,0,0,0)",
        ),
    )
    return fig


# ── Category Donut ────────────────────────────────────────────────
@callback(
    Output("chart-category-donut", "figure"),
    Input("filter-state", "value"),
    Input("filter-category", "value"),
    Input("filter-payment", "value"),
)
def update_category_donut(states, categories, payments):
    df = filter_data(states, categories, payments)
    cat = category_breakdown(df)

    fig = go.Figure(go.Pie(
        labels=cat["Category"],
        values=cat["Revenue"],
        hole=0.6,
        marker_colors=["#6366f1", "#10b981", "#f59e0b"],
        textinfo="label+percent",
        textfont=dict(size=11, color="#f1f5f9"),
        hovertemplate="<b>%{label}</b><br>Revenue: ₹%{value:,.0f}<br>Share: %{percent}<extra></extra>",
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=300, showlegend=False)
    fig.add_annotation(text="Revenue<br>Split", x=0.5, y=0.5, showarrow=False,
                       font=dict(size=12, color="#94a3b8"))
    return fig


# ── Sub-Category Diverging Bar ────────────────────────────────────
@callback(
    Output("chart-subcategory", "figure"),
    Input("filter-state", "value"),
    Input("filter-category", "value"),
    Input("filter-payment", "value"),
)
def update_subcategory(states, categories, payments):
    df = filter_data(states, categories, payments)
    sub = subcategory_breakdown(df).head(20)

    colors = ["#f43f5e" if v < 0 else "#10b981" for v in sub["Profit"]]
    fig = go.Figure(go.Bar(
        x=sub["Profit"], y=sub["Sub-Category"],
        orientation="h",
        marker_color=colors, marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Profit: ₹%{x:,.0f}<extra></extra>",
    ))
    fig.add_vline(x=0, line_color="rgba(255,255,255,0.2)", line_width=1)
    fig.update_layout(
        **PLOTLY_LAYOUT, height=380,
        xaxis=dict(**AXIS_STYLE, title="Profit (₹)"),
        yaxis=dict(**AXIS_STYLE, autorange="reversed"),
    )
    return fig


# ── Payment Mode Chart ────────────────────────────────────────────
@callback(
    Output("chart-payment", "figure"),
    Input("filter-state", "value"),
    Input("filter-category", "value"),
    Input("filter-payment", "value"),
)
def update_payment(states, categories, payments):
    df = filter_data(states, categories, payments)
    pay = payment_breakdown(df)

    fig = go.Figure()
    fig.add_bar(
        x=pay["PaymentMode"], y=pay["Revenue"],
        name="Revenue", marker_color="#6366f1", marker_line_width=0,
    )
    fig.add_bar(
        x=pay["PaymentMode"], y=pay["Profit"],
        name="Profit",
        marker_color=[("#10b981" if v >= 0 else "#f43f5e") for v in pay["Profit"]],
        marker_line_width=0,
    )
    fig.update_layout(
        **PLOTLY_LAYOUT, barmode="group", height=300,
        xaxis=dict(**AXIS_STYLE),
        yaxis=dict(**AXIS_STYLE, title="₹"),
    )
    return fig


# ── State Bar Chart ────────────────────────────────────────────────
@callback(
    Output("chart-state", "figure"),
    Input("filter-state", "value"),
    Input("filter-category", "value"),
    Input("filter-payment", "value"),
)
def update_state(states, categories, payments):
    df = filter_data(states, categories, payments)
    st = state_breakdown(df).head(15)

    fig = go.Figure()
    fig.add_bar(
        x=st["State"], y=st["Revenue"],
        name="Revenue", marker_color="#6366f1", marker_line_width=0, opacity=0.85,
    )
    fig.add_bar(
        x=st["State"], y=st["Profit"],
        name="Profit",
        marker_color=[("#10b981" if v >= 0 else "#f43f5e") for v in st["Profit"]],
        marker_line_width=0,
    )
    fig.update_layout(
        **PLOTLY_LAYOUT, barmode="group", height=320,
        xaxis=dict(**AXIS_STYLE, tickangle=-30),
        yaxis=dict(**AXIS_STYLE, title="₹"),
    )
    return fig


# ── City Table ────────────────────────────────────────────────────
@callback(
    Output("table-city", "children"),
    Input("filter-state", "value"),
    Input("filter-category", "value"),
    Input("filter-payment", "value"),
)
def update_city_table(states, categories, payments):
    df = filter_data(states, categories, payments)
    cities = city_breakdown(df).head(12)

    rows = []
    for _, row in cities.iterrows():
        margin_cls = "positive" if row["Margin_Pct"] >= 0 else "negative"
        rows.append(html.Tr([
            html.Td(row["City"]),
            html.Td(f"₹{row['Revenue']:,.0f}", className="mono"),
            html.Td(f"₹{row['Profit']:,.0f}", className=f"mono {margin_cls}"),
            html.Td(f"{row['Margin_Pct']:.1f}%", className=margin_cls),
        ]))

    return html.Table([
        html.Thead(html.Tr([
            html.Th("City"), html.Th("Revenue"), html.Th("Profit"), html.Th("Margin"),
        ])),
        html.Tbody(rows),
    ], className="data-table")


# ── Loss Diagnostic Charts ────────────────────────────────────────
@callback(
    Output("chart-loss-subcats", "figure"),
    Output("chart-profit-pool", "figure"),
    Input("filter-state", "value"),
    Input("filter-category", "value"),
    Input("filter-payment", "value"),
)
def update_loss_charts(states, categories, payments):
    df = filter_data(states, categories, payments)
    diag = loss_diagnostic(df)

    # Worst loss sub-categories
    worst = diag["worst_subcats"]
    fig_loss = go.Figure(go.Bar(
        x=worst["Loss"], y=worst["Sub-Category"],
        orientation="h", marker_color="#f43f5e", marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Loss: ₹%{x:,.0f}<extra></extra>",
    ))
    fig_loss.update_layout(
        **PLOTLY_LAYOUT, height=320,
        xaxis=dict(**AXIS_STYLE, title="Net Loss (₹)"),
        yaxis=dict(**AXIS_STYLE, autorange="reversed"),
    )

    # Profit pool donut
    fig_pool = go.Figure(go.Pie(
        labels=["Profitable Transactions", "Loss Transactions"],
        values=[abs(diag["profit_total"]), abs(diag["loss_total"])],
        hole=0.6,
        marker_colors=["#10b981", "#f43f5e"],
        textinfo="label+percent",
        textfont=dict(size=11, color="#f1f5f9"),
    ))
    fig_pool.update_layout(**PLOTLY_LAYOUT, height=320, showlegend=False)
    pool_net = diag["profit_total"] + diag["loss_total"]
    fig_pool.add_annotation(
        text=f"Net<br>₹{pool_net:,.0f}",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=13, color="#f1f5f9"),
    )

    return fig_loss, fig_pool


# ── Customer Chart ────────────────────────────────────────────────
@callback(
    Output("chart-customers", "figure"),
    Input("filter-state", "value"),
    Input("filter-category", "value"),
    Input("filter-payment", "value"),
)
def update_customers(states, categories, payments):
    df = filter_data(states, categories, payments)
    cust = customer_breakdown(df).head(15)

    fig = go.Figure()
    fig.add_bar(
        x=cust["CustomerName"], y=cust["Revenue"],
        name="Revenue", marker_color="#6366f1", marker_line_width=0, opacity=0.8,
    )
    fig.add_bar(
        x=cust["CustomerName"], y=cust["Profit"],
        name="Profit",
        marker_color=[("#10b981" if v >= 0 else "#f43f5e") for v in cust["Profit"]],
        marker_line_width=0,
    )
    fig.update_layout(
        **PLOTLY_LAYOUT, barmode="overlay", height=320,
        xaxis=dict(**AXIS_STYLE, tickangle=-30),
        yaxis=dict(**AXIS_STYLE, title="₹"),
    )
    return fig


# ── RFM Chart ────────────────────────────────────────────────────
@callback(
    Output("chart-rfm", "figure"),
    Input("filter-state", "value"),
    Input("filter-category", "value"),
    Input("filter-payment", "value"),
)
def update_rfm_chart(states, categories, payments):
    df = filter_data(states, categories, payments)
    rfm = rfm_segmentation(df)
    seg_counts = rfm["Segment"].value_counts().reset_index()
    seg_counts.columns = ["Segment", "Count"]

    color_map = {
        "Champions": "#10b981",
        "Loyal Customers": "#06b6d4",
        "Potential Loyalists": "#6366f1",
        "At Risk": "#f59e0b",
        "Can't Lose Them": "#f43f5e",
        "Lost": "#475569",
        "Needs Attention": "#8b5cf6",
    }
    colors = [color_map.get(s, "#6366f1") for s in seg_counts["Segment"]]

    fig = go.Figure(go.Pie(
        labels=seg_counts["Segment"],
        values=seg_counts["Count"],
        hole=0.55,
        marker_colors=colors,
        textinfo="label+value",
        textfont=dict(size=10, color="#f1f5f9"),
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=320, showlegend=False)
    return fig


# ── RFM Table ────────────────────────────────────────────────────
@callback(
    Output("table-rfm", "children"),
    Input("filter-state", "value"),
    Input("filter-category", "value"),
    Input("filter-payment", "value"),
)
def update_rfm_table(states, categories, payments):
    df = filter_data(states, categories, payments)
    rfm = rfm_segmentation(df).sort_values("RFM_Score", ascending=False).head(50)

    seg_cls = {
        "Champions": "rfm-Champions",
        "Loyal Customers": "rfm-Loyal_Customers",
        "Potential Loyalists": "rfm-Potential",
        "At Risk": "rfm-At_Risk",
        "Can't Lose Them": "rfm-Cant_Lose",
        "Lost": "rfm-Lost",
        "Needs Attention": "rfm-Needs_Attention",
    }

    rows = []
    for _, row in rfm.iterrows():
        cls = seg_cls.get(row["Segment"], "")
        rows.append(html.Tr([
            html.Td(row["CustomerName"]),
            html.Td(html.Span(row["Segment"], className=f"rfm-badge {cls}")),
            html.Td(str(row["Recency"]) + "d", className="mono"),
            html.Td(str(row["Frequency"]), className="mono"),
            html.Td(f"₹{row['Monetary']:,.0f}", className="mono"),
            html.Td(str(row["RFM_Score"]), className="mono"),
        ]))

    return html.Table([
        html.Thead(html.Tr([
            html.Th("Customer"), html.Th("Segment"),
            html.Th("Recency"), html.Th("Freq"), html.Th("Revenue"), html.Th("Score"),
        ])),
        html.Tbody(rows),
    ], className="data-table")


# ── AI Copilot Prescriptions ──────────────────────────────────────
@callback(
    Output("ai-prescriptions", "children"),
    Input("filter-state", "value"),
    Input("filter-category", "value"),
    Input("filter-payment", "value"),
)
def update_prescriptions(states, categories, payments):
    df = filter_data(states, categories, payments)
    k = top_kpis(df)
    pay = payment_breakdown(df)
    cities = city_breakdown(df)
    prescriptions = generate_prescriptions(k, None, cities, pay)

    cards = []
    for p in prescriptions:
        pri = p["priority"].lower()
        cards.append(html.Div([
            html.Div([
                html.Span(p["icon"], style={"fontSize": "1.1rem"}),
                html.Span(p["priority"], className=f"presc-priority {pri}"),
                html.Span(p["title"], className="presc-title"),
            ], className="presc-header"),
            html.Div("📊 Finding", className="presc-section"),
            html.P(p["finding"], className="presc-text"),
            html.Div("🎯 Recommended Action", className="presc-section"),
            html.P(p["action"], className="presc-text"),
            html.Div("💡 Expected Impact", className="presc-section"),
            html.P(p["impact"], className="presc-impact"),
        ], className=f"prescription-card {pri}"))

    return cards


# ══════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    debug = os.environ.get("DEBUG", "true").lower() == "true"
    print(f"\n🚀 E-Commerce AI Dashboard running at http://localhost:{port}\n")
    app.run(debug=debug, port=port, host="0.0.0.0")

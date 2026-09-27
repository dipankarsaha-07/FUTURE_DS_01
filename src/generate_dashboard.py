import os
import json
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSIGHTS_PATH = os.path.join(BASE_DIR, "data", "processed", "business_insights.json")
CLEANED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "superstore_cleaned.csv")
HTML_OUTPUT_PATH = os.path.join(BASE_DIR, "reports", "interactive_dashboard.html")

def generate_dashboard():
    print("Generating client-ready Interactive Executive Dashboard...")
    
    with open(INSIGHTS_PATH, "r") as f:
        insights = json.load(f)

    df = pd.read_csv(CLEANED_DATA_PATH)

    monthly = df.groupby(["Order Year", "Order Month"]).agg(
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum")
    ).reset_index()
    monthly["Label"] = monthly["Order Year"].astype(str) + "-" + monthly["Order Month"].astype(str).str.zfill(2)
    monthly_labels = monthly["Label"].tolist()
    monthly_revenue = [round(x, 2) for x in monthly["Revenue"].tolist()]
    monthly_profit = [round(x, 2) for x in monthly["Profit"].tolist()]

    subcats = insights["subcategory_performance"]
    subcat_names = [s["Sub-Category"] for s in subcats]
    subcat_revs = [round(s["Revenue"], 2) for s in subcats]
    subcat_profs = [round(s["Profit"], 2) for s in subcats]
    subcat_colors = ["#dc2626" if p < 0 else "#2563eb" for p in subcat_profs]

    cats = insights["category_performance"]
    cat_names = [c["Category"] for c in cats]
    cat_revs = [round(c["Revenue"], 2) for c in cats]
    cat_profs = [round(c["Profit"], 2) for c in cats]

    regs = insights["region_performance"]
    reg_names = [r["Region"] for r in regs]
    reg_revs = [round(r["Revenue"], 2) for r in regs]
    reg_profs = [round(r["Profit"], 2) for r in regs]
    reg_margins = [round(r["Profit_Margin_Pct"], 2) for r in regs]

    disc = insights["discount_sensitivity"]
    disc_brackets = [d["Discount Bracket"] for d in disc]
    disc_margins = [round(d["Profit_Margin_Pct"], 2) for d in disc]
    disc_loss_rates = [round(d["Loss_Rate_Pct"], 2) for d in disc]

    prod_summary = df.groupby(["Product Name", "Category", "Sub-Category"]).agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique"),
        AvgDiscount=("Discount", "mean")
    ).reset_index().sort_values(by="Sales", ascending=False).head(20)
    
    prod_table_rows = []
    for _, row in prod_summary.iterrows():
        margin = (row["Profit"] / row["Sales"] * 100) if row["Sales"] > 0 else 0
        badge_cls = "badge-success" if row["Profit"] > 2000 else ("badge-danger" if row["Profit"] < 0 else "badge-warning")
        status_text = "High Earner" if row["Profit"] > 2000 else ("Loss Leader" if row["Profit"] < 0 else "Moderate")
        prod_table_rows.append(f"""
            <tr>
                <td style="font-weight: 600; max-width: 320px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{row['Product Name']}">{row['Product Name']}</td>
                <td><span class="badge badge-neutral">{row['Category']}</span></td>
                <td>{row['Sub-Category']}</td>
                <td style="text-align: right; font-weight: 600;">${row['Sales']:,.2f}</td>
                <td style="text-align: right; font-weight: 600; color: {'#dc2626' if row['Profit'] < 0 else '#16a34a'};">${row['Profit']:,.2f}</td>
                <td style="text-align: right; font-weight: 600; color: {'#dc2626' if margin < 0 else '#16a34a'};">{margin:.1f}%</td>
                <td style="text-align: center;"><span class="badge {badge_cls}">{status_text}</span></td>
            </tr>
        """)
    prod_table_html = "\n".join(prod_table_rows)

    kpi = insights["kpis"]

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Superstore Executive Sales & Profitability Dashboard</title>
    <!-- Chart.js CDN -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-page: #f8fafc;
            --bg-card: #ffffff;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --primary: #2563eb;
            --primary-light: #eff6ff;
            --success: #16a34a;
            --success-light: #f0fdf4;
            --danger: #dc2626;
            --danger-light: #fef2f2;
            --warning: #d97706;
            --warning-light: #fffbeb;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.06);
            --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05);
            --radius-md: 12px;
            --radius-lg: 16px;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        body {{
            background-color: var(--bg-page);
            color: var(--text-main);
            line-height: 1.5;
            padding-bottom: 60px;
        }}

        /* Header Bar */
        .top-navbar {{
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: white;
            padding: 24px 36px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }}

        .brand-section h1 {{
            font-size: 24px;
            font-weight: 800;
            letter-spacing: -0.02em;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .brand-section p {{
            font-size: 13.5px;
            color: #94a3b8;
            margin-top: 4px;
        }}

        .badge-live {{
            background: rgba(37, 99, 235, 0.25);
            border: 1px solid rgba(59, 130, 246, 0.5);
            color: #60a5fa;
            font-size: 11px;
            padding: 4px 10px;
            border-radius: 9999px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .container {{
            max-width: 1440px;
            margin: 0 auto;
            padding: 28px 36px;
        }}

        /* KPI Cards Grid */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 28px;
        }}

        .kpi-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 20px 22px;
            box-shadow: var(--shadow-sm);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}

        .kpi-card:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }}

        .kpi-title {{
            font-size: 12.5px;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.03em;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .kpi-value {{
            font-size: 28px;
            font-weight: 800;
            margin-top: 8px;
            color: var(--text-main);
            letter-spacing: -0.03em;
        }}

        .kpi-subtitle {{
            font-size: 12px;
            margin-top: 6px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .kpi-pill {{
            padding: 2px 8px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 11px;
        }}

        .pill-positive {{ background: var(--success-light); color: var(--success); }}
        .pill-negative {{ background: var(--danger-light); color: var(--danger); }}
        .pill-neutral {{ background: var(--primary-light); color: var(--primary); }}

        /* Charts Layout */
        .chart-row {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 24px;
            margin-bottom: 28px;
        }}

        .chart-row-equal {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-bottom: 28px;
        }}

        .chart-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 24px;
            box-shadow: var(--shadow-sm);
        }}

        .chart-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 18px;
            border-bottom: 1px solid var(--border);
            padding-bottom: 12px;
        }}

        .chart-header h2 {{
            font-size: 16px;
            font-weight: 700;
            color: var(--text-main);
            letter-spacing: -0.01em;
        }}

        .chart-header p {{
            font-size: 12px;
            color: var(--text-muted);
        }}

        .chart-wrapper {{
            position: relative;
            height: 320px;
            width: 100%;
        }}

        /* Strategic Playbook Cards */
        .playbook-card {{
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid var(--border);
            border-left: 4px solid var(--primary);
            border-radius: var(--radius-md);
            padding: 22px;
            margin-bottom: 20px;
            box-shadow: var(--shadow-sm);
        }}

        .playbook-card h3 {{
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .playbook-card p {{
            font-size: 13.5px;
            color: #334155;
            line-height: 1.6;
        }}

        .strategic-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        /* Table Styling */
        .table-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 24px;
            box-shadow: var(--shadow-sm);
            margin-bottom: 28px;
        }}

        .table-responsive {{
            overflow-x: auto;
            margin-top: 14px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}

        th {{
            background-color: #f8fafc;
            color: var(--text-muted);
            font-weight: 700;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.04em;
            padding: 12px 14px;
            border-bottom: 1px solid var(--border);
            text-align: left;
        }}

        td {{
            padding: 12px 14px;
            border-bottom: 1px solid #f1f5f9;
            color: #1e293b;
        }}

        tr:hover td {{
            background-color: #f8fafc;
        }}

        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
        }}

        .badge-success {{ background: var(--success-light); color: var(--success); }}
        .badge-danger {{ background: var(--danger-light); color: var(--danger); }}
        .badge-warning {{ background: var(--warning-light); color: var(--warning); }}
        .badge-neutral {{ background: #f1f5f9; color: #475569; }}

        .table-search {{
            padding: 8px 14px;
            border: 1px solid var(--border);
            border-radius: 8px;
            font-size: 13px;
            width: 260px;
            outline: none;
            transition: border-color 0.2s ease;
        }}

        .table-search:focus {{
            border-color: var(--primary);
        }}

        @media (max-width: 1024px) {{
            .chart-row, .chart-row-equal {{
                grid-template-columns: 1fr;
            }}
            .container {{
                padding: 18px 20px;
            }}
        }}
    </style>
</head>
<body>

    <!-- Header Navbar -->
    <header class="top-navbar">
        <div class="brand-section">
            <h1>
                <span>📊</span> Superstore Business Intelligence Dashboard
            </h1>
            <p>Comprehensive Sales Performance, Regional Profitability, and Discount Sensitivity Analysis (2014 – 2017)</p>
        </div>
        <div>
            <span class="badge-live">Executive Analytics Suite</span>
        </div>
    </header>

    <main class="container">

        <!-- Top KPI Cards -->
        <section class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">
                    <span>Total Revenue</span>
                    <span>💵</span>
                </div>
                <div class="kpi-value">${kpi['total_revenue']:,.2f}</div>
                <div class="kpi-subtitle">
                    <span class="kpi-pill pill-positive">+20.4% YoY</span>
                    <span style="color: var(--text-muted);">Across 4 years</span>
                </div>
            </div>

            <div class="kpi-card">
                <div class="kpi-title">
                    <span>Net Operating Profit</span>
                    <span>📈</span>
                </div>
                <div class="kpi-value">${kpi['total_profit']:,.2f}</div>
                <div class="kpi-subtitle">
                    <span class="kpi-pill pill-neutral">{kpi['overall_profit_margin_pct']}% Margin</span>
                    <span style="color: var(--text-muted);">Blended Net Margin</span>
                </div>
            </div>

            <div class="kpi-card">
                <div class="kpi-title">
                    <span>Total Orders & AOV</span>
                    <span>📦</span>
                </div>
                <div class="kpi-value">{kpi['total_orders']:,}</div>
                <div class="kpi-subtitle">
                    <span class="kpi-pill pill-neutral">${kpi['average_order_value']:.2f} AOV</span>
                    <span style="color: var(--text-muted);">{kpi['total_customers']} Customers</span>
                </div>
            </div>

            <div class="kpi-card" style="border-left: 4px solid var(--danger);">
                <div class="kpi-title">
                    <span>Loss-Making Orders</span>
                    <span>⚠️</span>
                </div>
                <div class="kpi-value" style="color: var(--danger);">{kpi['unprofitable_orders_count']:,}</div>
                <div class="kpi-subtitle">
                    <span class="kpi-pill pill-negative">{kpi['pct_unprofitable_orders']}% of all orders</span>
                    <span style="color: var(--text-muted);">Discount-driven bleed</span>
                </div>
            </div>

            <div class="kpi-card">
                <div class="kpi-title">
                    <span>Top Profit Engine</span>
                    <span>🏆</span>
                </div>
                <div class="kpi-value" style="color: var(--success); font-size: 22px; margin-top: 14px;">Technology</div>
                <div class="kpi-subtitle">
                    <span class="kpi-pill pill-positive">17.4% Margin</span>
                    <span style="color: var(--text-muted);">$145.5K Profit</span>
                </div>
            </div>
        </section>

        <!-- Charts Row 1: Time Series & Category Breakdown -->
        <section class="chart-row">
            <div class="chart-card">
                <div class="chart-header">
                    <div>
                        <h2>Monthly Revenue & Net Profit Trajectory (2014 – 2017)</h2>
                        <p>Consistent growth with intense Q4 holiday seasonality spikes in November & December</p>
                    </div>
                </div>
                <div class="chart-wrapper">
                    <canvas id="monthlyTrendChart"></canvas>
                </div>
            </div>

            <div class="chart-card">
                <div class="chart-header">
                    <div>
                        <h2>Category Profit Contribution</h2>
                        <p>Furniture underperforms despite 32.3% revenue share</p>
                    </div>
                </div>
                <div class="chart-wrapper">
                    <canvas id="categoryDonutChart"></canvas>
                </div>
            </div>
        </section>

        <!-- Charts Row 2: Sub-Category Waterfall & Discount Sensitivity -->
        <section class="chart-row-equal">
            <div class="chart-card">
                <div class="chart-header">
                    <div>
                        <h2>Sub-Category Profitability Analysis</h2>
                        <p>Copiers & Phones drive gains; Tables (-$17.7K) & Bookcases (-$3.5K) lose money</p>
                    </div>
                </div>
                <div class="chart-wrapper">
                    <canvas id="subcatChart"></canvas>
                </div>
            </div>

            <div class="chart-card">
                <div class="chart-header">
                    <div>
                        <h2>Discount Sensitivity: Profit Margin Collapse</h2>
                        <p>Steep discounting past 20% causes catastrophic margin erosion</p>
                    </div>
                </div>
                <div class="chart-wrapper">
                    <canvas id="discountChart"></canvas>
                </div>
            </div>
        </section>

        <!-- Charts Row 3: Regional Analysis -->
        <section class="chart-card" style="margin-bottom: 28px;">
            <div class="chart-header">
                <div>
                    <h2>Regional Financial Matrix & Profit Margins</h2>
                    <p>West and East maintain high margins (~14%); Central is dragged down by heavy discounting (7.9% margin)</p>
                </div>
            </div>
            <div class="chart-wrapper" style="height: 280px;">
                <canvas id="regionChart"></canvas>
            </div>
        </section>

        <!-- Strategic Advisory & Executive Recommendations -->
        <section style="margin-bottom: 28px;">
            <h2 style="font-size: 20px; font-weight: 800; margin-bottom: 16px; color: var(--text-main);">
                🎯 Strategic Advisory & Growth Playbook (C-Suite Recommendations)
            </h2>
            <div class="strategic-grid">
                <div class="playbook-card" style="border-left-color: var(--danger);">
                    <h3>🚫 1. Cap Discounts at 20% Immediately</h3>
                    <p>
                        Data proves that transactions discounted above 20% incur an average <strong>-15.3% margin</strong> with a <strong>93.0% loss rate</strong>. Orders with >40% discount have a <strong>100% loss rate</strong> (-77.4% margin).
                        Eliminating discounts above 20% will instantly recover an estimated <strong>$38,000+ in annual profit</strong>.
                    </p>
                </div>

                <div class="playbook-card" style="border-left-color: var(--warning);">
                    <h3>🪑 2. Restructure the Tables & Furniture Line</h3>
                    <p>
                        While Furniture brings $742K in sales (32.3% of total), its blended margin is only <strong>2.49%</strong>, driven by severe losses in <strong>Tables (-$17,725)</strong> and <strong>Bookcases (-$3,473)</strong>.
                        We recommend renegotiating manufacturing costs, adding shipping surcharges for bulky items, or bundling tables exclusively with high-margin chairs.
                    </p>
                </div>

                <div class="playbook-card" style="border-left-color: var(--primary);">
                    <h3>📍 3. Regional Turnaround for Central & South</h3>
                    <p>
                        Central region margin lags at <strong>7.92%</strong> due to chronic loss-making states: <strong>Texas (-$25,729)</strong> and <strong>Illinois (-$12,608)</strong> where average discounting exceeds 37%. 
                        Establish strict geographic price floors and restrict discretionary sales rep discount authority in these states.
                    </p>
                </div>

                <div class="playbook-card" style="border-left-color: var(--success);">
                    <h3>🚀 4. Scale Star Products: Copiers, Phones & Paper</h3>
                    <p>
                        The <strong>Canon imageCLASS Copier</strong> alone generated <strong>$25,199 profit (40.9% margin)</strong>. Technology is our strongest growth engine ($145.5K profit). 
                        Reallocate marketing and ad spend toward enterprise copier leases, phone accessories, and recurring office paper subscriptions.
                    </p>
                </div>
            </div>
        </section>

        <!-- Top Products Data Table -->
        <section class="table-card">
            <div class="chart-header">
                <div>
                    <h2>Top 20 Revenue Products Performance Breakdown</h2>
                    <p>Detailed view of sales volume, net profit contribution, and margin viability</p>
                </div>
                <div>
                    <input type="text" id="tableSearch" class="table-search" placeholder="Search product name or category...">
                </div>
            </div>
            <div class="table-responsive">
                <table id="productTable">
                    <thead>
                        <tr>
                            <th>Product Name</th>
                            <th>Category</th>
                            <th>Sub-Category</th>
                            <th style="text-align: right;">Sales</th>
                            <th style="text-align: right;">Net Profit</th>
                            <th style="text-align: right;">Margin %</th>
                            <th style="text-align: center;">Profitability Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {prod_table_html}
                    </tbody>
                </table>
            </div>
        </section>

    </main>

    <script>
        // Search Filter for Product Table
        document.getElementById('tableSearch').addEventListener('keyup', function() {{
            let filter = this.value.toLowerCase();
            let rows = document.querySelectorAll('#productTable tbody tr');
            rows.forEach(row => {{
                let text = row.innerText.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            }});
        }});

        // 1. Monthly Trend Chart
        new Chart(document.getElementById('monthlyTrendChart'), {{
            type: 'line',
            data: {{
                labels: {json.dumps(monthly_labels)},
                datasets: [
                    {{
                        label: 'Revenue ($)',
                        data: {json.dumps(monthly_revenue)},
                        borderColor: '#2563eb',
                        backgroundColor: 'rgba(37, 99, 235, 0.08)',
                        fill: true,
                        tension: 0.3,
                        pointRadius: 2,
                        yAxisID: 'y'
                    }},
                    {{
                        label: 'Net Profit ($)',
                        data: {json.dumps(monthly_profit)},
                        borderColor: '#10b981',
                        borderDash: [4, 4],
                        pointRadius: 2,
                        tension: 0.3,
                        yAxisID: 'y1'
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                interaction: {{ mode: 'index', intersect: false }},
                scales: {{
                    y: {{
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {{ display: true, text: 'Revenue ($)' }},
                        grid: {{ color: '#f1f5f9' }}
                    }},
                    y1: {{
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {{ display: true, text: 'Profit ($)' }},
                        grid: {{ drawOnChartArea: false }}
                    }},
                    x: {{ grid: {{ display: false }} }}
                }}
            }}
        }});

        // 2. Category Donut Chart
        new Chart(document.getElementById('categoryDonutChart'), {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(cat_names)},
                datasets: [{{
                    data: {json.dumps(cat_profs)},
                    backgroundColor: ['#f59e0b', '#10b981', '#2563eb'],
                    hoverOffset: 6
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'bottom' }},
                    tooltip: {{
                        callbacks: {{
                            label: function(ctx) {{
                                return `${{ctx.label}}: $${{ctx.parsed.toLocaleString()}} Profit`;
                            }}
                        }}
                    }}
                }}
            }}
        }});

        // 3. Subcategory Profit Bar Chart
        new Chart(document.getElementById('subcatChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(subcat_names)},
                datasets: [{{
                    label: 'Net Profit ($)',
                    data: {json.dumps(subcat_profs)},
                    backgroundColor: {json.dumps(subcat_colors)},
                    borderRadius: 4
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{
                        title: {{ display: true, text: 'Net Profit ($)' }},
                        grid: {{ color: '#f1f5f9' }}
                    }},
                    y: {{ grid: {{ display: false }} }}
                }}
            }}
        }});

        // 4. Discount Sensitivity
        new Chart(document.getElementById('discountChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(disc_brackets)},
                datasets: [
                    {{
                        type: 'bar',
                        label: 'Profit Margin (%)',
                        data: {json.dumps(disc_margins)},
                        backgroundColor: ['#16a34a', '#2563eb', '#f59e0b', '#dc2626'],
                        borderRadius: 6,
                        yAxisID: 'y'
                    }},
                    {{
                        type: 'line',
                        label: '% Unprofitable Orders',
                        data: {json.dumps(disc_loss_rates)},
                        borderColor: '#0f172a',
                        pointBackgroundColor: '#0f172a',
                        pointRadius: 5,
                        yAxisID: 'y1'
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        type: 'linear',
                        position: 'left',
                        title: {{ display: true, text: 'Profit Margin (%)' }},
                        grid: {{ color: '#f1f5f9' }}
                    }},
                    y1: {{
                        type: 'linear',
                        position: 'right',
                        title: {{ display: true, text: '% Loss Rate' }},
                        grid: {{ drawOnChartArea: false }},
                        min: 0,
                        max: 100
                    }}
                }}
            }}
        }});

        // 5. Regional Performance Chart
        new Chart(document.getElementById('regionChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(reg_names)},
                datasets: [
                    {{
                        label: 'Revenue ($)',
                        data: {json.dumps(reg_revs)},
                        backgroundColor: '#3b82f6',
                        borderRadius: 4
                    }},
                    {{
                        label: 'Profit ($)',
                        data: {json.dumps(reg_profs)},
                        backgroundColor: '#10b981',
                        borderRadius: 4
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        title: {{ display: true, text: 'USD Amount ($)' }},
                        grid: {{ color: '#f1f5f9' }}
                    }},
                    x: {{ grid: {{ display: false }} }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

    with open(HTML_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Dashboard generated successfully at: {HTML_OUTPUT_PATH}")

if __name__ == "__main__":
    generate_dashboard()

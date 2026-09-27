# Superstore Commercial Sales & Profitability Analytics Suite

A professional data analytics project designed for real-world commercial advisory, business intelligence, and financial decision-making. Built using Python, Pandas, Matplotlib, Seaborn, and Chart.js on the [Kaggle Superstore Sales Dataset](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final).

---

## 📊 Project Overview

This project simulates a senior commercial data analyst advising C-suite executives, business owners, and regional sales directors. Rather than just creating descriptive charts, this project performs **root-cause financial diagnostics** to solve core business problems:
- **Top Revenue Generators vs Profit Drivers:** Unveiling top products like the Canon imageCLASS Copier ($25.2K profit) vs high-volume loss leaders like Cisco TelePresence (-$1.8K loss).
- **Temporal Patterns & Seasonality:** Capturing multi-year +14.9% CAGR growth and navigating intense Q4 holiday seasonality (November & December account for >30% of sales).
- **Category Profit Disparities:** Identifying why Furniture generates 32.3% of revenue ($742K) but only 2.49% profit margin due to heavy losses in Tables (-$17.7K) and Bookcases (-$3.5K).
- **Geographic Margin Erosion:** Pinpointing why the Central region underperforms (7.9% margin) driven by heavy discounting in Texas (-$25.7K loss) and Illinois (-$12.6K loss).
- **The Discount Margin Destruction Curve:** Empirically proving that transactions discounted above 20% experience an average **-15.3% margin** (93% loss rate), and discounts above 40% experience a **100% loss rate**.
- **Actionable 4-Pillar Growth Playbook:** Concrete strategic initiatives to recover +$38,000 to +$55,000 in lost annual net profit.

---

## 📁 Repository Structure

```
superstore_analytics/
├── data/
│   ├── raw/
│   │   └── Sample - Superstore.csv       # Raw 9,994 records
│   └── processed/
│       ├── superstore_cleaned.csv        # Cleaned dataset with 34 engineered metrics
│       ├── cleaning_summary.json         # Data quality & schema audit
│       └── business_insights.json        # Structured KPI aggregations
├── src/
│   ├── download_data.py                  # Automated dataset acquisition & validation
│   ├── data_cleaning.py                  # Data cleaning, null checks, feature engineering
│   ├── exploratory_analysis.py           # Quantitative analysis across dimensions
│   ├── generate_visualizations.py        # Publication-ready Matplotlib/Seaborn figures
│   └── generate_dashboard.py             # Generates interactive HTML dashboard
├── reports/
│   ├── figures/                          # High-resolution presentation figures (PNG)
│   │   ├── fig1_monthly_revenue_profit_trend.png
│   │   ├── fig2_subcategory_profitability.png
│   │   ├── fig3_regional_performance_matrix.png
│   │   ├── fig4_discount_impact_on_margins.png
│   │   └── fig5_customer_segments_and_shipping.png
│   ├── executive_summary.md              # Markdown executive report for C-suite
│   └── interactive_dashboard.html         # Client-ready interactive Chart.js dashboard
├── requirements.txt                      # Project dependencies
└── README.md                             # Documentation & user guide
```

---

## 🚀 How to Run the Pipeline

### 1. Environment Setup
The project uses standard Python with a virtual environment:
```bash
# Navigate to the project directory
cd superstore_analytics

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1
```

### 2. Execute Data Pipeline & Analysis
Run the end-to-end analytics workflow with a single sequence:

```bash
# Step 1: Download & verify raw dataset
python src/download_data.py

# Step 2: Clean, validate, and engineer features
python src/data_cleaning.py

# Step 3: Run comprehensive exploratory data analysis
python src/exploratory_analysis.py

# Step 4: Generate publication-grade presentation charts
python src/generate_visualizations.py

# Step 5: Synthesize client-ready interactive dashboard
python src/generate_dashboard.py
```

### 3. Open the Interactive Dashboard
Double-click or open `reports/interactive_dashboard.html` in any modern web browser (Chrome, Edge, Firefox, Safari). No web server required—it is fully self-contained!

---

## 📈 Key Metrics at a Glance

| Executive KPI | Figure | Status / Insight |
| :--- | :--- | :--- |
| **Gross Revenue** | **$2,297,200.86** | 4-Year Total (2014 – 2017) |
| **Net Operating Profit** | **$286,397.02** | 12.47% Blended Net Margin |
| **Total Orders** | **5,009 Orders** | 793 Unique Customers across 50 States |
| **Average Order Value (AOV)** | **$458.61** | Healthy cross-category basket size |
| **Unprofitable Orders** | **1,022 Orders (20.4%)** | Major opportunity for profit recovery |
| **Top Category** | **Technology** | $836.2K Sales, $145.5K Profit (17.4% Margin) |
| **Lowest Margin Category** | **Furniture** | $742.0K Sales, $18.5K Profit (2.49% Margin) |
| **Premier Region** | **West** | $725.5K Sales, $108.4K Profit (14.94% Margin) |
| **Problem Region** | **Central** | $501.2K Sales, $39.7K Profit (7.92% Margin) |

---

## 💡 Strategic Takeaways

1. **Cap Discounts at 20%:** Over $181,000 was lost on orders discounted past 40% (100% loss rate). Enforcing a 20% cap instantly recovers $38,000+ in annual profit.
2. **Restructure Furniture Line:** Tables (-$17.7K) and Bookcases (-$3.5K) require bulky freight surcharges, supplier price renegotiation, or bundling with high-margin chairs.
3. **Turn Around Central Region:** Re-align field sales compensation from gross volume to gross profit contribution in Texas (-$25.7K) and Illinois (-$12.6K).
4. **Scale High-Margin Winners:** Expand B2B copier leasing (Canon imageCLASS delivers 40.9% margin) and recurring office supply replenishment subscriptions.

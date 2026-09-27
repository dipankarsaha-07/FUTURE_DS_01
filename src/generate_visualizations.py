import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "Arial, DejaVu Sans, Helvetica"
plt.rcParams["axes.edgecolor"] = "#D0D5DD"
plt.rcParams["axes.linewidth"] = 0.8
plt.rcParams["grid.color"] = "#F2F4F7"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DATA = os.path.join(BASE_DIR, "data", "processed", "superstore_cleaned.csv")
FIGURES_DIR = os.path.join(BASE_DIR, "reports", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

df = pd.read_csv(PROCESSED_DATA)
df["Order Date"] = pd.to_datetime(df["Order Date"])

NAVY = "#1E293B"
BLUE = "#2563EB"
TEAL = "#0D9488"
GREEN = "#16A34A"
AMBER = "#D97706"
RED = "#DC2626"
GRAY = "#64748B"
LIGHT_BG = "#F8FAFC"

def chart_1_monthly_trends():
    """Figure 1: Monthly Revenue & Profit Trajectory (2014-2017)"""
    monthly = df.set_index("Order Date").resample("MS").agg(
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum")
    ).reset_index()

    fig, ax1 = plt.subplots(figsize=(14, 6), facecolor="white")
    
    ax1.plot(monthly["Order Date"], monthly["Revenue"] / 1000, color=BLUE, linewidth=2.5, label="Monthly Revenue ($K)", marker="o", markersize=4)
    ax1.fill_between(monthly["Order Date"], monthly["Revenue"] / 1000, alpha=0.12, color=BLUE)
    ax1.set_ylabel("Monthly Revenue ($ Thousands)", color=BLUE, fontsize=12, fontweight="bold")
    ax1.tick_params(axis="y", labelcolor=BLUE)
    ax1.set_ylim(bottom=0)

    ax2 = ax1.twinx()
    ax2.plot(monthly["Order Date"], monthly["Profit"] / 1000, color=TEAL, linewidth=2.5, linestyle="--", label="Monthly Profit ($K)", marker="s", markersize=4)
    ax2.axhline(0, color=RED, linestyle=":", alpha=0.6, linewidth=1)
    ax2.set_ylabel("Monthly Net Profit ($ Thousands)", color=TEAL, fontsize=12, fontweight="bold")
    ax2.tick_params(axis="y", labelcolor=TEAL)

    for year in [2014, 2015, 2016, 2017]:
        nov_dec_start = pd.Timestamp(f"{year}-11-01")
        nov_dec_end = pd.Timestamp(f"{year}-12-31")
        ax1.axvspan(nov_dec_start, nov_dec_end, color="#FEF3C7", alpha=0.4)

    plt.title("Monthly Revenue & Net Profit Trend (2014 – 2017)\nConsistent Multi-Year Growth with Notable Q4 Holiday Seasonality Surges", 
              fontsize=14, fontweight="bold", pad=15, loc="left", color=NAVY)
    
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=True, facecolor="white", edgecolor="#E2E8F0")

    fig.tight_layout()
    path = os.path.join(FIGURES_DIR, "fig1_monthly_revenue_profit_trend.png")
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"Saved: {path}")

def chart_2_subcategory_profitability():
    """Figure 2: Sub-Category Revenue vs Profit (Identifying Profit Drivers vs Drainers)"""
    subcat = df.groupby(["Category", "Sub-Category"]).agg(
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum")
    ).reset_index().sort_values(by="Profit", ascending=True)

    fig, ax = plt.subplots(figsize=(12, 8), facecolor="white")
    
    colors = [RED if p < 0 else (GREEN if p > 20000 else BLUE) for p in subcat["Profit"]]
    
    y_pos = np.arange(len(subcat))
    bars = ax.barh(y_pos, subcat["Profit"] / 1000, color=colors, height=0.65, edgecolor="none")
    
    ax.axvline(0, color=NAVY, linewidth=1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(subcat["Sub-Category"], fontsize=11, fontweight="medium")
    ax.set_xlabel("Net Profit ($ Thousands)", fontsize=12, fontweight="bold", color=NAVY)
    
    for bar in bars:
        width = bar.get_width()
        ha = "left" if width >= 0 else "right"
        offset = 1.2 if width >= 0 else -1.2
        val_str = f"${width:,.1f}K"
        ax.text(width + offset, bar.get_y() + bar.get_height()/2, val_str,
                va="center", ha=ha, fontsize=9.5, fontweight="bold",
                color=RED if width < 0 else NAVY)

    plt.title("Net Profit Contribution by Sub-Category\nCopiers & Phones Drive Growth; Tables (-$17.7K) & Bookcases (-$3.5K) Bleed Margin", 
              fontsize=13, fontweight="bold", pad=15, loc="left", color=NAVY)
    
    ax.set_xlim(min(subcat["Profit"]/1000) - 8, max(subcat["Profit"]/1000) + 12)
    fig.tight_layout()
    path = os.path.join(FIGURES_DIR, "fig2_subcategory_profitability.png")
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"Saved: {path}")

def chart_3_regional_and_state_analysis():
    """Figure 3: Regional Margin Comparison & Top/Bottom 5 States"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), facecolor="white")

    reg = df.groupby("Region").agg(
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum")
    ).reset_index()
    reg["Margin_Pct"] = (reg["Profit"] / reg["Revenue"]) * 100
    reg = reg.sort_values(by="Profit", ascending=False)

    x = np.arange(len(reg))
    width = 0.35
    ax1.bar(x - width/2, reg["Revenue"]/1000, width, label="Revenue ($K)", color=BLUE, alpha=0.85)
    ax1.bar(x + width/2, reg["Profit"]/1000, width, label="Profit ($K)", color=TEAL, alpha=0.85)
    ax1.set_xticks(x)
    ax1.set_xticklabels(reg["Region"], fontsize=11, fontweight="bold")
    ax1.set_ylabel("Amount ($ Thousands)", fontsize=11, fontweight="bold", color=NAVY)
    ax1.set_title("Regional Financial Comparison\nWest & East Outperform; Central Suffers Margin Compression", 
                  fontsize=12, fontweight="bold", loc="left", color=NAVY)
    ax1.legend(frameon=True)

    for i, row in reg.iterrows():
        pos = list(reg.index).index(i)
        ax1.text(pos + width/2, (row["Profit"]/1000) + 15, f"{row['Margin_Pct']:.1f}%\nMargin", 
                 ha="center", fontsize=9, fontweight="bold", color=TEAL)

    state_prof = df.groupby("State")["Profit"].sum().reset_index()
    top5 = state_prof.sort_values(by="Profit", ascending=False).head(5)
    bot5 = state_prof.sort_values(by="Profit", ascending=True).head(5)
    combined = pd.concat([bot5, top5]).sort_values(by="Profit")

    colors = [RED if p < 0 else GREEN for p in combined["Profit"]]
    ax2.barh(combined["State"], combined["Profit"]/1000, color=colors, height=0.6)
    ax2.axvline(0, color=NAVY, linewidth=1)
    ax2.set_xlabel("Net Profit ($ Thousands)", fontsize=11, fontweight="bold", color=NAVY)
    ax2.set_title("State Extremes: Top 5 Winners vs Bottom 5 Loss-Makers\nTexas (-$25.7K) & Ohio (-$17.0K) Face Severe Deficits", 
                  fontsize=12, fontweight="bold", loc="left", color=NAVY)

    for i, row in combined.iterrows():
        p_val = row["Profit"] / 1000
        ha = "left" if p_val >= 0 else "right"
        offset = 2 if p_val >= 0 else -2
        ax2.text(p_val + offset, row["State"], f"${p_val:,.1f}K", 
                 va="center", ha=ha, fontsize=9, fontweight="bold",
                 color=RED if p_val < 0 else GREEN)

    ax2.set_xlim(min(combined["Profit"]/1000) - 10, max(combined["Profit"]/1000) + 15)

    fig.tight_layout()
    path = os.path.join(FIGURES_DIR, "fig3_regional_performance_matrix.png")
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"Saved: {path}")

def chart_4_discount_margin_erosion():
    """Figure 4: Discount Sensitivity & Profit Margin Collapse"""
    disc_summary = df.groupby("Discount Bracket").agg(
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Row ID", "count"),
        Unprofitable=("Is Profitable", lambda x: int((~x).sum()))
    ).loc[["0% (None)", "1% - 20% (Low)", "21% - 40% (Moderate)", "> 40% (Steep)"]].reset_index()

    disc_summary["Margin_Pct"] = (disc_summary["Profit"] / disc_summary["Revenue"]) * 100
    disc_summary["Unprofitable_Rate_Pct"] = (disc_summary["Unprofitable"] / disc_summary["Orders"]) * 100

    fig, ax1 = plt.subplots(figsize=(11, 6), facecolor="white")

    bar_colors = [GREEN, BLUE, AMBER, RED]
    bars = ax1.bar(disc_summary["Discount Bracket"], disc_summary["Margin_Pct"], color=bar_colors, width=0.55, edgecolor="none")
    ax1.axhline(0, color=NAVY, linestyle="-", linewidth=1.2)
    ax1.set_ylabel("Operating Profit Margin (%)", fontsize=12, fontweight="bold", color=NAVY)
    ax1.set_ylim(-90, 45)

    for bar, pct in zip(bars, disc_summary["Margin_Pct"]):
        y_pos = bar.get_height() + (2.5 if bar.get_height() >= 0 else -6.5)
        ax1.text(bar.get_x() + bar.get_width()/2, y_pos, f"{pct:.1f}%", 
                 ha="center", fontsize=11, fontweight="bold",
                 color=RED if pct < 0 else NAVY)

    ax2 = ax1.twinx()
    ax2.plot(disc_summary["Discount Bracket"], disc_summary["Unprofitable_Rate_Pct"], color=NAVY, marker="o", linewidth=2.5, markersize=8, label="% Unprofitable Transactions")
    ax2.set_ylabel("% of Transactions Losing Money", fontsize=12, fontweight="bold", color=NAVY)
    ax2.set_ylim(0, 115)
    
    for x, y in zip(disc_summary["Discount Bracket"], disc_summary["Unprofitable_Rate_Pct"]):
        ax2.text(x, y + 4, f"{y:.1f}% Fail", ha="center", fontsize=9.5, fontweight="bold", color=NAVY)

    plt.title("Discount Sensitivity: The Profit Margin Destruction Curve\nDiscounts >20% Result in 93%+ Loss Rates; Discounts >40% Have a 100% Failure Rate", 
              fontsize=13, fontweight="bold", pad=15, loc="left", color=NAVY)

    fig.tight_layout()
    path = os.path.join(FIGURES_DIR, "fig4_discount_impact_on_margins.png")
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"Saved: {path}")

def chart_5_segment_and_shipping():
    """Figure 5: Customer Segment Performance & Shipping Efficiency"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), facecolor="white")

    seg = df.groupby("Segment").agg(
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum")
    ).reset_index()
    seg["Margin_Pct"] = (seg["Profit"] / seg["Revenue"]) * 100

    colors = [BLUE, TEAL, AMBER]
    ax1.pie(seg["Revenue"], labels=seg["Segment"], autopct="%1.1f%%", startangle=140, 
            colors=colors, wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2),
            textprops={"fontsize": 11, "fontweight": "bold"})
    ax1.set_title("Revenue Share by Customer Segment\nConsumer Leads with 50.6% ($1.16M)", fontsize=12, fontweight="bold", loc="left", color=NAVY)

    ship = df.groupby("Ship Mode").agg(
        Avg_Days=("Days to Ship", "mean"),
        Margin_Pct=("Profit Margin", lambda x: np.mean(x) * 100),
        Volume=("Row ID", "count")
    ).reset_index().sort_values(by="Avg_Days", ascending=True)

    ax2.scatter(ship["Avg_Days"], ship["Margin_Pct"], s=ship["Volume"] / 3, color=BLUE, alpha=0.7, edgecolors=NAVY, linewidth=1.5)
    for i, row in ship.iterrows():
        ax2.annotate(f"{row['Ship Mode']}\n({row['Avg_Days']:.1f} days, {row['Margin_Pct']:.1f}%)", 
                     (row["Avg_Days"], row["Margin_Pct"]),
                     textcoords="offset points", xytext=(0, 14), ha="center", fontsize=9.5, fontweight="bold")

    ax2.set_xlabel("Average Days to Ship (Fulfillment Speed)", fontsize=11, fontweight="bold", color=NAVY)
    ax2.set_ylabel("Average Profit Margin (%)", fontsize=11, fontweight="bold", color=NAVY)
    ax2.set_title("Fulfillment Speed vs Profitability\nSame Day Ships in ~0 days; Standard Class Dominates Volume", fontsize=12, fontweight="bold", loc="left", color=NAVY)
    ax2.set_ylim(8, 16)
    ax2.set_xlim(-0.5, 6)

    fig.tight_layout()
    path = os.path.join(FIGURES_DIR, "fig5_customer_segments_and_shipping.png")
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"Saved: {path}")

def generate_all_charts():
    print("Generating executive-ready visualizations...")
    chart_1_monthly_trends()
    chart_2_subcategory_profitability()
    chart_3_regional_and_state_analysis()
    chart_4_discount_margin_erosion()
    chart_5_segment_and_shipping()
    print("All charts successfully generated in reports/figures/")

if __name__ == "__main__":
    generate_all_charts()
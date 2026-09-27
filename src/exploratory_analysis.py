import os
import json
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "superstore_cleaned.csv")
OUTPUT_METRICS_PATH = os.path.join(BASE_DIR, "data", "processed", "business_insights.json")

def run_analysis():
    print("=" * 70)
    print("EXECUTING IN-DEPTH BUSINESS SALES & PROFITABILITY ANALYSIS")
    print("=" * 70)

    df = pd.read_csv(PROCESSED_DATA_PATH)
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Ship Date"] = pd.to_datetime(df["Ship Date"])

    insights = {}

    total_sales = float(df["Sales"].sum())
    total_profit = float(df["Profit"].sum())
    profit_margin = (total_profit / total_sales) * 100
    total_orders = int(df["Order ID"].nunique())
    total_customers = int(df["Customer ID"].nunique())
    total_units = int(df["Quantity"].sum())
    avg_order_value = total_sales / total_orders
    avg_profit_per_order = total_profit / total_orders
    unprofitable_orders_count = int((df.groupby("Order ID")["Profit"].sum() < 0).sum())
    pct_unprofitable_orders = (unprofitable_orders_count / total_orders) * 100

    insights["kpis"] = {
        "total_revenue": round(total_sales, 2),
        "total_profit": round(total_profit, 2),
        "overall_profit_margin_pct": round(profit_margin, 2),
        "total_orders": total_orders,
        "total_customers": total_customers,
        "total_units_sold": total_units,
        "average_order_value": round(avg_order_value, 2),
        "average_profit_per_order": round(avg_profit_per_order, 2),
        "unprofitable_orders_count": unprofitable_orders_count,
        "pct_unprofitable_orders": round(pct_unprofitable_orders, 2)
    }

    yearly = df.groupby("Order Year").agg(
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique"),
        Quantity=("Quantity", "sum")
    ).reset_index()
    yearly["Profit_Margin_Pct"] = (yearly["Profit"] / yearly["Revenue"]) * 100
    yearly["YoY_Revenue_Growth_Pct"] = yearly["Revenue"].pct_change() * 100
    yearly["YoY_Profit_Growth_Pct"] = yearly["Profit"].pct_change() * 100

    insights["yearly_performance"] = yearly.round(2).to_dict(orient="records")

    monthly = df.groupby(["Order Year", "Order Month"]).agg(
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique")
    ).reset_index()
    monthly["Year_Month"] = monthly["Order Year"].astype(str) + "-" + monthly["Order Month"].astype(str).str.zfill(2)
    insights["monthly_trends"] = monthly.round(2).to_dict(orient="records")

    seasonality = df.groupby("Order Month Name").agg(
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique")
    ).loc[
        ['January', 'February', 'March', 'April', 'May', 'June', 
         'July', 'August', 'September', 'October', 'November', 'December']
    ].reset_index()
    seasonality["Profit_Margin_Pct"] = (seasonality["Profit"] / seasonality["Revenue"]) * 100
    insights["seasonality"] = seasonality.round(2).to_dict(orient="records")

    cat_summary = df.groupby("Category").agg(
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        Avg_Discount=("Discount", "mean"),
        Orders=("Order ID", "nunique")
    ).reset_index()
    cat_summary["Profit_Margin_Pct"] = (cat_summary["Profit"] / cat_summary["Revenue"]) * 100
    cat_summary["Revenue_Share_Pct"] = (cat_summary["Revenue"] / total_sales) * 100
    cat_summary["Profit_Share_Pct"] = (cat_summary["Profit"] / total_profit) * 100
    insights["category_performance"] = cat_summary.round(2).to_dict(orient="records")

    subcat_summary = df.groupby(["Category", "Sub-Category"]).agg(
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        Avg_Discount=("Discount", "mean")
    ).reset_index()
    subcat_summary["Profit_Margin_Pct"] = (subcat_summary["Profit"] / subcat_summary["Revenue"]) * 100
    subcat_summary = subcat_summary.sort_values(by="Revenue", ascending=False)
    insights["subcategory_performance"] = subcat_summary.round(2).to_dict(orient="records")

    region_summary = df.groupby("Region").agg(
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique"),
        Avg_Discount=("Discount", "mean")
    ).reset_index()
    region_summary["Profit_Margin_Pct"] = (region_summary["Profit"] / region_summary["Revenue"]) * 100
    region_summary["Revenue_Share_Pct"] = (region_summary["Revenue"] / total_sales) * 100
    region_summary["Profit_Share_Pct"] = (region_summary["Profit"] / total_profit) * 100
    region_summary = region_summary.sort_values(by="Profit", ascending=False)
    insights["region_performance"] = region_summary.round(2).to_dict(orient="records")

    state_summary = df.groupby("State").agg(
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique"),
        Avg_Discount=("Discount", "mean")
    ).reset_index()
    state_summary["Profit_Margin_Pct"] = (state_summary["Profit"] / state_summary["Revenue"]) * 100
    top_states_profit = state_summary.sort_values(by="Profit", ascending=False).head(10)
    bottom_states_profit = state_summary.sort_values(by="Profit", ascending=True).head(10)
    insights["top_10_states_profit"] = top_states_profit.round(2).to_dict(orient="records")
    insights["bottom_10_states_profit"] = bottom_states_profit.round(2).to_dict(orient="records")

    prod_summary = df.groupby(["Product ID", "Product Name", "Category", "Sub-Category"]).agg(
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Units_Sold=("Quantity", "sum"),
        Avg_Discount=("Discount", "mean")
    ).reset_index()
    prod_summary["Profit_Margin_Pct"] = (prod_summary["Profit"] / prod_summary["Revenue"]) * 100
    
    top_10_revenue_products = prod_summary.sort_values(by="Revenue", ascending=False).head(10)
    top_10_profit_products = prod_summary.sort_values(by="Profit", ascending=False).head(10)
    bottom_10_profit_products = prod_summary.sort_values(by="Profit", ascending=True).head(10)

    insights["top_10_revenue_products"] = top_10_revenue_products.round(2).to_dict(orient="records")
    insights["top_10_profit_products"] = top_10_profit_products.round(2).to_dict(orient="records")
    insights["bottom_10_profit_products"] = bottom_10_profit_products.round(2).to_dict(orient="records")

    segment_summary = df.groupby("Segment").agg(
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Customers=("Customer ID", "nunique"),
        Orders=("Order ID", "nunique"),
        Avg_Discount=("Discount", "mean")
    ).reset_index()
    segment_summary["Profit_Margin_Pct"] = (segment_summary["Profit"] / segment_summary["Revenue"]) * 100
    segment_summary["AOV"] = segment_summary["Revenue"] / segment_summary["Orders"]
    insights["segment_performance"] = segment_summary.round(2).to_dict(orient="records")

    discount_impact = df.groupby("Discount Bracket").agg(
        Transactions=("Row ID", "count"),
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Avg_Profit_Per_Tx=("Profit", "mean"),
        Loss_Transactions=("Is Profitable", lambda x: int((~x).sum()))
    ).reset_index()
    discount_impact["Profit_Margin_Pct"] = (discount_impact["Profit"] / discount_impact["Revenue"]) * 100
    discount_impact["Loss_Rate_Pct"] = (discount_impact["Loss_Transactions"] / discount_impact["Transactions"]) * 100
    insights["discount_sensitivity"] = discount_impact.round(2).to_dict(orient="records")

    ship_summary = df.groupby("Ship Mode").agg(
        Orders=("Order ID", "nunique"),
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Avg_Ship_Days=("Days to Ship", "mean")
    ).reset_index()
    ship_summary["Profit_Margin_Pct"] = (ship_summary["Profit"] / ship_summary["Revenue"]) * 100
    insights["shipping_efficiency"] = ship_summary.round(2).to_dict(orient="records")

    with open(OUTPUT_METRICS_PATH, "w") as f:
        json.dump(insights, f, indent=4)

    print(f"Analysis successfully completed and saved to {OUTPUT_METRICS_PATH}")
    
    print("\n--- KEY BUSINESS HIGHLIGHTS ---")
    print(f"Total Revenue: ${total_sales:,.2f}")
    print(f"Total Net Profit: ${total_profit:,.2f} ({profit_margin:.2f}% Net Margin)")
    print(f"Total Orders: {total_orders:,} | Average Order Value: ${avg_order_value:.2f}")
    print(f"Unprofitable Orders: {unprofitable_orders_count:,} ({pct_unprofitable_orders:.1f}% of all orders!)")
    
    print("\n--- CATEGORY BREAKDOWN ---")
    for cat in insights["category_performance"]:
        print(f"• {cat['Category']}: Revenue ${cat['Revenue']:,.2f} ({cat['Revenue_Share_Pct']}%), Profit ${cat['Profit']:,.2f} ({cat['Profit_Margin_Pct']}% margin)")
        
    print("\n--- REGIONAL BREAKDOWN ---")
    for reg in insights["region_performance"]:
        print(f"• {reg['Region']}: Revenue ${reg['Revenue']:,.2f}, Profit ${reg['Profit']:,.2f} ({reg['Profit_Margin_Pct']}% margin)")

    print("\n--- DISCOUNT EROSION ---")
    for d in insights["discount_sensitivity"]:
        print(f"• Discount {d['Discount Bracket']}: Margin {d['Profit_Margin_Pct']}%, Loss Rate {d['Loss_Rate_Pct']}%")

    return insights

if __name__ == "__main__":
    run_analysis()

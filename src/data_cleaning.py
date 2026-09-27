"""
Superstore Sales Analytics - Data Cleaning & Feature Engineering Module
Author: Data Analytics Specialist
Description: Cleans raw Superstore data, validates integrity, standardizes formats,
             and engineers key business metrics for downstream analysis.
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "Sample - Superstore.csv")
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "superstore_cleaned.csv")
METRICS_SUMMARY_PATH = os.path.join(BASE_DIR, "data", "processed", "cleaning_summary.json")

def clean_data():
    print("=" * 60)
    print("STEP 1: LOADING RAW DATA")
    print("=" * 60)
    try:
        df = pd.read_csv(RAW_DATA_PATH, encoding="windows-1252")
    except Exception:
        df = pd.read_csv(RAW_DATA_PATH, encoding="latin-1")
    
    initial_rows, initial_cols = df.shape
    print(f"Raw dataset loaded: {initial_rows:,} rows, {initial_cols} columns")

    print("\n" + "=" * 60)
    print("STEP 2: DATA STANDARDIZATION & CLEANING")
    print("=" * 60)
    
    # Standardize column names (strip whitespace)
    df.columns = df.columns.str.strip()

    # Clean text columns (strip leading/trailing whitespace)
    text_cols = df.select_dtypes(include=["object"]).columns
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()

    # Parse Dates
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="mixed")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="mixed")

    # Validate date logic (Ship Date must be on or after Order Date)
    invalid_dates = df[df["Ship Date"] < df["Order Date"]]
    if len(invalid_dates) > 0:
        print(f"WARNING: Found {len(invalid_dates)} records where Ship Date < Order Date. Correcting...")
        df = df[df["Ship Date"] >= df["Order Date"]]

    # Postal code formatting: pad with leading zero for US zipcodes
    df["Postal Code"] = df["Postal Code"].astype(str).str.replace(".0", "", regex=False).str.zfill(5)

    # Check for duplicates
    dup_count = df.duplicated(subset=["Order ID", "Product ID"]).sum()
    print(f"Duplicate (Order ID + Product ID) records: {dup_count}")

    print("\n" + "=" * 60)
    print("STEP 3: FEATURE ENGINEERING FOR BUSINESS ANALYTICS")
    print("=" * 60)
    
    # Temporal features
    df["Order Year"] = df["Order Date"].dt.year
    df["Order Quarter"] = df["Order Date"].dt.to_period("Q").astype(str)
    df["Order Month"] = df["Order Date"].dt.month
    df["Order Month Name"] = df["Order Date"].dt.strftime("%B")
    df["Order Year-Month"] = df["Order Date"].dt.strftime("%Y-%m")
    df["Order Day of Week"] = df["Order Date"].dt.strftime("%A")

    # Shipping efficiency
    df["Days to Ship"] = (df["Ship Date"] - df["Order Date"]).dt.days

    # Financial & profitability metrics
    df["Profit Margin"] = np.where(df["Sales"] > 0, df["Profit"] / df["Sales"], 0.0)
    df["Cost"] = df["Sales"] - df["Profit"]
    df["Unit Price"] = df["Sales"] / df["Quantity"]
    df["Unit Profit"] = df["Profit"] / df["Quantity"]
    df["Is Profitable"] = df["Profit"] > 0

    # Discount segmentation
    def categorize_discount(disc):
        if disc == 0:
            return "0% (None)"
        elif disc <= 0.20:
            return "1% - 20% (Low)"
        elif disc <= 0.40:
            return "21% - 40% (Moderate)"
        else:
            return "> 40% (Steep)"

    df["Discount Bracket"] = df["Discount"].apply(categorize_discount)

    # Save processed dataset
    os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
    df.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"Cleaned dataset saved to: {PROCESSED_DATA_PATH}")
    print(f"Final dataset shape: {df.shape[0]:,} rows, {df.shape[1]} columns")

    # High-level data quality summary
    summary = {
        "initial_rows": initial_rows,
        "final_rows": df.shape[0],
        "columns": list(df.columns),
        "date_range_start": str(df["Order Date"].min().date()),
        "date_range_end": str(df["Order Date"].max().date()),
        "total_revenue": round(float(df["Sales"].sum()), 2),
        "total_profit": round(float(df["Profit"].sum()), 2),
        "overall_profit_margin_pct": round(float((df["Profit"].sum() / df["Sales"].sum()) * 100), 2),
        "total_orders": int(df["Order ID"].nunique()),
        "total_customers": int(df["Customer ID"].nunique()),
        "total_products": int(df["Product ID"].nunique()),
    }

    import json
    with open(METRICS_SUMMARY_PATH, "w") as f:
        json.dump(summary, f, indent=4)

    print("\nData Cleaning & Preparation Completed Successfully.")
    print(f"Summary metrics: Total Revenue: ${summary['total_revenue']:,.2f}, Total Profit: ${summary['total_profit']:,.2f} ({summary['overall_profit_margin_pct']}%)")
    return df

if __name__ == "__main__":
    clean_data()

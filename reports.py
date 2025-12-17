import matplotlib.pyplot as plt
import pandas as pd
from export_data import fetch_sales_dataframe
from datetime import datetime


def revenue_time_series():
    df = fetch_sales_dataframe()
    if df.empty:
        return
    df["sale_date"] = pd.to_datetime(df["sale_date"])
    daily = df.groupby("sale_date")["amount"].sum().reset_index()
    plt.figure()
    plt.plot(daily["sale_date"], daily["amount"])
    plt.title("Revenue over time")
    plt.tight_layout()
    fname = f"report_revenue_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(fname)
    plt.close()
    print(f"[report] Saved -> {fname}")


def top_products_bar():
    df = fetch_sales_dataframe()
    if df.empty:
        return
    top = df.groupby("product")["amount"].sum().sort_values(ascending=False).head(10)
    plt.figure()
    top.plot(kind="bar")
    plt.title("Top Products by Revenue")
    plt.tight_layout()
    fname = f"report_top_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(fname)
    plt.close()
    print(f"[report] Saved -> {fname}")
    
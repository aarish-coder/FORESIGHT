import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

PROCESSED_DIR = Path("data/processed")
OUTPUT_DIR = Path("outputs/figures")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def find_sales_file():
    files = list(PROCESSED_DIR.glob("*sales*_clean.csv"))

    if not files:
        raise FileNotFoundError(
            "Sales cleaned CSV not found in data/processed/"
        )

    return files[0]


def main():

    print("=" * 60)
    print("FORESIGHT - DEMAND PATTERN ANALYSIS")
    print("=" * 60)

    # Load cleaned sales data
    sales_file = find_sales_file()
    df = pd.read_csv(sales_file)

    print(f"\nLoaded: {sales_file}")
    print(f"Rows: {len(df):,}")

    # Convert date
    if "date" in df.columns:
        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

    # --------------------------------------------------------
    # 1. Basic statistics
    # --------------------------------------------------------

    print("\n--- BASIC STATISTICS ---")

    if "units_sold" in df.columns:
        print("\nUnits sold:")
        print(df["units_sold"].describe())

    if "revenue" in df.columns:
        print("\nRevenue:")
        print(df["revenue"].describe())

    # --------------------------------------------------------
    # 2. Top selling SKUs
    # --------------------------------------------------------

    if "sku_id" in df.columns and "units_sold" in df.columns:

        top_skus = (
            df.groupby("sku_id")["units_sold"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        print("\n--- TOP 10 SKUs BY UNITS SOLD ---")
        print(top_skus)

        plt.figure(figsize=(10, 6))
        top_skus.sort_values().plot(kind="barh")
        plt.title("Top 10 SKUs by Units Sold")
        plt.xlabel("Units Sold")
        plt.ylabel("SKU")
        plt.tight_layout()

        plt.savefig(
            OUTPUT_DIR / "top_10_skus.png"
        )

        plt.close()

    # --------------------------------------------------------
    # 3. Daily demand
    # --------------------------------------------------------

    if "date" in df.columns and "units_sold" in df.columns:

        daily_demand = (
            df.groupby("date")["units_sold"]
            .sum()
        )

        plt.figure(figsize=(12, 6))
        daily_demand.plot()

        plt.title("Daily Demand Trend")
        plt.xlabel("Date")
        plt.ylabel("Units Sold")
        plt.tight_layout()

        plt.savefig(
            OUTPUT_DIR / "daily_demand_trend.png"
        )

        plt.close()

    # --------------------------------------------------------
    # 4. Weekly demand
    # --------------------------------------------------------

    if "date" in df.columns and "units_sold" in df.columns:

        weekly_demand = (
            df.set_index("date")
            .resample("W")["units_sold"]
            .sum()
        )

        plt.figure(figsize=(12, 6))
        weekly_demand.plot()

        plt.title("Weekly Demand Trend")
        plt.xlabel("Week")
        plt.ylabel("Units Sold")
        plt.tight_layout()

        plt.savefig(
            OUTPUT_DIR / "weekly_demand_trend.png"
        )

        plt.close()

    # --------------------------------------------------------
    # 5. Promotion impact
    # --------------------------------------------------------

    if (
        "promo_flag" in df.columns
        and "units_sold" in df.columns
    ):

        promo_demand = (
            df.groupby("promo_flag")["units_sold"]
            .mean()
        )

        print("\n--- PROMOTION IMPACT ---")
        print(promo_demand)

        plt.figure(figsize=(7, 5))
        promo_demand.plot(kind="bar")

        plt.title("Average Demand: Promotion vs Non-Promotion")
        plt.xlabel("Promotion Flag")
        plt.ylabel("Average Units Sold")
        plt.xticks(rotation=0)

        plt.tight_layout()

        plt.savefig(
            OUTPUT_DIR / "promotion_impact.png"
        )

        plt.close()

    # --------------------------------------------------------
    # 6. Zero-demand / dead-stock candidates
    # --------------------------------------------------------

    if "sku_id" in df.columns and "units_sold" in df.columns:

        sku_summary = (
            df.groupby("sku_id")
            .agg(
                total_units=("units_sold", "sum"),
                average_units=("units_sold", "mean"),
                days=("units_sold", "count")
            )
        )

        dead_stock = sku_summary[
            sku_summary["total_units"] == 0
        ]

        print("\n--- ZERO-DEMAND SKUs ---")
        print(dead_stock)

        dead_stock.to_csv(
            PROCESSED_DIR / "dead_stock_candidates.csv"
        )

    # --------------------------------------------------------
    # 7. Save summary
    # --------------------------------------------------------

    summary = []

    summary.append(
        f"Total rows: {len(df):,}"
    )

    if "sku_id" in df.columns:
        summary.append(
            f"Unique SKUs: {df['sku_id'].nunique():,}"
        )

    if "date" in df.columns:
        summary.append(
            f"Date range: {df['date'].min()} to {df['date'].max()}"
        )

    if "units_sold" in df.columns:
        summary.append(
            f"Total units sold: {df['units_sold'].sum():,.0f}"
        )

    with open(
        "reports/demand_analysis.txt",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "\n".join(summary)
        )

    print("\n" + "=" * 60)
    print("DEMAND ANALYSIS COMPLETED")
    print("=" * 60)

    print("\nGenerated:")
    print("  outputs/figures/")
    print("  reports/demand_analysis.txt")


if __name__ == "__main__":
    main()
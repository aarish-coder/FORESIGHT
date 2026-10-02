import pandas as pd
import numpy as np
from pathlib import Path

PROCESSED_DIR = Path("data/processed")
FORECAST_DIR = Path("outputs/forecasts")
RISK_DIR = Path("outputs/risk")

RISK_DIR.mkdir(parents=True, exist_ok=True)


def main():

    print("=" * 60)
    print("FORESIGHT - INVENTORY RISK ANALYSIS")
    print("=" * 60)

    # Load cleaned inventory data
    files = list(PROCESSED_DIR.glob("*_clean.csv"))

    if not files:
        raise FileNotFoundError(
            "No cleaned dataset found."
        )

    df = pd.read_csv(files[0])

    # ---------------------------------------------------------
    # Basic inventory calculations
    # ---------------------------------------------------------

    df["inventory_value"] = (
        df["qty_on_hand"] *
        df["stock_unit_cost_price"]
    )

    df["potential_sales_value"] = (
        df["qty_on_hand"] *
        df["stock_unit_selling_price"]
    )

    # ---------------------------------------------------------
    # Inventory risk indicators
    # ---------------------------------------------------------

    # Low-stock threshold
    low_stock_threshold = (
        df.groupby("product_category")["qty_on_hand"]
        .transform("median")
    )

    df["stockout_risk"] = np.where(
        df["qty_on_hand"] <= low_stock_threshold,
        "High",
        "Low"
    )

    # High inventory threshold
    high_stock_threshold = (
        df.groupby("product_category")["qty_on_hand"]
        .transform(
            lambda x: x.quantile(0.75)
        )
    )

    df["overstock_risk"] = np.where(
        df["qty_on_hand"] >= high_stock_threshold,
        "High",
        "Low"
    )

    # ---------------------------------------------------------
    # Decision quadrant
    # ---------------------------------------------------------

    conditions = [
        (
            (df["stockout_risk"] == "High") &
            (df["overstock_risk"] == "Low")
        ),
        (
            (df["stockout_risk"] == "Low") &
            (df["overstock_risk"] == "High")
        ),
        (
            (df["stockout_risk"] == "High") &
            (df["overstock_risk"] == "High")
        ),
        (
            (df["stockout_risk"] == "Low") &
            (df["overstock_risk"] == "Low")
        )
    ]

    decisions = [
        "Reorder Now",
        "Markdown / Clear",
        "Watch / Volatile",
        "Healthy"
    ]

    df["decision"] = np.select(
        conditions,
        decisions,
        default="Review"
    )

    # ---------------------------------------------------------
    # Risk score
    # ---------------------------------------------------------

    df["risk_score"] = (
        (df["stockout_risk"] == "High").astype(int) +
        (df["overstock_risk"] == "High").astype(int)
    )

    # ---------------------------------------------------------
    # Rupee value at stake
    # ---------------------------------------------------------

    df["rupee_value_at_stake"] = (
        df["inventory_value"]
    )

    # ---------------------------------------------------------
    # Save results
    # ---------------------------------------------------------

    output_columns = [
        "product_no",
        "product_description",
        "product_division",
        "product_category",
        "product_subcategory",
        "store",
        "qty_on_hand",
        "inventory_value",
        "stockout_risk",
        "overstock_risk",
        "risk_score",
        "decision",
        "rupee_value_at_stake"
    ]

    output = df[output_columns]

    output_file = (
        RISK_DIR /
        "risk_results.csv"
    )

    output.to_csv(
        output_file,
        index=False
    )

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    print("\nRisk Summary:")
    print(
        output["decision"]
        .value_counts()
    )

    print("\nSaved:")
    print(output_file)

    print("\n" + "=" * 60)
    print("RISK ANALYSIS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
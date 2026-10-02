import pandas as pd
import numpy as np
from pathlib import Path

PROCESSED_DIR = Path("data/processed")
OUTPUT_DIR = Path("outputs/forecasts")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():

    print("=" * 60)
    print("FORESIGHT - DEMAND / INVENTORY FORECAST")
    print("=" * 60)

    # ---------------------------------------------------------
    # Load cleaned dataset
    # ---------------------------------------------------------

    files = list(
        PROCESSED_DIR.glob("*_clean.csv")
    )

    if not files:
        raise FileNotFoundError(
            "No cleaned CSV found in data/processed/"
        )

    file = files[0]

    print(f"\nLoading: {file}")

    df = pd.read_csv(file)

    # ---------------------------------------------------------
    # Convert dates
    # ---------------------------------------------------------

    df["start_date"] = pd.to_datetime(
        df["start_date"],
        errors="coerce"
    )

    df["end_date"] = pd.to_datetime(
        df["end_date"],
        errors="coerce"
    )

    # ---------------------------------------------------------
    # Calculate inventory value
    # ---------------------------------------------------------

    df["inventory_value"] = (
        df["qty_on_hand"] *
        df["stock_unit_cost_price"]
    )

    # ---------------------------------------------------------
    # Estimate potential sales value
    # ---------------------------------------------------------

    df["potential_sales_value"] = (
        df["qty_on_hand"] *
        df["stock_unit_selling_price"]
    )

    # ---------------------------------------------------------
    # Create inventory-level forecast proxy
    #
    # Since this dataset does NOT contain historical units sold,
    # we cannot honestly calculate a true demand forecast.
    #
    # Instead, we create a simple inventory-value baseline that
    # can be used for the MVP.
    # ---------------------------------------------------------

    df["forecast_inventory_units"] = (
        df["qty_on_hand"]
    )

    df["forecast_inventory_value"] = (
        df["forecast_inventory_units"] *
        df["stock_unit_cost_price"]
    )

    # ---------------------------------------------------------
    # Product-level aggregation
    # ---------------------------------------------------------

    product_forecast = (
        df.groupby(
            [
                "product_no",
                "product_description",
                "product_division",
                "product_category",
                "product_subcategory"
            ],
            dropna=False
        )
        .agg(
            current_stock_units=("qty_on_hand", "sum"),
            inventory_value=("inventory_value", "sum"),
            potential_sales_value=("potential_sales_value", "sum"),
            average_unit_cost=("stock_unit_cost_price", "mean"),
            average_selling_price=(
                "stock_unit_selling_price",
                "mean"
            )
        )
        .reset_index()
    )

    # ---------------------------------------------------------
    # Save forecast output
    # ---------------------------------------------------------

    output_file = (
        OUTPUT_DIR /
        "forecast_results.csv"
    )

    product_forecast.to_csv(
        output_file,
        index=False
    )

    print("\nForecast output created:")
    print(output_file)

    print(
        f"\nProducts analysed: "
        f"{len(product_forecast):,}"
    )

    print(
        f"Total inventory units: "
        f"{product_forecast['current_stock_units'].sum():,.0f}"
    )

    print(
        f"Total inventory value: ₹"
        f"{product_forecast['inventory_value'].sum():,.2f}"
    )

    print("\n" + "=" * 60)
    print("FORECAST STAGE COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
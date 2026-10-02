import pandas as pd
from pathlib import Path

RISK_DIR = Path("outputs/risk")
OUTPUT_DIR = Path("outputs/recommendations")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():

    print("=" * 60)
    print("FORESIGHT - RECOMMENDATION ENGINE")
    print("=" * 60)

    file = RISK_DIR / "risk_results.csv"

    if not file.exists():
        raise FileNotFoundError(
            "risk_results.csv not found. "
            "Run risk_analysis.py first."
        )

    df = pd.read_csv(file)

    # ---------------------------------------------------------
    # Recommendation logic
    # ---------------------------------------------------------

    recommendations = {
        "Reorder Now":
            "Increase replenishment priority and review stock availability.",

        "Markdown / Clear":
            "Consider markdown or clearance to reduce excess inventory.",

        "Watch / Volatile":
            "Monitor inventory closely and review demand uncertainty.",

        "Healthy":
            "No immediate inventory action required.",

        "Review":
            "Review product-level inventory conditions manually."
    }

    df["recommendation"] = (
        df["decision"]
        .map(recommendations)
        .fillna("Review product manually.")
    )

    # ---------------------------------------------------------
    # Priority
    # ---------------------------------------------------------

    priority_map = {
        "Reorder Now": 1,
        "Watch / Volatile": 2,
        "Markdown / Clear": 3,
        "Healthy": 4,
        "Review": 5
    }

    df["priority"] = (
        df["decision"]
        .map(priority_map)
        .fillna(5)
    )

    # ---------------------------------------------------------
    # Sort
    # ---------------------------------------------------------

    df = df.sort_values(
        ["priority", "rupee_value_at_stake"],
        ascending=[True, False]
    )

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    output_file = (
        OUTPUT_DIR /
        "recommendations.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print("\nRecommendation Summary:")
    print(
        df["decision"]
        .value_counts()
    )

    print("\nSaved:")
    print(output_file)

    print("\n" + "=" * 60)
    print("RECOMMENDATION ENGINE COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
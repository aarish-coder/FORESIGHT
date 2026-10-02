import pandas as pd
from pathlib import Path


# ============================================================
# FORESIGHT - DATA CLEANING PIPELINE
# ============================================================

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_files():
    """Load all CSV files from the raw data folder."""

    csv_files = list(RAW_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            "No CSV files found in data/raw/"
        )

    print("\nFiles found:")
    for file in csv_files:
        print(f" - {file.name}")

    dataframes = {}

    for file in csv_files:
        print(f"\nLoading: {file.name}")

        df = pd.read_csv(file)

        print(f"Rows: {len(df):,}")
        print(f"Columns: {len(df.columns)}")

        dataframes[file.stem] = df

    return dataframes


def basic_cleaning(df, name):
    """Perform safe basic cleaning."""

    print(f"\n{'=' * 60}")
    print(f"CLEANING: {name}")
    print(f"{'=' * 60}")

    # Remove completely empty rows
    before = len(df)
    df = df.dropna(how="all")
    after = len(df)

    print(f"Empty rows removed: {before - after}")

    # Remove duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)

    print(f"Duplicate rows removed: {before - after}")

    # Remove unnecessary spaces from column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Strip whitespace from text columns
    for column in df.select_dtypes(include="object").columns:
        df[column] = df[column].astype(str).str.strip()

    print("\nMissing values:")
    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if len(missing) == 0:
        print("No missing values.")
    else:
        print(missing)

    print("\nFinal shape:")
    print(df.shape)

    return df


def convert_dates(df):
    """Convert columns containing date-like names."""

    for column in df.columns:

        if "date" in column or column in ["week", "month"]:
            try:
                df[column] = pd.to_datetime(
                    df[column],
                    errors="coerce"
                )

                print(f"Converted to date: {column}")

            except Exception:
                pass

    return df


def save_cleaned_files(dataframes):
    """Save cleaned individual datasets."""

    for name, df in dataframes.items():

        output_file = PROCESSED_DIR / f"{name}_clean.csv"

        df.to_csv(
            output_file,
            index=False
        )

        print(f"\nSaved: {output_file}")


def create_combined_dataset(dataframes):
    """
    Create a combined analysis-ready dataset when possible.

    The actual merging logic will be finalized after
    inspecting the provided dataset schemas.
    """

    print("\n" + "=" * 60)
    print("DATASET SUMMARY")
    print("=" * 60)

    for name, df in dataframes.items():

        print(f"\n{name}")
        print("-" * 40)

        print("Columns:")
        for column in df.columns:
            print(f"  - {column}")

        print(f"Rows: {len(df):,}")


def main():

    print("=" * 60)
    print("FORESIGHT DATA CLEANING PIPELINE")
    print("=" * 60)

    # Step 1: Load raw files
    dataframes = load_files()

    # Step 2: Clean each dataset
    cleaned_data = {}

    for name, df in dataframes.items():

        df = basic_cleaning(df, name)
        df = convert_dates(df)

        cleaned_data[name] = df

    # Step 3: Save cleaned datasets
    save_cleaned_files(cleaned_data)

    # Step 4: Show dataset structure
    create_combined_dataset(cleaned_data)

    print("\n" + "=" * 60)
    print("DATA CLEANING COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
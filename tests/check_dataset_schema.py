from pathlib import Path
import pandas as pd

DATA_ROOT = Path("data/Market")

print("=" * 100)
print("FULL DATASET SCHEMA CHECK")
print("=" * 100)

for dataset in sorted(DATA_ROOT.iterdir()):
    if not dataset.is_dir():
        continue

    telemetry = dataset / "telemetry"

    print(f"\nDATASET: {dataset.name}")

    for date_folder in sorted(telemetry.iterdir()):

        print(f"\n  DATE: {date_folder.name}")

        for category in ["metric", "log", "trace"]:

            folder = date_folder / category

            for csv_file in sorted(folder.glob("*.csv")):

                print(f"\n    FILE: {csv_file.name}")

                df = pd.read_csv(csv_file, low_memory=False)

                print(f"    Rows    : {len(df):,}")
                print(f"    Columns : {len(df.columns)}")

                for col in df.columns:

                    non_null = df[col].dropna()

                    sample_types = sorted(
                        {type(x).__name__ for x in non_null.head(1000)}
                    )

                    print(
                        f"       {col:<20}"
                        f"dtype={str(df[col].dtype):<10}"
                        f" sample_types={sample_types}"
                    )
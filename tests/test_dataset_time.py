from pathlib import Path
import pandas as pd

DATASET = Path(r"D:\Market\cloudbed-2\telemetry\2022_03_20\metric\metric_service.csv")


def main():

    print("=" * 40)
    print(" DATASET TIME CHECK ")
    print("=" * 40)

    df = pd.read_csv(DATASET)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nFirst 5 rows:")
    print(df.head())

    # Convert timestamp
    df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    unit="s"
)

    print("\nMin timestamp:")
    print(df["timestamp"].min())

    print("\nMax timestamp:")
    print(df["timestamp"].max())

    print("\nTotal rows:")
    print(len(df))

    print("\nSample timestamps:")
    print(df["timestamp"].head(20))


if __name__ == "__main__":
    main()
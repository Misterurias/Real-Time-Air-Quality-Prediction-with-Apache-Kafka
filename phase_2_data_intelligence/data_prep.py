# phase_2_data_intelligence/data_prep.py
import yaml
import pandas as pd
from pathlib import Path

def load_config():
    """Load configuration from config.yaml next to this script."""
    with open(Path(__file__).parent / "config.yaml", "r") as f:
        return yaml.safe_load(f)

def parse_datetime(df):
    """Parse Date/Time or DateTime columns into a single DateTime column."""
    if "Date" in df.columns and "Time" in df.columns:
        # UCI dataset format: day/month/year hour.minute.second
        dt = pd.to_datetime(
            df["Date"] + " " + df["Time"],
            format="%d/%m/%Y %H.%M.%S",
            errors="coerce"
        )
        df.insert(0, "DateTime", dt)
    elif "DateTime" in df.columns:
        df["DateTime"] = pd.to_datetime(df["DateTime"], errors="coerce")
    else:
        raise ValueError(f"Expected Date/Time columns not found. Found: {df.columns.tolist()}")

    # Drop rows where parsing failed
    before = len(df)
    df = df.dropna(subset=["DateTime"])
    after = len(df)
    if before != after:
        print(f"[INFO] Dropped {before - after} rows with invalid DateTime")
    return df

def resample_hourly(df):
    """Resample to hourly averages, ensuring no NaT in index."""
    df = df.set_index("DateTime").sort_index()
    if df.index.isnull().any():
        raise ValueError("[ERROR] NaT values still present in DateTime index.")
    # Use lowercase 'h' (uppercase 'H' is deprecated)
    hourly = df.resample("h").mean(numeric_only=True)
    return hourly.reset_index()

def clean_air_quality(df, pollutants, aliases, neg200_missing=True):
    """Apply missing value handling and rename pollutant columns."""
    for col in pollutants:
        if col not in df.columns:
            raise ValueError(f"Expected pollutant column missing: {col}")
        if neg200_missing:
            df[col] = df[col].where(df[col] != -200, pd.NA)
    return df.rename(columns=aliases)

def save_clean(df, outdir):
    """Save cleaned hourly data to outputs/tables/clean_hourly.csv."""
    outdir = Path(outdir)
    (outdir / "tables").mkdir(parents=True, exist_ok=True)
    csv_path = outdir / "tables" / "clean_hourly.csv"
    df.to_csv(csv_path, index=False)
    print(f"[SAVED] Cleaned hourly dataset at {csv_path}")
    return csv_path

if __name__ == "__main__":
    cfg = load_config()

    dataset_path = Path(cfg["dataset_path"])
    print(f"[INFO] Reading dataset from {dataset_path}")

    try:
        # Try raw UCI format first (semicolon + comma decimals)
        raw = pd.read_csv(dataset_path, sep=";", decimal=",")
        if len(raw.columns) == 1:  # wrong delimiter, fallback
            raw = pd.read_csv(dataset_path)
    except Exception:
        raw = pd.read_csv(dataset_path)

    raw = parse_datetime(raw)

    keep_cols = ["DateTime"] + cfg["pollutants"]
    raw = raw[keep_cols]

    clean = clean_air_quality(
        raw,
        pollutants=cfg["pollutants"],
        aliases=cfg["aliases"],
        neg200_missing=cfg["negative_200_is_missing"]
    )

    hourly = resample_hourly(clean)
    output_path = save_clean(hourly, cfg["output_dir"])
    print("[INFO] Data preparation complete.")

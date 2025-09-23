# phase_2_data_intelligence/eda_timeseries.py
import yaml
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

plt.rcParams["figure.figsize"] = (12, 4)
plt.rcParams["axes.grid"] = True

def load_config():
    with open(Path(__file__).parent / "config.yaml", "r") as f:
        return yaml.safe_load(f)

def load_clean(cfg):
    path = Path(cfg["output_dir"]) / "tables" / "clean_hourly.csv"
    print(f"[INFO] Loading cleaned dataset from {path}")
    df = pd.read_csv(path, parse_dates=["DateTime"])
    print(f"[INFO] Loaded {len(df)} rows with columns: {df.columns.tolist()}")
    return df

def ensure_dirs(base):
    figs = Path(base) / "figures"
    tabs = Path(base) / "tables"
    figs.mkdir(parents=True, exist_ok=True)
    tabs.mkdir(parents=True, exist_ok=True)
    return figs, tabs

def plot_series(df, cols, figs):
    for c in cols:
        if c not in df.columns:
            print(f"[WARN] Skipping {c}, not found in dataset.")
            continue
        ax = df.set_index("DateTime")[c].plot()
        ax.set_title(f"{c} over time")
        ax.set_xlabel("")
        fig_path = figs / f"ts_{c}.png"
        plt.tight_layout(); plt.savefig(fig_path); plt.close()
        print(f"[SAVED] Time-series plot for {c} → {fig_path}")

def daily_weekly_cycles(df, cols, tabs, figs):
    tmp = df.copy()
    tmp["hour"] = tmp["DateTime"].dt.hour
    tmp["dow"]  = tmp["DateTime"].dt.dayofweek

    for c in cols:
        if c not in tmp.columns:
            continue
        by_hour = tmp.groupby("hour")[c].mean(numeric_only=True)
        by_dow  = tmp.groupby("dow")[c].mean(numeric_only=True)

        by_hour_path = tabs / f"daily_cycle_{c}.csv"
        by_dow_path = tabs / f"weekly_cycle_{c}.csv"
        by_hour.to_csv(by_hour_path)
        by_dow.to_csv(by_dow_path)
        print(f"[SAVED] Daily cycle CSV for {c} → {by_hour_path}")
        print(f"[SAVED] Weekly cycle CSV for {c} → {by_dow_path}")

        # Plots
        by_hour.plot(marker="o", title=f"Daily cycle (avg by hour) - {c}")
        plt.xlabel("Hour of Day"); plt.ylabel(c)
        plt.tight_layout(); plt.savefig(figs / f"daily_cycle_{c}.png"); plt.close()

        by_dow.plot(marker="o", title=f"Weekly cycle (avg by weekday) - {c}")
        plt.xlabel("Day of Week (0=Mon)"); plt.ylabel(c)
        plt.tight_layout(); plt.savefig(figs / f"weekly_cycle_{c}.png"); plt.close()

def correlation_matrix(df, cols, tabs, figs):
    corr = df[cols].corr(method="pearson")
    corr_path = tabs / "correlation_matrix.csv"
    corr.to_csv(corr_path)
    print(f"[SAVED] Correlation matrix CSV → {corr_path}")

    fig, ax = plt.subplots()
    cax = ax.imshow(corr.values, interpolation="nearest", cmap="coolwarm")
    ax.set_title("Correlation Matrix (Pearson)")
    ax.set_xticks(range(len(cols))); ax.set_yticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=45, ha="right"); ax.set_yticklabels(cols)
    fig.colorbar(cax)
    fig_path = figs / "correlation_matrix.png"
    plt.tight_layout(); plt.savefig(fig_path); plt.close()
    print(f"[SAVED] Correlation matrix heatmap → {fig_path}")

if __name__ == "__main__":
    cfg = load_config()
    df = load_clean(cfg)
    figs, tabs = ensure_dirs(cfg["output_dir"])

    # If aliases exist, use their values; else just take all numeric columns except DateTime
    if cfg.get("aliases"):
        cols = list(cfg["aliases"].values())
    else:
        cols = [c for c in df.columns if c != "DateTime" and pd.api.types.is_numeric_dtype(df[c])]

    plot_series(df, cols, figs)
    daily_weekly_cycles(df, cols, tabs, figs)
    correlation_matrix(df, cols, tabs, figs)
    print("[INFO] EDA complete.")

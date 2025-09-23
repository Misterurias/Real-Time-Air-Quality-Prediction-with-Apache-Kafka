# phase_2_data_intelligence/advanced_analytics.py
import yaml
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.tsa.seasonal import STL
import numpy as np

plt.rcParams["figure.figsize"] = (12, 4)
plt.rcParams["axes.grid"] = True

def load_config():
    with open(Path(__file__).parent / "config.yaml", "r") as f:
        return yaml.safe_load(f)

def load_clean(cfg):
    path = Path(cfg["output_dir"]) / "tables" / "clean_hourly.csv"
    df = pd.read_csv(path, parse_dates=["DateTime"]).set_index("DateTime").sort_index()
    return df

def ensure_dirs(base):
    figs = Path(base) / "figures"
    tabs = Path(base) / "tables"
    figs.mkdir(parents=True, exist_ok=True)
    tabs.mkdir(parents=True, exist_ok=True)
    return figs, tabs

def plot_acf_pacf(series, name, figs, nlags=48):
    s = series.dropna()
    if len(s) < 10:
        return

    a = acf(s, nlags=nlags, fft=True, missing="drop")
    p = pacf(s, nlags=min(nlags, len(s)//4), method="yw")

    # ACF
    plt.stem(range(len(a)), a)
    plt.title(f"ACF - {name}")
    plt.xlabel("Lag (hours)"); plt.ylabel("ACF")
    plt.tight_layout(); plt.savefig(figs / f"acf_{name}.png"); plt.close()

    # PACF
    plt.stem(range(len(p)), p)
    plt.title(f"PACF - {name}")
    plt.xlabel("Lag (hours)"); plt.ylabel("PACF")
    plt.tight_layout(); plt.savefig(figs / f"pacf_{name}.png"); plt.close()

def stl_decompose(series, name, figs, tabs, period=24*7):
    s = series.dropna()
    if len(s) < period*2:
        return None
    res = STL(s, period=period, robust=True).fit()

    # Save plots
    res.trend.plot(title=f"STL Trend - {name}"); plt.tight_layout()
    plt.savefig(figs / f"stl_trend_{name}.png"); plt.close()

    res.seasonal.plot(title=f"STL Seasonal - {name}"); plt.tight_layout()
    plt.savefig(figs / f"stl_seasonal_{name}.png"); plt.close()

    res.resid.plot(title=f"STL Residual - {name}"); plt.tight_layout()
    plt.savefig(figs / f"stl_resid_{name}.png"); plt.close()

    # Save to CSV
    out = pd.DataFrame({
        "DateTime": s.index,
        f"{name}_trend": res.trend,
        f"{name}_seasonal": res.seasonal,
        f"{name}_resid": res.resid
    })
    out.to_csv(tabs / f"stl_{name}.csv", index=False)
    print(f"[stl] decomposition saved for {name}")
    return res

def seasonal_zscore_anomalies(series, period=24, z=3.0):
    """Seasonal detrending by hourly-of-day mean; flag |z|>threshold."""
    s = series.copy()
    df = pd.DataFrame({"y": s})
    df["hour"] = df.index.hour
    mu = df.groupby("hour")["y"].transform("mean")
    sd = df.groupby("hour")["y"].transform("std")
    zscores = (df["y"] - mu) / sd.replace(0, np.nan)
    flags = zscores.abs() > z
    return flags, zscores

if __name__ == "__main__":
    cfg = load_config()
    df = load_clean(cfg)
    figs, tabs = ensure_dirs(cfg["output_dir"])
    cols = list(cfg["aliases"].values())

    for c in cols:
        if c not in df.columns:
            continue
        series = df[c]

        # ACF/PACF
        plot_acf_pacf(series, c, figs)

        # STL Decomposition
        stl = stl_decompose(series, c, figs, tabs, period=24*7)

        # Anomaly detection
        flags, z = seasonal_zscore_anomalies(series, period=24, z=3.0)
        out = pd.DataFrame({
            "DateTime": df.index,
            c: series,
            f"{c}_is_anomaly": flags,
            f"{c}_zscore": z
        })
        out.to_csv(tabs / f"anomalies_{c}.csv", index=False)
        print(f"[anomalies] saved for {c}")

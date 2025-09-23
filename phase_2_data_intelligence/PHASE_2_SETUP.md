
# Phase 2 Setup & Reproducibility Guide

This document explains how to recreate the Phase 2 workflow for **Advanced Environmental Data Intelligence and Pattern Analysis**.  
Following these steps will ensure the same results, figures, and tables can be reproduced.

## 1. Environment Setup

- **Python version**: 3.13.7  
- **Virtual Environment**:

```bash
# Create virtual environment
python -m venv .venv

# Activate on macOS/Linux
source .venv/bin/activate

# Activate on Windows (PowerShell)
.venv\Scripts\activate
````

* **Install dependencies**:

```bash
pip install -r requirements.txt
```

Dependencies include:

* `kafka-python`
* `numpy`
* `pandas`
* `matplotlib`
* `statsmodels`
* `pyyaml`

If new packages are added, update the lock file:

```bash
pip freeze > requirements.txt
```


## 2. Data Preparation

The raw dataset is expected at:

```
AirQualityData/cleaned_air_quality.csv
```

Run preprocessing:

```bash
python phase_2_data_intelligence/data_prep.py
```

This script:

* Combines `Date` + `Time` into a proper `DateTime` field
* Replaces invalid `-200` values with `NaN`
* Resamples data into **hourly averages**
* Outputs processed data to:

```
outputs/tables/clean_hourly.csv
```

✅ Check terminal logs for dropped rows due to invalid timestamps.


## 3. Exploratory Data Analysis (EDA)

Run:

```bash
python phase_2_data_intelligence/eda_timeseries.py
```

This generates:

* **Figures** (`outputs/figures/`):

  * Time series plots for pollutants
  * Daily cycle plots (hourly averages)
  * Weekly cycle plots (day-of-week averages)
  * Correlation heatmap

* **Tables** (`outputs/tables/`):

  * Daily cycle CSVs
  * Weekly cycle CSVs
  * Correlation matrix CSV


## 4. Advanced Analytics

Run:

```bash
python phase_2_data_intelligence/advanced_analytics.py
```

This performs advanced time series analysis:

* **ACF & PACF plots** (`acf_*.png`, `pacf_*.png`)
  → Show temporal dependencies and lag correlations

* **STL decomposition** (`stl_trend_*.png`, `stl_seasonal_*.png`, `stl_resid_*.png`)
  → Breaks series into trend, seasonal, and residual components

* **Anomalies detection**
  → Saves anomaly-labeled CSVs (`anomalies_*.csv`) with flags and z-scores

All results are saved under:

```
outputs/figures/
outputs/tables/
```


## 5. Report

The Phase 2 analytical report is documented in:

```
phase_2_data_intelligence/phase_2_report.md
```

Contents:

* **Executive Summary** (2–3 pages)
* **Temporal Pattern Analysis**
* **Correlation Insights**
* **STL decomposition results**
* **Anomaly detection findings**
* **Business implications**
* **Modeling strategy going forward**

This serves as the formal Phase 2 deliverable.


## 6. Reproducibility Notes

* Always activate the virtual environment before running scripts.
* Ensure the dataset format matches expected columns:

  * `Date`, `Time`, `CO(GT)`, `NMHC(GT)`, `C6H6(GT)`, `NOx(GT)`, `NO2(GT)`, etc.
* If your dataset comes with a combined `DateTime` column, scripts handle this automatically.
* Figures may differ slightly depending on library version, but overall trends remain consistent.
* To reset outputs before re-running, clear the `outputs/` folder.


## 7. Workflow Summary

1. **Data Prep** → Clean & resample (`data_prep.py`)
2. **EDA** → Generate baseline visualizations & correlations (`eda_timeseries.py`)
3. **Advanced Analytics** → Perform statistical decomposition, ACF/PACF, anomaly detection (`advanced_analytics.py`)
4. **Report** → Summarize findings & implications (`phase_2_report.md`)

✅ Following these steps guarantees that all Phase 2 deliverables can be recreated end-to-end.

## Academic Integrity Note

This assignment was completed with the use of generative AI (OpenAI ChatGPT, GPT-5, September 2025).  
Prompts and responses are documented in **Appendix A** (`appendix_ai_usage/appendix_kafka.txt`).
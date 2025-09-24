# phase_3_predictive_analytics/src/data_preprocessing.py

import pandas as pd
import numpy as np

def load_and_engineer(path="../data/cleaned_air_quality.csv", target_pollutant="NO2(GT)"):
    # Load raw
    df = pd.read_csv(path)

    # Combine Date + Time into datetime
    df['Datetime'] = pd.to_datetime(
        df['Date'] + ' ' + df['Time'],
        format="%d/%m/%Y %H.%M.%S"
    )
    df = df.set_index('Datetime').drop(columns=['Date', 'Time'])

    # Temporal Features
    df['hour'] = df.index.hour
    df['dayofweek'] = df.index.dayofweek
    df['month'] = df.index.month
    df['is_weekend'] = (df['dayofweek'] >= 5).astype(int)

    # Cyclical Encoding
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)

    # Lagged Features
    for lag in [1, 6, 12, 24]:
        df[f'{target_pollutant}_lag{lag}'] = df[target_pollutant].shift(lag)

    # Rolling Statistics
    for window in [3, 6, 12]:
        df[f'{target_pollutant}_rollmean{window}'] = df[target_pollutant].rolling(window=window).mean()
        df[f'{target_pollutant}_rollstd{window}'] = df[target_pollutant].rolling(window=window).std()

    # Drop NaNs
    df = df.dropna()

    return df

def prepare_features(df, target_pollutant="NO2(GT)"):
    """
    Prepare features for real-time prediction.
    Ensures only numeric values are sent to the model.
    """

    import numpy as np
    import pandas as pd

    # Combine datetime if not already present
    if 'Datetime' not in df.columns and 'Date' in df.columns and 'Time' in df.columns:
        df['Datetime'] = pd.to_datetime(
            df['Date'] + ' ' + df['Time'],
            format="%d/%m/%Y %H.%M.%S"
        )

    # Use datetime as index
    if 'Datetime' in df.columns:
        df = df.set_index('Datetime')

    # Temporal features
    df['hour'] = df.index.hour
    df['dayofweek'] = df.index.dayofweek
    df['month'] = df.index.month
    df['is_weekend'] = (df['dayofweek'] >= 5).astype(int)

    # Cyclical encoding
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)

    # Drop non-numeric and target columns
    features = df.drop(columns=['Date', 'Time', target_pollutant], errors="ignore")

    # Keep only numeric columns
    features = features.select_dtypes(include=['int64', 'float64'])

    return features

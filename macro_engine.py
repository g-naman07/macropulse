import numpy as np
import pandas as pd


def add_time_series_metrics(data):
    required = ["date", "country", "series", "value", "unit", "source"]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))
    df = data.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["date", "value", "country", "series"])
    df = df.sort_values(["country", "series", "date"])
    grouped = df.groupby(["country", "series"], group_keys=False)
    df["mom_change_pct"] = grouped["value"].pct_change() * 100
    # This is a 12-observation comparison; appropriate for monthly series.
    df["yoy_change_pct"] = grouped["value"].pct_change(12) * 100
    df["change"] = grouped["value"].diff()
    df["rolling_mean_change"] = grouped["change"].transform(lambda s: s.rolling(12, min_periods=6).mean())
    df["rolling_std_change"] = grouped["change"].transform(lambda s: s.rolling(12, min_periods=6).std())
    denominator = df["rolling_std_change"].replace(0, np.nan)
    df["change_zscore"] = (df["change"] - df["rolling_mean_change"]) / denominator
    return df


def flag_unusual_changes(view, threshold=2.5):
    flagged = view[view["change_zscore"].abs() >= threshold].copy()
    if flagged.empty:
        return pd.DataFrame(columns=["date", "series", "value", "change", "change_zscore", "source"])
    return flagged[["date", "series", "value", "change", "change_zscore", "source"]].sort_values("date", ascending=False)

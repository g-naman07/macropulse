import requests
import pandas as pd

FRED_OBSERVATIONS_URL = "https://api.stlouisfed.org/fred/series/observations"


def fetch_fred_series(series_id, api_key, observation_start="2015-01-01"):
    """Fetch one public FRED series. API key is supplied by the user, never hard-coded."""
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": observation_start,
        "sort_order": "asc",
    }
    response = requests.get(FRED_OBSERVATIONS_URL, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()
    if "observations" not in payload:
        raise ValueError(payload.get("error_message", "Unexpected FRED response"))
    frame = pd.DataFrame(payload["observations"])
    if frame.empty:
        raise ValueError("FRED returned no observations")
    frame = frame.rename(columns={"observation_date": "date"})
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    frame = frame.dropna(subset=["value"])
    frame["country"] = "United States"
    frame["series"] = series_id
    frame["unit"] = frame.get(" units", "") if " units" in frame.columns else "series units"
    frame["source"] = "FRED"
    return frame[["date", "country", "series", "value", "unit", "source"]]

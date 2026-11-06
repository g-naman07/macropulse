# MacroPulse — Economic Data Intelligence

A macroeconomic time-series dashboard. It loads the included demo data, supports CSV uploads, and can optionally fetch public FRED observations when you provide your own API key.

## Run with sample data

```bash
cd macropulse
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Enable live FRED data

1. Create a free API key from the FRED website.
2. Set it as an environment variable; do not commit it to Git.

Windows PowerShell:

```powershell
$env:FRED_API_KEY="YOUR_KEY"
streamlit run app.py
```

macOS/Linux:

```bash
export FRED_API_KEY="YOUR_KEY"
streamlit run app.py
```

The app includes example series IDs: `CPIAUCSL`, `UNRATE`, `FEDFUNDS`, `DGS10`. FRED series can have different frequencies and units. The demo's YoY calculation compares 12 observations, so verify frequency before interpreting it as a 12-month change.

## CSV schema

`date, country, series, value, unit, source`

## Interview discussion

- Explain why monthly, quarterly and daily series should not be compared without frequency alignment.
- Explain month-over-month and year-over-year changes.
- Explain rolling z-scores and why statistical flags need context.
- Add revision tracking and vintage dates to distinguish first releases from revised economic data.

**Data note:** the included file is synthetic and intended only to test the interface. Live FRED data requires the user's own API key.

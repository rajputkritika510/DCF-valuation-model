"""
data_loader.py
----------------
Handles loading of historical financial data for the DCF model.
Supports:
    1. Loading from a local CSV file (recommended, works offline)
    2. Loading live data from Yahoo Finance via yfinance (optional, needs internet)
"""

import os
import pandas as pd


REQUIRED_COLUMNS = [
    "year", "revenue", "ebit", "tax", "depreciation",
    "capex", "net_debt", "shares_outstanding", "current_price"
]


def load_historical_csv(path: str) -> pd.DataFrame:
    """
    Load historical financial data from a CSV file.

    Expected columns (see data/sample_data.csv for an example):
        year, revenue, ebit, tax, depreciation, capex,
        net_debt, shares_outstanding, current_price

    All monetary values should be in the same unit (e.g. INR Crores).
    """
    df = pd.read_csv(path)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"CSV is missing required columns: {missing}. "
            f"Expected columns: {REQUIRED_COLUMNS}"
        )

    df = df.sort_values("year").reset_index(drop=True)
    return df


def load_historical_excel(path: str, sheet_name=0) -> pd.DataFrame:
    """
    Load historical financial data from an Excel file (.xlsx / .xls).

    Expected columns are the same as load_historical_csv():
        year, revenue, ebit, tax, depreciation, capex,
        net_debt, shares_outstanding, current_price

    sheet_name : name or index of the sheet to read (default: first sheet)
    """
    df = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Excel file is missing required columns: {missing}. "
            f"Expected columns: {REQUIRED_COLUMNS}"
        )

    df = df.sort_values("year").reset_index(drop=True)
    return df


def load_historical_data(path: str, sheet_name=0) -> pd.DataFrame:
    """
    Convenience wrapper that auto-detects file type from the extension
    and routes to the correct loader (.csv -> CSV, .xlsx/.xls -> Excel).
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return load_historical_csv(path)
    elif ext in (".xlsx", ".xls"):
        return load_historical_excel(path, sheet_name=sheet_name)
    else:
        raise ValueError(f"Unsupported file type '{ext}'. Use .csv, .xlsx or .xls")


def load_from_yfinance(ticker: str) -> dict:
    """
    Pull basic company data live from Yahoo Finance.
    Requires internet access and the `yfinance` package.

    NOTE: yfinance does not give a clean 5-year EBIT/FCFF series out of
    the box for every stock, so this is best used to quickly grab
    market data (price, shares outstanding, market cap) while you fill
    in the historical income-statement numbers manually / via CSV.
    """
    try:
        import yfinance as yf
    except ImportError as e:
        raise ImportError(
            "yfinance is not installed. Run: pip install yfinance"
        ) from e

    stock = yf.Ticker(ticker)
    info = stock.info

    data = {
        "ticker": ticker,
        "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "market_cap": info.get("marketCap"),
        "shares_outstanding": info.get("sharesOutstanding"),
        "beta": info.get("beta"),
        "total_debt": info.get("totalDebt"),
        "total_cash": info.get("totalCash"),
    }

    # Net debt = Total Debt - Cash & Equivalents
    if data["total_debt"] is not None and data["total_cash"] is not None:
        data["net_debt"] = data["total_debt"] - data["total_cash"]
    else:
        data["net_debt"] = None

    return data


if __name__ == "__main__":
    # Quick manual test
    df = load_historical_csv("../data/sample_data.csv")
    print(df)

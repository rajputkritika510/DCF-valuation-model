"""
financial_analysis.py
-----------------------
Analyzes historical financial statements to derive the ratios and
trends that will be used as the basis for forecasting assumptions.
"""

import pandas as pd


def calculate_revenue_growth(df: pd.DataFrame) -> pd.DataFrame:
    """Adds a 'revenue_growth' column (year-over-year % change)."""
    df = df.copy()
    df["revenue_growth"] = df["revenue"].pct_change()
    return df


def calculate_ebit_margin(df: pd.DataFrame) -> pd.DataFrame:
    """Adds an 'ebit_margin' column = EBIT / Revenue."""
    df = df.copy()
    df["ebit_margin"] = df["ebit"] / df["revenue"]
    return df


def calculate_tax_rate(df: pd.DataFrame) -> pd.DataFrame:
    """Adds an 'effective_tax_rate' column = Tax / EBIT."""
    df = df.copy()
    df["effective_tax_rate"] = df["tax"] / df["ebit"]
    return df


def calculate_capex_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """Adds a 'capex_ratio' column = Capex / Revenue."""
    df = df.copy()
    df["capex_ratio"] = df["capex"] / df["revenue"]
    return df


def calculate_da_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """Adds a 'da_ratio' column = Depreciation & Amortization / Revenue."""
    df = df.copy()
    df["da_ratio"] = df["depreciation"] / df["revenue"]
    return df


def full_historical_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Runs every historical ratio calculation and returns an enriched dataframe."""
    df = calculate_revenue_growth(df)
    df = calculate_ebit_margin(df)
    df = calculate_tax_rate(df)
    df = calculate_capex_ratio(df)
    df = calculate_da_ratio(df)
    return df


def summarize_historicals(df: pd.DataFrame) -> dict:
    """
    Returns average historical ratios that can be used as sensible
    starting-point assumptions for the forecast stage.
    """
    enriched = full_historical_analysis(df)

    summary = {
        "avg_revenue_growth": round(enriched["revenue_growth"].mean(skipna=True), 4),
        "avg_ebit_margin": round(enriched["ebit_margin"].mean(), 4),
        "avg_tax_rate": round(enriched["effective_tax_rate"].mean(), 4),
        "avg_capex_ratio": round(enriched["capex_ratio"].mean(), 4),
        "avg_da_ratio": round(enriched["da_ratio"].mean(), 4),
        "latest_revenue": enriched["revenue"].iloc[-1],
        "latest_net_debt": enriched["net_debt"].iloc[-1],
        "latest_shares_outstanding": enriched["shares_outstanding"].iloc[-1],
        "latest_price": enriched["current_price"].iloc[-1],
    }
    return summary

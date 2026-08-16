"""
forecasting.py
----------------
Projects Revenue, EBIT and Free Cash Flow to the Firm (FCFF)
forward for the explicit forecast period (typically 5 years).
"""


def forecast_revenue(base_revenue: float, growth_rate: float, years: int = 5) -> list:
    """
    Projects revenue forward using a constant annual growth rate.
    Returns a list of `years` future revenue values.
    """
    revenues = []
    revenue = base_revenue
    for _ in range(years):
        revenue = revenue * (1 + growth_rate)
        revenues.append(revenue)
    return revenues


def forecast_revenue_declining_growth(
    base_revenue: float, start_growth: float, end_growth: float, years: int = 5
) -> list:
    """
    More realistic revenue forecast: growth rate linearly decays from
    `start_growth` (year 1) down to `end_growth` (final year). This
    mirrors how high-growth companies typically mature over time.
    """
    revenues = []
    revenue = base_revenue
    if years == 1:
        step = 0
    else:
        step = (start_growth - end_growth) / (years - 1)

    for i in range(years):
        growth = start_growth - (step * i)
        revenue = revenue * (1 + growth)
        revenues.append(revenue)
    return revenues


def forecast_ebit(revenues: list, ebit_margin: float) -> list:
    """Projects EBIT = Revenue * EBIT Margin for each forecast year."""
    return [rev * ebit_margin for rev in revenues]


def forecast_fcff(
    revenues: list,
    ebit_list: list,
    tax_rate: float,
    da_pct: float,
    capex_pct: float,
    nwc_pct: float,
) -> tuple:
    """
    Calculates FCFF for each forecast year:

        NOPAT = EBIT * (1 - Tax Rate)
        FCFF  = NOPAT + D&A - Capex - Change in NWC

    Returns (fcff_list, details_list) where details_list has a
    breakdown dict per year (useful for displaying in the dashboard).
    """
    fcff_list = []
    details = []

    for rev, ebit in zip(revenues, ebit_list):
        nopat = ebit * (1 - tax_rate)
        da = rev * da_pct
        capex = rev * capex_pct
        change_nwc = rev * nwc_pct

        fcff = nopat + da - capex - change_nwc
        fcff_list.append(fcff)

        details.append({
            "revenue": rev,
            "ebit": ebit,
            "nopat": nopat,
            "d_and_a": da,
            "capex": capex,
            "change_in_nwc": change_nwc,
            "fcff": fcff,
        })

    return fcff_list, details

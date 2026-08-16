"""
wacc.py
--------
Calculates the discount rate (WACC) used to bring future cash flows
back to present value.

WACC = (E / (D+E)) * Ke  +  (D / (D+E)) * Kd * (1 - Tax Rate)

Where:
    Ke = Cost of Equity (via CAPM)
    Kd = Cost of Debt
    E  = Market value of Equity
    D  = Market value of Debt
"""


def cost_of_equity_capm(risk_free_rate: float, beta: float, market_return: float) -> float:
    """
    Cost of Equity using the Capital Asset Pricing Model (CAPM).

        Ke = Rf + Beta * (Rm - Rf)
    """
    return risk_free_rate + beta * (market_return - risk_free_rate)


def calculate_wacc(
    market_cap: float,
    total_debt: float,
    cost_of_equity: float,
    cost_of_debt: float,
    tax_rate: float,
) -> float:
    """
    Weighted Average Cost of Capital.

    market_cap   -> Market value of Equity (E)
    total_debt   -> Market/Book value of Debt (D)
    cost_of_equity -> Ke (decimal, e.g. 0.1127 for 11.27%)
    cost_of_debt   -> Kd (decimal, pre-tax cost of borrowing)
    tax_rate       -> effective tax rate (decimal)
    """
    equity = market_cap
    debt = total_debt
    total_value = equity + debt

    if total_value == 0:
        raise ValueError("Equity + Debt cannot be zero when calculating WACC.")

    equity_weight = equity / total_value
    debt_weight = debt / total_value

    wacc = (equity_weight * cost_of_equity) + (
        debt_weight * cost_of_debt * (1 - tax_rate)
    )
    return wacc


def wacc_breakdown(
    market_cap: float,
    total_debt: float,
    risk_free_rate: float,
    beta: float,
    market_return: float,
    cost_of_debt: float,
    tax_rate: float,
) -> dict:
    """Convenience function that returns Ke, Kd(after-tax), weights, and final WACC."""
    ke = cost_of_equity_capm(risk_free_rate, beta, market_return)
    wacc = calculate_wacc(market_cap, total_debt, ke, cost_of_debt, tax_rate)

    total_value = market_cap + total_debt
    return {
        "cost_of_equity": ke,
        "cost_of_debt_pretax": cost_of_debt,
        "cost_of_debt_aftertax": cost_of_debt * (1 - tax_rate),
        "equity_weight": market_cap / total_value,
        "debt_weight": total_debt / total_value,
        "wacc": wacc,
    }

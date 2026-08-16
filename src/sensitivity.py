"""
sensitivity.py
-----------------
Two "must-have" analytical features for the project:

1. sensitivity_table()  -> WACC vs Terminal Growth grid of intrinsic values
2. scenario_analysis()  -> Bear / Base / Bull comparison
"""

import pandas as pd

try:
    from .dcf import DCFModel
except ImportError:
    from dcf import DCFModel


def sensitivity_table(base_params: dict, wacc_range: list, growth_range: list) -> pd.DataFrame:
    """
    Builds a matrix of intrinsic value per share across a range of
    WACC values (rows) and Terminal Growth values (columns).

    base_params : dict of all DCFModel constructor args EXCEPT
                   'wacc' and 'terminal_growth' (those are swept).
    wacc_range   : list of WACC values to test, e.g. [0.085, 0.09, 0.095, 0.10, 0.105]
    growth_range : list of terminal growth values to test, e.g. [0.03, 0.035, 0.04, 0.045]
    """
    rows = []
    for wacc in wacc_range:
        row = []
        for g in growth_range:
            if wacc <= g:
                row.append(None)  # invalid combination, terminal value formula breaks
                continue
            params = dict(base_params)
            params["wacc"] = wacc
            params["terminal_growth"] = g
            model = DCFModel(**params)
            result = model.run()
            row.append(round(result["value_per_share"], 2))
        rows.append(row)

    df = pd.DataFrame(
        rows,
        index=[f"{w * 100:.1f}%" for w in wacc_range],
        columns=[f"{g * 100:.1f}%" for g in growth_range],
    )
    df.index.name = "WACC"
    df.columns.name = "Terminal Growth"
    return df


def scenario_analysis(base_params: dict, bear_overrides: dict, bull_overrides: dict) -> dict:
    """
    Runs the DCF three times: Bear case, Base case, Bull case.

    base_params    : the "Base Case" full parameter dict
    bear_overrides : dict of params to override for the Bear case
                      (e.g. lower growth, higher WACC)
    bull_overrides : dict of params to override for the Bull case
                      (e.g. higher growth, lower WACC)

    Returns a dict: {"Bear": result_dict, "Base": result_dict, "Bull": result_dict}
    """
    scenarios_out = {}

    scenario_defs = {
        "Bear": bear_overrides,
        "Base": {},
        "Bull": bull_overrides,
    }

    for name, overrides in scenario_defs.items():
        params = dict(base_params)
        params.update(overrides)
        model = DCFModel(**params)
        scenarios_out[name] = model.run()

    return scenarios_out


def scenario_summary_table(scenarios: dict) -> pd.DataFrame:
    """Converts the scenario_analysis() output into a clean summary DataFrame."""
    rows = []
    for name, result in scenarios.items():
        rows.append({
            "Scenario": name,
            "Value per Share": round(result["value_per_share"], 2),
            "Enterprise Value": round(result["enterprise_value"], 2),
            "Equity Value": round(result["equity_value"], 2),
            "Upside vs Market %": round(result["upside_pct"] * 100, 2) if result["upside_pct"] is not None else None,
        })
    # Order Bear, Base, Bull
    order = {"Bear": 0, "Base": 1, "Bull": 2}
    rows.sort(key=lambda r: order.get(r["Scenario"], 99))
    return pd.DataFrame(rows)

"""
test_dcf.py
-------------
Basic unit tests for the DCF valuation engine.

Run with:
    pytest tests/
"""

import sys
import os
import pytest

# Make sure `src` is importable when running pytest from the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.dcf import DCFModel
from src.wacc import cost_of_equity_capm, calculate_wacc
from src.forecasting import forecast_revenue, forecast_ebit, forecast_fcff
from src.sensitivity import sensitivity_table, scenario_analysis


BASE_PARAMS = dict(
    revenue_base=240893,
    revenue_growth=0.08,
    ebit_margin=0.26,
    tax_rate=0.25,
    da_pct=0.03,
    capex_pct=0.05,
    nwc_pct=0.01,
    wacc=0.095,
    terminal_growth=0.04,
    net_debt=-22400,
    shares_outstanding=365,
    forecast_years=5,
    current_price=3200,
)


def test_revenue_forecast_grows():
    revenues = forecast_revenue(100, 0.10, years=3)
    assert len(revenues) == 3
    assert revenues[0] == pytest.approx(110)
    assert revenues[-1] > revenues[0]


def test_ebit_forecast():
    revenues = [100, 110, 121]
    ebit = forecast_ebit(revenues, 0.25)
    assert ebit == [25.0, 27.5, 30.25]


def test_fcff_is_positive_for_healthy_company():
    revenues = forecast_revenue(240893, 0.08, years=5)
    ebit_list = forecast_ebit(revenues, 0.26)
    fcff_list, _ = forecast_fcff(revenues, ebit_list, 0.25, 0.03, 0.05, 0.01)
    assert all(f > 0 for f in fcff_list)


def test_cost_of_equity_capm():
    ke = cost_of_equity_capm(risk_free_rate=0.068, beta=0.95, market_return=0.115)
    assert ke == pytest.approx(0.11265, rel=1e-3)


def test_wacc_between_cost_of_equity_and_debt():
    wacc = calculate_wacc(
        market_cap=1000000, total_debt=200000,
        cost_of_equity=0.12, cost_of_debt=0.08, tax_rate=0.25
    )
    assert 0 < wacc < 0.12


def test_dcf_model_runs_and_returns_expected_keys():
    model = DCFModel(**BASE_PARAMS)
    result = model.run()
    expected_keys = {
        "value_per_share", "enterprise_value", "equity_value",
        "terminal_value", "sum_pv_fcff", "upside_pct", "verdict",
    }
    assert expected_keys.issubset(result.keys())
    assert result["value_per_share"] > 0


def test_dcf_raises_when_wacc_below_terminal_growth():
    bad_params = dict(BASE_PARAMS)
    bad_params["wacc"] = 0.03
    bad_params["terminal_growth"] = 0.04
    with pytest.raises(ValueError):
        DCFModel(**bad_params)


def test_sensitivity_table_shape():
    wacc_range = [0.085, 0.09, 0.095, 0.10]
    growth_range = [0.03, 0.035, 0.04]
    params = {k: v for k, v in BASE_PARAMS.items() if k not in ("wacc", "terminal_growth")}
    df = sensitivity_table(params, wacc_range, growth_range)
    assert df.shape == (4, 3)


def test_scenario_analysis_bull_greater_than_bear():
    bear = {"revenue_growth": 0.05, "ebit_margin": 0.23, "wacc": 0.10, "terminal_growth": 0.03}
    bull = {"revenue_growth": 0.11, "ebit_margin": 0.29, "wacc": 0.08, "terminal_growth": 0.05}
    scenarios = scenario_analysis(BASE_PARAMS, bear, bull)
    assert scenarios["Bull"]["value_per_share"] > scenarios["Bear"]["value_per_share"]

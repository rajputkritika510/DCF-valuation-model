"""
test_import_parser.py
------------------------
Tests for src/import_parser.py — makes sure both file formats
(raw historical data, and pre-built valuation workbooks) are
correctly detected and parsed.
"""

import sys
import os
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.import_parser import detect_historical_format, parse_prebuilt_workbook


def test_detect_historical_format_true_for_matching_columns():
    df = pd.DataFrame({
        "year": [2023, 2024],
        "revenue": [100, 110],
        "ebit": [20, 22],
        "tax": [5, 5.5],
        "depreciation": [3, 3],
        "capex": [4, 4],
        "net_debt": [10, 10],
        "shares_outstanding": [50, 50],
        "current_price": [200, 210],
    })
    assert detect_historical_format(df) is True


def test_detect_historical_format_false_for_unrelated_columns():
    df = pd.DataFrame({"Metric": ["Revenue"], "Year 1": [100]})
    assert detect_historical_format(df) is False


def test_parse_prebuilt_workbook_extracts_key_fields(tmp_path):
    import openpyxl

    wb = openpyxl.Workbook()
    ws1 = wb.active
    ws1.title = "DCF Values"
    ws1.append(["Forecast Year", "FY2026E", "FY2027E"])
    ws1.append(["Revenue", 1000, 1090])
    ws1.append(["EBIT Margin", 0.20, 0.21])
    ws1.append(["Tax Rate", 0.25, 0.25])
    ws1.append(["Depreciation & Amortization", 40, 44])
    ws1.append(["Capital Expenditure", 50, 55])
    ws1.append(["Change in Net Working Capital", 10, 11])

    ws2 = wb.create_sheet("Key Assumptions")
    ws2.append(["Assumption", "Value"])
    ws2.append(["WACC", 0.10])
    ws2.append(["Terminal Growth Rate", 0.04])
    ws2.append(["Net Debt (Cr)", 500])
    ws2.append(["Shares Outstanding (Cr)", 40])
    ws2.append(["Current Market Price", 900])

    file_path = tmp_path / "test_prebuilt.xlsx"
    wb.save(file_path)

    result = parse_prebuilt_workbook(str(file_path))
    assert result["found"] is True
    params = result["params"]
    assert params["revenue_base"] == 1000
    assert round(params["ebit_margin"], 2) == 0.21 or round(params["ebit_margin"], 3) == 0.205
    assert params["wacc"] == 0.10
    assert params["terminal_growth"] == 0.04
    assert params["net_debt"] == 500
    assert params["shares_outstanding"] == 40
    assert params["current_price"] == 900

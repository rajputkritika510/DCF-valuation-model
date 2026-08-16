"""
dcf.py
-------
The core DCF engine. Ties together revenue/EBIT/FCFF forecasting,
discounting, terminal value, and final intrinsic value per share.

Flow:
    Revenue -> EBIT -> NOPAT -> FCFF -> Discount (WACC)
    -> Terminal Value -> Enterprise Value -> Equity Value
    -> Intrinsic Value per Share
"""

try:
    from .forecasting import forecast_revenue, forecast_revenue_declining_growth, forecast_ebit, forecast_fcff
except ImportError:
    # allows running this file directly (python src/dcf.py) as well as
    # importing it as part of the `src` package
    from forecasting import forecast_revenue, forecast_revenue_declining_growth, forecast_ebit, forecast_fcff


class DCFModel:
    def __init__(
        self,
        revenue_base: float,
        revenue_growth: float,
        ebit_margin: float,
        tax_rate: float,
        da_pct: float,
        capex_pct: float,
        nwc_pct: float,
        wacc: float,
        terminal_growth: float,
        net_debt: float,
        shares_outstanding: float,
        forecast_years: int = 5,
        current_price: float = None,
        declining_growth_end: float = None,
    ):
        """
        Parameters
        ----------
        revenue_base : latest actual revenue (starting point for forecast)
        revenue_growth : year-1 revenue growth assumption (decimal)
        ebit_margin : assumed EBIT margin held across the forecast (decimal)
        tax_rate : effective tax rate (decimal)
        da_pct : D&A as % of revenue (decimal)
        capex_pct : Capex as % of revenue (decimal)
        nwc_pct : Change in Net Working Capital as % of revenue (decimal)
        wacc : discount rate (decimal)
        terminal_growth : perpetual growth rate used in terminal value (decimal)
        net_debt : total debt minus cash (same currency unit as revenue)
        shares_outstanding : number of shares
        forecast_years : explicit forecast horizon, default 5
        current_price : current market price per share (optional, for upside calc)
        declining_growth_end : if provided, revenue growth linearly decays
                                from `revenue_growth` to this value over the
                                forecast period instead of staying constant
        """
        if wacc <= terminal_growth:
            raise ValueError(
                "WACC must be greater than the terminal growth rate, "
                "otherwise the terminal value formula breaks (division by <= 0)."
            )

        self.revenue_base = revenue_base
        self.revenue_growth = revenue_growth
        self.ebit_margin = ebit_margin
        self.tax_rate = tax_rate
        self.da_pct = da_pct
        self.capex_pct = capex_pct
        self.nwc_pct = nwc_pct
        self.wacc = wacc
        self.terminal_growth = terminal_growth
        self.net_debt = net_debt
        self.shares_outstanding = shares_outstanding
        self.forecast_years = forecast_years
        self.current_price = current_price
        self.declining_growth_end = declining_growth_end

    def run(self) -> dict:
        # 1. Forecast revenue
        if self.declining_growth_end is not None:
            revenues = forecast_revenue_declining_growth(
                self.revenue_base, self.revenue_growth,
                self.declining_growth_end, self.forecast_years
            )
        else:
            revenues = forecast_revenue(self.revenue_base, self.revenue_growth, self.forecast_years)

        # 2. Forecast EBIT
        ebit_list = forecast_ebit(revenues, self.ebit_margin)

        # 3. Forecast FCFF
        fcff_list, fcff_details = forecast_fcff(
            revenues, ebit_list, self.tax_rate, self.da_pct, self.capex_pct, self.nwc_pct
        )

        # 4. Discount each year's FCFF back to present value
        pv_fcff_list = [
            fcff / ((1 + self.wacc) ** (i + 1)) for i, fcff in enumerate(fcff_list)
        ]
        sum_pv_fcff = sum(pv_fcff_list)

        # 5. Terminal Value (Gordon Growth / Perpetuity method)
        terminal_fcff = fcff_list[-1] * (1 + self.terminal_growth)
        terminal_value = terminal_fcff / (self.wacc - self.terminal_growth)
        pv_terminal_value = terminal_value / ((1 + self.wacc) ** self.forecast_years)

        # 6. Enterprise Value -> Equity Value -> Value per Share
        enterprise_value = sum_pv_fcff + pv_terminal_value
        equity_value = enterprise_value - self.net_debt
        value_per_share = equity_value / self.shares_outstanding

        # 7. Upside / downside vs current market price
        upside_pct = None
        verdict = None
        if self.current_price:
            upside_pct = (value_per_share - self.current_price) / self.current_price
            verdict = "Potentially Undervalued" if upside_pct > 0 else "Potentially Overvalued"

        return {
            "revenues": revenues,
            "ebit_list": ebit_list,
            "fcff_list": fcff_list,
            "fcff_details": fcff_details,
            "pv_fcff_list": pv_fcff_list,
            "sum_pv_fcff": sum_pv_fcff,
            "terminal_value": terminal_value,
            "pv_terminal_value": pv_terminal_value,
            "enterprise_value": enterprise_value,
            "equity_value": equity_value,
            "value_per_share": value_per_share,
            "current_price": self.current_price,
            "upside_pct": upside_pct,
            "verdict": verdict,
            "wacc": self.wacc,
            "terminal_growth": self.terminal_growth,
        }


if __name__ == "__main__":
    # Quick manual sanity check with example numbers
    model = DCFModel(
        revenue_base=260000,
        revenue_growth=0.08,
        ebit_margin=0.26,
        tax_rate=0.25,
        da_pct=0.03,
        capex_pct=0.05,
        nwc_pct=0.01,
        wacc=0.095,
        terminal_growth=0.04,
        net_debt=-15000,  # net cash
        shares_outstanding=365,
        forecast_years=5,
        current_price=3200,
    )
    result = model.run()
    print(f"Intrinsic Value per Share: {result['value_per_share']:.2f}")
    print(f"Verdict: {result['verdict']} ({result['upside_pct']*100:.2f}%)")

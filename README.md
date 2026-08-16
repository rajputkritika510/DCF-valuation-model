# 💰 DCF Valuation Model

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python\&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit\&logoColor=white)
![Excel](https://img.shields.io/badge/Excel-DCF%20Model-217346?logo=microsoftexcel\&logoColor=white)
![Pytest](https://img.shields.io/badge/Tests-Pytest-0A9EDC?logo=pytest\&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

## 🌐 Live Demo

🚀 **[Open DCF Valuation Dashboard](https://dcf-valuation-model-lvb2jmucpzjeqkqqvyhvtd.streamlit.app/)**

Explore the interactive DCF valuation model with forecasting, WACC, sensitivity analysis, and scenario analysis.

A Python-based **Discounted Cash Flow (DCF) Valuation Model** designed to estimate a company's intrinsic value using historical financial data, financial forecasting, WACC, terminal value, and scenario-based analysis.

The project combines **Corporate Finance, Financial Modeling, Python, Excel, and Data Analytics** into an interactive valuation system.

> **Core Question:** What is the estimated intrinsic value of a company based on its future cash-generating potential?

---

## 📌 Project Overview

The DCF Valuation Model follows a standard corporate finance valuation approach:

**Historical Financials → Forecast → FCFF → WACC → Terminal Value → Enterprise Value → Equity Value → Intrinsic Value per Share**

The project provides both:

* 📊 An interactive **Streamlit dashboard**
* 📗 A formula-driven **Excel DCF model**

---

## ✨ Key Features

### 📂 Financial Data Input

* Import historical financial data through CSV or Excel files
* Structured format for revenue, EBIT, tax, depreciation, capital expenditure, and other valuation inputs
* Sample dataset included for demonstration

### 🔮 Financial Forecasting

* Five-year revenue forecasting
* EBIT and operating margin projections
* NOPAT calculation
* Free Cash Flow to Firm (FCFF) estimation

### 💸 WACC Calculation

* Weighted Average Cost of Capital calculation
* Cost of Equity using the CAPM approach
* Incorporates cost of debt and capital structure

### ♾️ Terminal Value

* Gordon Growth Model
* Terminal value calculation based on long-term growth assumptions

### 🏢 DCF Valuation

Calculates:

**Enterprise Value → Equity Value → Intrinsic Value per Share**

### 🎯 Sensitivity Analysis

Analyze how changes in:

* WACC
* Terminal Growth Rate

can affect the estimated intrinsic value.

### 🐻🐂 Scenario Analysis

Compare three valuation scenarios:

* 🐻 Bear Case
* ⚖️ Base Case
* 🐂 Bull Case

### 📊 Interactive Dashboard

The Streamlit dashboard provides:

* KPI summary
* Historical financial analysis
* Forecast & FCFF analysis
* Valuation overview
* Sensitivity analysis
* Scenario comparison
* Interactive charts

### 📗 Excel DCF Model

The project also includes an Excel-based valuation model with formulas for:

* WACC
* Financial Forecast
* FCFF
* Terminal Value
* Enterprise Value
* Equity Value
* Sensitivity Analysis

### ✅ Testing

Core valuation calculations and data-processing functions are tested using **pytest**.

---

## 🖥️ Dashboard

The dashboard is organized into five major sections:

| Section            | Description                                                   |
| ------------------ | ------------------------------------------------------------- |
| 🏠 Overview        | Intrinsic value, valuation summary, and key valuation metrics |
| 📊 Historical Data | Historical financial performance and key ratios               |
| 🔮 Forecast & FCFF | Revenue, EBIT, NOPAT, and FCFF projections                    |
| 🎯 Sensitivity     | WACC vs. Terminal Growth sensitivity analysis                 |
| 🐻🐂 Scenarios     | Bear, Base, and Bull valuation comparison                     |

---

## 📁 Project Structure

```text
dcf-valuation-model/
│
├── data/
│   ├── sample_data.csv
│   └── DCF_Model_Template.xlsx
│
├── src/
│   ├── data_loader.py
│   ├── financial_analysis.py
│   ├── forecasting.py
│   ├── wacc.py
│   ├── dcf.py
│   └── sensitivity.py
│
├── dashboard/
│   └── app.py
│
├── tests/
│   └── test_dcf.py
│
├── build_excel_template.py
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/rajputkritika510/DCF-valuation-model.git
cd DCF-valuation-model
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

**Windows:**

```bash
venv\Scripts\activate
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit Dashboard

```bash
streamlit run dashboard/app.py
```

The application will open in your browser.

### 5. Run Tests

```bash
pytest tests/ -v
```

---

## 🧮 DCF Methodology

The model follows the standard DCF valuation framework:

```text
Historical Financial Data
          ↓
Revenue Forecast
          ↓
EBIT Forecast
          ↓
NOPAT
          ↓
FCFF
          ↓
Discount Using WACC
          ↓
Present Value of FCFF
          ↓
Terminal Value
          ↓
Enterprise Value
          ↓
Equity Value
          ↓
Intrinsic Value Per Share
```

### Free Cash Flow to Firm

**FCFF = NOPAT + D&A − CapEx − Change in NWC**

### Cost of Equity — CAPM

**Ke = Rf + β × (Rm − Rf)**

### Enterprise Value

**Enterprise Value = PV of Forecast FCFF + PV of Terminal Value**

### Equity Value

**Equity Value = Enterprise Value − Net Debt**

### Intrinsic Value Per Share

**Intrinsic Value Per Share = Equity Value ÷ Shares Outstanding**

---

## 📊 Input Data

The model can work with structured historical financial data containing fields such as:

| Input                | Purpose                  |
| -------------------- | ------------------------ |
| Revenue              | Revenue forecasting      |
| EBIT                 | Operating profitability  |
| Tax Rate             | NOPAT calculation        |
| Depreciation         | FCFF calculation         |
| Capital Expenditure  | FCFF calculation         |
| Change in NWC        | FCFF calculation         |
| Net Debt             | Equity value calculation |
| Shares Outstanding   | Per-share valuation      |
| Current Market Price | Valuation comparison     |

A sample dataset is included in the repository for demonstration purposes.

---

## 📗 Excel Model

The Excel model provides a standalone DCF valuation framework.

Users can modify the relevant assumptions and review the resulting:

* Forecast financials
* WACC
* FCFF
* Terminal Value
* Enterprise Value
* Equity Value
* Intrinsic Value
* Sensitivity Analysis

To regenerate the Excel model:

```bash
python build_excel_template.py
```

---

## ⚠️ Important Disclaimer

DCF valuation is highly dependent on assumptions such as:

* Revenue growth
* EBIT margin
* WACC
* Terminal growth rate
* Capital expenditure
* Working capital requirements

Small changes in these assumptions can significantly affect the estimated intrinsic value.

**This project is for educational and analytical purposes only and should not be considered investment advice or a guaranteed Buy/Sell recommendation.**

---

## 🛠️ Technology Stack

| Technology    | Purpose                            |
| ------------- | ---------------------------------- |
| **Python**    | Core financial modeling            |
| **Pandas**    | Data processing                    |
| **NumPy**     | Numerical calculations             |
| **SciPy**     | Financial/statistical calculations |
| **yfinance**  | Market data integration            |
| **Streamlit** | Interactive dashboard              |
| **Plotly**    | Interactive visualizations         |
| **OpenPyXL**  | Excel model generation             |
| **Pytest**    | Automated testing                  |

---

## 🗺️ Future Improvements

* [x] Historical financial analysis
* [x] Five-year financial forecasting
* [x] WACC calculation using CAPM
* [x] Terminal value calculation
* [x] Sensitivity analysis
* [x] Bull / Base / Bear scenarios
* [x] Interactive Streamlit dashboard
* [x] Excel DCF model
* [x] Automated testing
* [ ] Expanded market-data integration
* [ ] Automated company/ticker selection
* [ ] PDF valuation report generation
* [ ] Portfolio-level valuation comparison

---

## 🎯 Learning Outcomes

This project demonstrates practical knowledge of:

* Corporate Finance
* DCF Valuation
* Financial Modeling
* Equity Valuation
* WACC & CAPM
* Financial Forecasting
* Sensitivity Analysis
* Scenario Analysis
* Python Programming
* Excel Financial Modeling
* Data Visualization
* Automated Testing

---

## 📄 License

This project is licensed under the **MIT License**.

See the `LICENSE` file for more information.

---

## 👨‍💻 About the Project

This project was developed as a **Finance + Technology portfolio project** to demonstrate the practical application of corporate finance concepts through Python, Excel, and data analytics.

If you find the project useful, feel free to ⭐ **Star** the repository and explore the code.

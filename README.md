# Fund P&L Attribution Report

A Python tool that generates a monthly fund-level P&L attribution report — breaking down performance by **security**, **sector**, and **geography**, comparing actuals against a budget baseline and prior month, and automatically surfacing the top contributors and detractors.

Built as an extension of monthly variance analysis work done at **Mitel Communications** (FP&A, Global Corporate Finance), where I produced monthly actuals-to-budget variance reports across EMEA, APAC, and Americas. This project adapts that workflow to a fund accounting context — the same analytical logic, applied to an investment portfolio instead of a corporate cost base.

---

## What It Does

| Feature | Detail |
|---|---|
| **Security-level P&L** | Monthly return and P&L for each position |
| **Budget vs. Actuals** | Compares actual P&L to a pre-set budget return assumption per security |
| **Prior Month Variance** | Flags month-over-month P&L movements |
| **Sector Attribution** | Aggregates and ranks P&L contribution by sector |
| **Geography Attribution** | Aggregates and ranks P&L contribution by region |
| **Top Movers** | Auto-identifies top 3 contributors and detractors |
| **Excel Report** | Formatted 5-sheet management report, auto-generated |

---

## Output Report

The tool generates a dated Excel file in `/output/` with five formatted sheets:

| Sheet | Content |
|---|---|
| **Fund Summary** | Top-level KPIs: NAV, total P&L, vs. budget, vs. prior month |
| **Positions** | Full security-level breakdown with all variances |
| **Sector** | P&L attribution rolled up by sector with totals row |
| **Geography** | P&L attribution rolled up by geography with totals row |
| **Top Movers** | Top 3 contributors (green) and detractors (red) |

---

## Project Structure

```
pnl_attribution/
├── pnl_attribution.py   # Main script — configure portfolio and fund params here
├── pnl_report.py        # Excel report generator (5 sheets)
├── requirements.txt
├── output/              # Generated reports (git-ignored)
└── README.md
```

---

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/pnl-attribution.git
cd pnl-attribution
pip install -r requirements.txt
python pnl_attribution.py
```

---

## Configuration

Edit the `PORTFOLIO` dict and fund parameters at the top of `pnl_attribution.py`:

```python
PORTFOLIO = {
    "AAPL": {"shares": 50, "sector": "Technology", "geo": "North America", "budget_return_pct": 2.0},
    "JPM":  {"shares": 40, "sector": "Financials",  "geo": "North America", "budget_return_pct": 1.2},
    ...
}

CASH_BALANCE       = 75_000.00
FUND_NAME          = "Global Multi-Asset Fund"
REPORTING_CURRENCY = "USD"
```

`budget_return_pct` is the expected monthly return % for each security — used to calculate budget P&L and variance.

---

## Data Source

Live and historical price data is pulled from **Yahoo Finance** via the `yfinance` library. The script automatically pulls the last two completed calendar months to calculate current P&L and prior month comparison. No API key required.

---

## Sample Console Output

```
============================================================
  Global Multi-Asset Fund
  MONTHLY P&L ATTRIBUTION REPORT
============================================================

Fetching market data...
  Fetching May 2025 prices (2025-05-01 to 2025-05-31)...
  Fetching Apr 2025 prices (2025-04-01 to 2025-04-30)...

Calculating P&L attribution...

--- FUND SUMMARY: May 2025 ---
  Total NAV:          $  1,842,310.00
  Actual P&L:         $     28,415.22
  Budget P&L:         $     22,800.00
  Vs. Budget:         $     +5,615.22
  Vs. Prior Month:    $     -3,210.40

--- TOP 3 CONTRIBUTORS ---
  MSFT     Technology           P&L: $  8,210.40  (+4.82%)
  AAPL     Technology           P&L: $  6,540.10  (+3.91%)
  TSM      Technology           P&L: $  4,820.30  (+3.24%)

--- TOP 3 DETRACTORS ---
  BABA     Consumer Disc.       P&L: $ -2,410.80  (-3.62%)
  XOM      Energy               P&L: $ -1,820.50  (-1.94%)
  NESN.SW  Consumer Staples     P&L: $   -920.40  (-1.22%)

Report saved to: output/PnL_Attribution_May_2025_20250601.xlsx
============================================================
```

---

## Why I Built This

Fund accounting and FP&A teams produce monthly P&L attribution reports as a core deliverable — breaking down what drove performance, where variances originated, and what to flag for senior stakeholders. This project gave me hands-on exposure to that workflow at the fund level: sourcing live market data, calculating position-level P&L against a budget, attributing results across multiple dimensions, and producing a management-ready report automatically.

---

## Skills Demonstrated

- Monthly P&L calculation and multi-dimensional attribution (sector, geography)
- Budget vs. actuals variance analysis at position and portfolio level
- Financial data sourcing and manipulation with `pandas` and `yfinance`
- Automated exception identification (top contributors / detractors)
- Production-quality Excel reporting with `openpyxl`

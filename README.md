# Fund P&L Attribution Report

An automated monthly P&L attribution tool for a 14-stock global equity portfolio. It pulls live market data, calculates position-level P&L against a budget and the prior month, breaks down performance by sector and geography, and generates a formatted 5-sheet Excel management report.

Built as an extension of the monthly variance analysis work I did at Mitel Communications in Global Corporate Finance, comparing actuals to budget for senior leadership. This project applies the same analytical logic to an investment portfolio instead of a corporate cost base.

## What It Does

| Feature | Detail |
|---|---|
| Security-level P&L | Monthly return and P&L for each position |
| Budget vs. Actuals | Compares actual P&L to a budget return assumption per security |
| Prior Month Variance | Flags month-over-month P&L movements |
| Sector Attribution | Aggregates and ranks P&L contribution by sector |
| Geography Attribution | Aggregates and ranks P&L contribution by region |
| Top Movers | Identifies top 3 contributors and detractors (worst first) |
| Currency Conversion | Converts non-USD holdings to USD before calculating P&L |
| Excel Report | Formatted 5-sheet management report, generated automatically |

## Portfolio

AAPL, MSFT, GOOGL, JPM, GS, JNJ, UNH, XOM, SHEL, ASML, NESN.SW, TM, TSM, BABA

## Output Report

The notebook saves a dated Excel file in the `output` folder with five sheets:

| Sheet | Content |
|---|---|
| Fund Summary | Key figures: NAV, total P&L, vs. budget, vs. prior month |
| Positions | Full security-level breakdown with all variances |
| Sector | P&L attribution by sector with a totals row |
| Geography | P&L attribution by geography with a totals row |
| Top Movers | Top 3 contributors (green) and detractors (red) |

## Currency Handling

Nestlé (NESN.SW) trades on the Swiss exchange in Swiss francs. The tool pulls the daily CHF to USD exchange rate and converts Nestlé's prices to dollars before calculating P&L and NAV, so every position rolls up into the fund total in one currency.

## How I Built It

I used AI to help design the logic and write the code, then validated every output against manual calculations. While reviewing the results, I noticed Nestlé's numbers didn't line up with the rest of the fund, traced it to prices being treated as U.S. dollars, and added the currency conversion to fix it.

## How to Run

1. Install the required libraries: `pip install yfinance pandas openpyxl`
2. Open `pnl_attribution.ipynb` in JupyterLab
3. Run all cells
4. The Excel report is saved in the `output` folder

## Configuration

Edit the `PORTFOLIO` dictionary and fund settings in the notebook:

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

`budget_return_pct` is the expected monthly return for each security, used to calculate budget P&L and variance.

## Data Source

Price data comes from Yahoo Finance through the yfinance library. The notebook automatically pulls the last two completed calendar months to calculate current P&L and the prior month comparison. No API key is required.

## Why I Built This

Fund accounting and FP&A teams produce monthly P&L attribution reports as a core deliverable, explaining what drove performance, where variances came from, and what to flag for senior stakeholders. This project gave me hands-on experience with that workflow at the fund level, from sourcing live market data to producing a management-ready report automatically.

## Skills Demonstrated

- Monthly P&L calculation and attribution by sector and geography
- Budget vs. actuals variance analysis at the position and portfolio level
- Financial data sourcing and manipulation with pandas and yfinance
- Multi-currency handling and data validation
- Automated identification of top contributors and detractors
- Excel reporting with openpyxl

# Fund P&L Attribution Report

An automated monthly P&L attribution tool for a 14-stock global equity portfolio. It pulls live market data, calculates position-level P&L against budget and the prior month, and generates a formatted 5-sheet Excel management report.

## What It Does

- Pulls daily prices for 14 real stocks using yfinance
- Calculates monthly P&L, market value, and returns for each position
- Compares results against budget and the prior month
- Breaks down performance by sector and geography
- Ranks the top contributors and detractors (worst detractors first)
- Exports a formatted Excel report for management review

## Portfolio

AAPL, MSFT, GOOGL, JPM, GS, JNJ, UNH, XOM, SHEL, ASML, NESN.SW, TM, TSM, BABA

## Excel Report (5 Sheets)

1. **Fund Summary**: total P&L, NAV, and performance versus budget
2. **Positions**: position-level P&L, market value, and returns
3. **Sector**: P&L and variance by sector
4. **Geography**: P&L and variance by region
5. **Top Movers**: largest contributors (green) and detractors (red)

## Currency Handling

Nestlé (NESN.SW) trades on the Swiss exchange in Swiss francs. The tool pulls the daily CHF to USD exchange rate and converts Nestlé's prices to dollars before calculating P&L and NAV, so every position rolls up into the fund total in a single currency.

## How I Built It

I used AI to help design the logic and write the code, then validated every output against manual calculations to make sure the numbers were accurate. While reviewing the results, I caught an issue where Nestlé's prices were being treated as U.S. dollars and added the currency conversion to fix it.

## How to Run

1. Install the required libraries: `pip install yfinance pandas openpyxl`
2. Open `pnl_attribution.ipynb` in JupyterLab
3. Run all cells
4. The Excel report is saved in the `output` folder

## Tools

Python, pandas, yfinance, openpyxl, Excel

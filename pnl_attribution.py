"""
Fund P&L Attribution Report
-----------------------------
Author: Anagha Athreyas

PORTFOLIO CONSTRUCTION PHILOSOPHY
-----------------------------------
This fund simulates a globally diversified, large-cap equity portfolio.
Stock selection follows four criteria used by institutional fund managers:

1. MARKET CAP > $100B (Mega/Large-cap only)
   - Large-cap stocks are more liquid, more widely covered by analysts,
     and less volatile than small/mid-cap stocks.
   - Institutional funds like Bridgewater prefer liquid, deep markets
     where large positions can be entered and exited without moving the price.

2. AVERAGE DAILY TRADING VOLUME > $500M
   - High volume = easy to execute trades without slippage.
   - Low-volume stocks are harder to value and harder to exit in stress scenarios.

3. SECTOR DIVERSIFICATION (6 sectors represented)
   - Concentration in one sector creates correlated risk.
   - A diversified fund spreads exposure so that a drawdown in one sector
     does not wipe out the whole portfolio.
   - Sectors covered: Technology, Financials, Healthcare, Energy,
     Consumer Discretionary, Consumer Staples.

4. GEOGRAPHIC DIVERSIFICATION (3 regions represented)
   - North America, Europe, Asia Pacific.
   - Global exposure hedges against region-specific macro risk
     (e.g. US rate hikes, European energy crisis, China slowdown).

WHY THESE SPECIFIC STOCKS:
   AAPL, MSFT, GOOGL  — Mega-cap US tech, highest liquidity globally
   JPM, GS            — Systemically important US financials
   JNJ, UNH           — Defensive US healthcare
   XOM, SHEL          — US and European energy majors
   ASML               — European semiconductor leader, critical supply chain
   NESN.SW            — Swiss consumer staples, defensive non-US exposure
   TM                 — Japanese auto, Asia Pacific consumer discretionary
   TSM                — Taiwan semiconductor, Asia Pacific tech exposure
   BABA               — Chinese e-commerce; included to represent high-beta
                        emerging market risk within the Asia Pacific sleeve

WHAT THIS REPORT DOES:
   - Calculates monthly P&L for each position (actual price move x shares held)
   - Compares actual P&L to a budget return assumption set at portfolio construction
   - Compares to prior month to identify momentum shifts
   - Attributes P&L by sector and geography to show WHERE performance came from
   - Flags top contributors and detractors for management review
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pnl_report import generate_pnl_report


# ─────────────────────────────────────────────────────────────────────────────
# PORTFOLIO CONFIGURATION
#
# Selection criteria applied to each stock:
#   - Market cap > $100B (large/mega cap only)
#   - Avg daily volume > $500M (institutional liquidity threshold)
#   - Sector and geographic diversification maintained
#   - Budget return % = conservative monthly return assumption at construction
#     (used to measure whether the position is performing in line with expectations)
# ─────────────────────────────────────────────────────────────────────────────

PORTFOLIO = {
    # ── NORTH AMERICA: TECHNOLOGY ──────────────────────────────────────────
    # All three are mega-cap ($1T+), highest global trading volumes.
    # Core holdings in any large-cap global fund.
    "AAPL":  {"shares": 50,  "sector": "Technology",       "geo": "North America",
              "budget_return_pct": 2.0,
              "selection_reason": "Mega-cap US tech. Market cap ~$3T. Daily volume ~$10B. Largest position in most global indices."},

    "MSFT":  {"shares": 30,  "sector": "Technology",       "geo": "North America",
              "budget_return_pct": 1.8,
              "selection_reason": "Mega-cap US tech. Market cap ~$3T. Cloud and AI revenue growth. High institutional ownership."},

    "GOOGL": {"shares": 15,  "sector": "Technology",       "geo": "North America",
              "budget_return_pct": 1.5,
              "selection_reason": "Mega-cap US tech. Market cap ~$2T. Advertising + cloud diversification. High liquidity."},

    # ── NORTH AMERICA: FINANCIALS ──────────────────────────────────────────
    # Both are systemically important financial institutions (SIFIs).
    # Deep liquidity, strong correlation to macro environment.
    "JPM":   {"shares": 40,  "sector": "Financials",       "geo": "North America",
              "budget_return_pct": 1.2,
              "selection_reason": "Largest US bank by assets. Market cap ~$550B. Benchmark financial sector holding."},

    "GS":    {"shares": 20,  "sector": "Financials",       "geo": "North America",
              "budget_return_pct": 1.0,
              "selection_reason": "Leading global investment bank. Market cap ~$170B. High beta to capital markets activity."},

    # ── NORTH AMERICA: HEALTHCARE ──────────────────────────────────────────
    # Defensive sector. Low correlation to economic cycles.
    # Included to reduce portfolio volatility during market downturns.
    "JNJ":   {"shares": 25,  "sector": "Healthcare",       "geo": "North America",
              "budget_return_pct": 0.8,
              "selection_reason": "Diversified healthcare giant. Market cap ~$380B. Defensive, dividend-paying. Reduces portfolio beta."},

    "UNH":   {"shares": 18,  "sector": "Healthcare",       "geo": "North America",
              "budget_return_pct": 1.1,
              "selection_reason": "Largest US health insurer. Market cap ~$450B. Consistent earnings growth. Managed care exposure."},

    # ── NORTH AMERICA: ENERGY ──────────────────────────────────────────────
    # Commodity-linked. Acts as inflation hedge.
    # Included to provide diversification against rising energy prices.
    "XOM":   {"shares": 35,  "sector": "Energy",           "geo": "North America",
              "budget_return_pct": 0.5,
              "selection_reason": "Largest US energy major. Market cap ~$480B. Inflation hedge. High free cash flow generation."},

    # ── EUROPE: TECHNOLOGY ────────────────────────────────────────────────
    # ASML is the global monopoly supplier of EUV lithography machines.
    # No semiconductor fab in the world can make advanced chips without ASML.
    "ASML":  {"shares": 12,  "sector": "Technology",       "geo": "Europe",
              "budget_return_pct": 1.4,
              "selection_reason": "Global monopoly in EUV lithography. Market cap ~$280B. Critical semiconductor supply chain. European tech anchor."},

    # ── EUROPE: ENERGY ────────────────────────────────────────────────────
    "SHEL":  {"shares": 30,  "sector": "Energy",           "geo": "Europe",
              "budget_return_pct": 0.6,
              "selection_reason": "European energy major. Market cap ~$200B. Diversifies energy exposure beyond US markets."},

    # ── EUROPE: CONSUMER STAPLES ──────────────────────────────────────────
    # Defensive, non-cyclical. Provides stability to the European sleeve.
    "NESN.SW":{"shares": 20, "sector": "Consumer Staples", "geo": "Europe",
               "budget_return_pct": 0.7,
               "selection_reason": "World's largest food & beverage company. Market cap ~$230B. Defensive European exposure. CHF-denominated FX diversification."},

    # ── ASIA PACIFIC: TECHNOLOGY ──────────────────────────────────────────
    "TSM":   {"shares": 28,  "sector": "Technology",       "geo": "Asia Pacific",
              "budget_return_pct": 1.6,
              "selection_reason": "World's largest contract chipmaker. Market cap ~$800B. Manufactures chips for Apple, Nvidia, AMD. Asia tech anchor."},

    # ── ASIA PACIFIC: CONSUMER DISCRETIONARY ─────────────────────────────
    "TM":    {"shares": 22,  "sector": "Consumer Disc.",   "geo": "Asia Pacific",
              "budget_return_pct": 0.9,
              "selection_reason": "World's largest automaker by volume. Market cap ~$230B. JPY-denominated. Represents Asia Pacific consumer exposure."},

    "BABA":  {"shares": 25,  "sector": "Consumer Disc.",   "geo": "Asia Pacific",
              "budget_return_pct": -0.5,
              "selection_reason": "China's largest e-commerce platform. Market cap ~$200B. High-beta emerging market position. Intentionally sized small due to regulatory and geopolitical risk. Negative budget return reflects elevated risk premium."},
}

# ─────────────────────────────────────────────────────────────────────────────
# FUND PARAMETERS
# ─────────────────────────────────────────────────────────────────────────────

CASH_BALANCE       = 75_000.00   # Cash reserve held for liquidity and rebalancing
FUND_NAME          = "Global Multi-Asset Fund"
REPORTING_CURRENCY = "USD"


# ─────────────────────────────────────────────────────────────────────────────
# DATE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def get_month_boundaries(offset_months=0):
    """Return (first_day, last_day) for the target month."""
    today  = datetime.today()
    target = today - relativedelta(months=offset_months)
    first  = target.replace(day=1)
    last   = (first + relativedelta(months=1)) - timedelta(days=1)
    return first, last


def fetch_monthly_prices(tickers, month_offset=0):
    """
    Fetch the first and last available closing price for a given month.
    Uses a 5-day buffer on each side to handle weekends and market holidays.
    Returns dict: {ticker: {"open": float, "close": float}}
    """
    first, last = get_month_boundaries(offset_months=month_offset)
    buffer_start = first - timedelta(days=5)
    buffer_end   = last  + timedelta(days=5)

    print(f"  Fetching {first.strftime('%b %Y')} prices ({first.date()} to {last.date()})...")

    raw = yf.download(
        tickers,
        start=buffer_start.strftime("%Y-%m-%d"),
        end=buffer_end.strftime("%Y-%m-%d"),
        auto_adjust=True,
        progress=False
    )

    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw["Close"]
    else:
        prices = raw[["Close"]].rename(columns={"Close": tickers[0]})

    # Filter strictly to the calendar month
    prices = prices[
        (prices.index >= pd.Timestamp(first)) &
        (prices.index <= pd.Timestamp(last))
    ]
    prices = prices.dropna(how="all")

    result = {}
    for ticker in tickers:
        col = ticker if ticker in prices.columns else None
        if col and not prices[col].dropna().empty:
            result[ticker] = {
                "open":  float(prices[col].dropna().iloc[0]),
                "close": float(prices[col].dropna().iloc[-1]),
            }
        else:
            result[ticker] = {"open": np.nan, "close": np.nan}

    return result


# ─────────────────────────────────────────────────────────────────────────────
# P&L CALCULATIONS
# ─────────────────────────────────────────────────────────────────────────────

def build_position_pnl(current_prices, prior_prices):
    """
    Security-level P&L for current month.

    Actual P&L   = shares x (month close price - month open price)
    Budget P&L   = shares x month open price x budget_return_pct
    Prior P&L    = same calculation applied to prior month prices
    Vs Budget    = Actual P&L - Budget P&L  (positive = outperformed)
    Vs Prior     = Actual P&L - Prior P&L   (positive = improved MoM)
    """
    rows = []

    for ticker, meta in PORTFOLIO.items():
        shares = meta["shares"]
        cur    = current_prices.get(ticker, {})
        prev   = prior_prices.get(ticker, {})

        cur_open    = cur.get("open",  np.nan)
        cur_close   = cur.get("close", np.nan)
        prior_open  = prev.get("open",  np.nan)
        prior_close = prev.get("close", np.nan)

        # Current month
        cur_pnl        = shares * (cur_close - cur_open)          if not (np.isnan(cur_open)   or np.isnan(cur_close))   else np.nan
        cur_return_pct = (cur_close - cur_open) / cur_open * 100  if not (np.isnan(cur_open)   or np.isnan(cur_close))   else np.nan

        # Prior month
        prior_pnl = shares * (prior_close - prior_open) if not (np.isnan(prior_open) or np.isnan(prior_close)) else np.nan

        # Budget
        budget_pnl = shares * cur_open * (meta["budget_return_pct"] / 100) if not np.isnan(cur_open) else np.nan

        # Variances
        vs_budget = cur_pnl - budget_pnl if not (np.isnan(cur_pnl) or np.isnan(budget_pnl)) else np.nan
        vs_prior  = cur_pnl - prior_pnl  if not (np.isnan(cur_pnl) or np.isnan(prior_pnl))  else np.nan

        rows.append({
            "Ticker":              ticker,
            "Sector":              meta["sector"],
            "Geography":           meta["geo"],
            "Shares":              shares,
            "Month Open ($)":      round(cur_open, 2)        if not np.isnan(cur_open)        else None,
            "Month Close ($)":     round(cur_close, 2)       if not np.isnan(cur_close)       else None,
            "Monthly Return (%)":  round(cur_return_pct, 4)  if not np.isnan(cur_return_pct)  else None,
            "Actual P&L ($)":      round(cur_pnl, 2)         if not np.isnan(cur_pnl)         else None,
            "Prior Month P&L ($)": round(prior_pnl, 2)       if not np.isnan(prior_pnl)       else None,
            "Budget P&L ($)":      round(budget_pnl, 2)      if not np.isnan(budget_pnl)      else None,
            "Vs. Budget ($)":      round(vs_budget, 2)       if not np.isnan(vs_budget)       else None,
            "Vs. Prior Month ($)": round(vs_prior, 2)        if not np.isnan(vs_prior)        else None,
        })

    return pd.DataFrame(rows)


def build_sector_attribution(df):
    """Roll up P&L by sector. Shows which sectors drove or dragged performance."""
    return (
        df.groupby("Sector").agg(**{
            "Actual P&L ($)":      ("Actual P&L ($)",      "sum"),
            "Prior Month P&L ($)": ("Prior Month P&L ($)", "sum"),
            "Budget P&L ($)":      ("Budget P&L ($)",      "sum"),
            "Vs. Budget ($)":      ("Vs. Budget ($)",      "sum"),
            "Vs. Prior Month ($)": ("Vs. Prior Month ($)", "sum"),
        })
        .round(2)
        .sort_values("Actual P&L ($)", ascending=False)
        .reset_index()
    )


def build_geo_attribution(df):
    """Roll up P&L by geography. Shows regional performance contribution."""
    return (
        df.groupby("Geography").agg(**{
            "Actual P&L ($)":      ("Actual P&L ($)",      "sum"),
            "Prior Month P&L ($)": ("Prior Month P&L ($)", "sum"),
            "Budget P&L ($)":      ("Budget P&L ($)",      "sum"),
            "Vs. Budget ($)":      ("Vs. Budget ($)",      "sum"),
            "Vs. Prior Month ($)": ("Vs. Prior Month ($)", "sum"),
        })
        .round(2)
        .sort_values("Actual P&L ($)", ascending=False)
        .reset_index()
    )


def build_top_movers(df, n=3):
    """Identify top N contributors and detractors by actual P&L."""
    s    = df.dropna(subset=["Actual P&L ($)"]).sort_values("Actual P&L ($)", ascending=False)
    cols = ["Ticker", "Sector", "Geography", "Actual P&L ($)", "Monthly Return (%)"]
    return s.head(n)[cols].reset_index(drop=True), s.tail(n)[cols].reset_index(drop=True)


def build_fund_summary(df, month_label):
    """Compute top-level fund KPIs for the summary sheet."""
    total_mv = df["Shares"].multiply(df["Month Close ($)"].fillna(0)).sum() + CASH_BALANCE
    return {
        "Fund":                   FUND_NAME,
        "Reporting Month":        month_label,
        "Reporting Currency":     REPORTING_CURRENCY,
        "Total Fund NAV ($)":     round(total_mv, 2),
        "Total Actual P&L ($)":   round(df["Actual P&L ($)"].sum(), 2),
        "Total Budget P&L ($)":   round(df["Budget P&L ($)"].sum(), 2),
        "Total Prior P&L ($)":    round(df["Prior Month P&L ($)"].sum(), 2),
        "Vs. Budget ($)":         round(df["Actual P&L ($)"].sum() - df["Budget P&L ($)"].sum(), 2),
        "Vs. Prior Month ($)":    round(df["Actual P&L ($)"].sum() - df["Prior Month P&L ($)"].sum(), 2),
    }


def print_selection_criteria():
    """Print the portfolio construction rationale to console."""
    print("\n--- PORTFOLIO CONSTRUCTION CRITERIA ---")
    print("  Market Cap:   > $100B (large/mega-cap only)")
    print("  Avg Volume:   > $500M daily (institutional liquidity)")
    print("  Sectors:      6 (Technology, Financials, Healthcare,")
    print("                   Energy, Consumer Disc., Consumer Staples)")
    print("  Geographies:  3 (North America, Europe, Asia Pacific)")
    print("  Positions:    14 stocks + cash reserve")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print(f"  {FUND_NAME}")
    print("  MONTHLY P&L ATTRIBUTION REPORT")
    print("=" * 60)

    print_selection_criteria()

    tickers = list(PORTFOLIO.keys())

    print("\nFetching market data...")
    current_prices = fetch_monthly_prices(tickers, month_offset=1)
    prior_prices   = fetch_monthly_prices(tickers, month_offset=2)

    _, last_day = get_month_boundaries(offset_months=1)
    month_label = last_day.strftime("%B %Y")

    print("\nCalculating P&L attribution...")
    position_df              = build_position_pnl(current_prices, prior_prices)
    sector_df                = build_sector_attribution(position_df)
    geo_df                   = build_geo_attribution(position_df)
    contributors, detractors = build_top_movers(position_df)
    summary                  = build_fund_summary(position_df, month_label)

    print(f"\n--- FUND SUMMARY: {month_label} ---")
    print(f"  Total NAV:        ${summary['Total Fund NAV ($)']:>14,.2f}")
    print(f"  Actual P&L:       ${summary['Total Actual P&L ($)']:>14,.2f}")
    print(f"  Budget P&L:       ${summary['Total Budget P&L ($)']:>14,.2f}")
    print(f"  Vs. Budget:       ${summary['Vs. Budget ($)']:>+14,.2f}")
    print(f"  Vs. Prior Month:  ${summary['Vs. Prior Month ($)']:>+14,.2f}")

    print(f"\n--- TOP 3 CONTRIBUTORS ---")
    for _, r in contributors.iterrows():
        print(f"  {r['Ticker']:<8} {r['Sector']:<20}  "
              f"P&L: ${r['Actual P&L ($)']:>9,.2f}  ({r['Monthly Return (%)']:+.2f}%)")

    print(f"\n--- TOP 3 DETRACTORS ---")
    for _, r in detractors.iterrows():
        print(f"  {r['Ticker']:<8} {r['Sector']:<20}  "
              f"P&L: ${r['Actual P&L ($)']:>9,.2f}  ({r['Monthly Return (%)']:+.2f}%)")

    output_path = generate_pnl_report(
        summary, position_df, sector_df, geo_df,
        contributors, detractors, month_label
    )
    print(f"\nReport saved to: {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()

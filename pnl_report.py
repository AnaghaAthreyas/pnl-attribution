"""
pnl_report.py
--------------
Generates a formatted Excel management report with five sheets:
  1. Fund Summary     - top-level KPIs
  2. Positions        - security-level P&L vs budget and prior month
  3. Sector           - sector-level attribution
  4. Geography        - geo-level attribution
  5. Top Movers       - top 3 contributors and detractors
"""

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime
import os


# ─── COLORS ───────────────────────────────────
DARK_NAVY  = "1F2D3D"
MID_BLUE   = "2E4A6B"
LIGHT_BLUE = "D6E4F0"
WHITE      = "FFFFFF"
GREEN      = "1E8449"
RED        = "C0392B"
AMBER      = "D68910"
LIGHT_GRAY = "F4F6F7"
BORDER_COL = "CCCCCC"


def _border():
    s = Side(style="thin", color=BORDER_COL)
    return Border(left=s, right=s, top=s, bottom=s)

def _fill(color):
    return PatternFill("solid", fgColor=color)

def _hdr(ws, row, col, value, bg=MID_BLUE, fg=WHITE, bold=True, size=9, center=True):
    c = ws.cell(row, col, value=value)
    c.font = Font(bold=bold, color=fg, size=size)
    c.fill = _fill(bg)
    c.alignment = Alignment(horizontal="center" if center else "left", vertical="center")
    c.border = _border()
    return c

def _cell(ws, row, col, value, fmt=None, color=None, bold=False, bg=None, align="right"):
    c = ws.cell(row, col, value=value)
    if fmt:   c.number_format = fmt
    if bg:    c.fill = _fill(bg)
    if color: c.font = Font(color=color, bold=bold, size=9)
    else:     c.font = Font(size=9, bold=bold)
    c.alignment = Alignment(horizontal=align)
    c.border = _border()
    return c

def _title(ws, text, cols, bg=DARK_NAVY):
    ws.merge_cells(f"A1:{get_column_letter(cols)}1")
    c = ws["A1"]
    c.value = text
    c.font = Font(bold=True, color=WHITE, size=12)
    c.fill = _fill(bg)
    c.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 22

def _set_widths(ws, widths: dict):
    for col, w in widths.items():
        ws.column_dimensions[col].width = w

def _pnl_color(val):
    if val is None: return None
    return GREEN if val >= 0 else RED


# ─── SHEET 1: FUND SUMMARY ───────────────────

def _write_summary(ws, summary: dict):
    _title(ws, f"FUND SUMMARY  |  {summary['Reporting Month']}", 3)

    fields = [
        ("Fund",                 summary["Fund"],                       "@"),
        ("Reporting Month",      summary["Reporting Month"],            "@"),
        ("Reporting Currency",   summary["Reporting Currency"],         "@"),
        ("Total Fund NAV",       summary["Total Fund NAV ($)"],         "#,##0.00"),
        ("Total Actual P&L",     summary["Total Actual P&L ($)"],       "#,##0.00"),
        ("Total Budget P&L",     summary["Total Budget P&L ($)"],       "#,##0.00"),
        ("Total Prior Month P&L",summary["Total Prior P&L ($)"],        "#,##0.00"),
        ("Vs. Budget",           summary["Vs. Budget ($)"],             "+#,##0.00;-#,##0.00"),
        ("Vs. Prior Month",      summary["Vs. Prior Month ($)"],        "+#,##0.00;-#,##0.00"),
    ]

    for i, (label, value, fmt) in enumerate(fields):
        r = i + 3
        bg = LIGHT_GRAY if i % 2 == 0 else WHITE
        l = ws.cell(r, 1, value=label)
        l.font = Font(bold=True, size=9)
        l.fill = _fill(bg)
        l.border = _border()
        l.alignment = Alignment(horizontal="left")

        v = ws.cell(r, 2, value=value)
        v.number_format = fmt
        v.fill = _fill(bg)
        v.border = _border()
        v.alignment = Alignment(horizontal="right")
        v.font = Font(size=9)

        if label in ("Vs. Budget", "Vs. Prior Month") and isinstance(value, (int, float)):
            v.font = Font(color=_pnl_color(value), bold=True, size=9)

        ws.merge_cells(f"B{r}:C{r}")

    _set_widths(ws, {"A": 25, "B": 20, "C": 10})


# ─── SHEET 2: POSITIONS ──────────────────────

def _write_positions(ws, df: pd.DataFrame):
    cols = list(df.columns)
    _title(ws, "SECURITY-LEVEL P&L ATTRIBUTION", len(cols))

    for j, h in enumerate(cols, 1):
        _hdr(ws, 2, j, h)
    ws.row_dimensions[2].height = 16

    for i, row in df.iterrows():
        r = i + 3
        bg = LIGHT_GRAY if i % 2 == 0 else WHITE
        fmts = ["@","@","@","0","#,##0.00","#,##0.00",'0.00"%"',
                "#,##0.00","#,##0.00","#,##0.00","+#,##0.00;-#,##0.00","+#,##0.00;-#,##0.00"]
        aligns = ["left","left","left","right","right","right","right","right","right","right","right","right"]

        for j, (val, fmt, aln) in enumerate(zip(row, fmts, aligns), 1):
            actual = val  # Monthly Return already stored as a plain number e.g. 12.83
            c = _cell(ws, r, j, actual, fmt=fmt, bg=bg, align=aln)

            # Color P&L columns
            if j in (8, 11, 12) and isinstance(val, (int, float)):
                c.font = Font(color=_pnl_color(val), bold=True, size=9)

    _set_widths(ws, {"A": 8,"B": 18,"C": 16,"D": 8,"E": 14,"F": 14,
                     "G": 16,"H": 14,"I": 16,"J": 14,"K": 16,"L": 18})


# ─── SHEET 3: SECTOR ─────────────────────────

def _write_attribution(ws, df: pd.DataFrame, title_text: str, group_col: str):
    cols = list(df.columns)
    _title(ws, title_text, len(cols))

    for j, h in enumerate(cols, 1):
        _hdr(ws, 2, j, h)
    ws.row_dimensions[2].height = 16

    fmts = ["@", "#,##0.00", "#,##0.00", "#,##0.00", "+#,##0.00;-#,##0.00", "+#,##0.00;-#,##0.00"]

    for i, row in df.iterrows():
        r = i + 3
        bg = LIGHT_GRAY if i % 2 == 0 else WHITE
        for j, (val, fmt) in enumerate(zip(row, fmts), 1):
            aln = "left" if j == 1 else "right"
            c = _cell(ws, r, j, val, fmt=fmt, bg=bg, align=aln)
            if j in (4, 5, 6) and isinstance(val, (int, float)):
                c.font = Font(color=_pnl_color(val), bold=True, size=9)

    # Totals row
    r_total = len(df) + 3
    _cell(ws, r_total, 1, "TOTAL", bold=True, bg=MID_BLUE, align="left")
    ws.cell(r_total, 1).font = Font(bold=True, color=WHITE, size=9)
    for j in range(2, len(cols) + 1):
        col_name = df.columns[j - 1]
        total = df[col_name].sum()
        c = _cell(ws, r_total, j, round(total, 2), fmt=fmts[j-1], bg=MID_BLUE)
        c.font = Font(bold=True, color=WHITE, size=9)

    _set_widths(ws, {"A": 20, "B": 16, "C": 18, "D": 16, "E": 16, "F": 18})


# ─── SHEET 5: TOP MOVERS ─────────────────────

def _write_top_movers(ws, contributors: pd.DataFrame, detractors: pd.DataFrame):
    _title(ws, "TOP MOVERS  |  CONTRIBUTORS & DETRACTORS", 5)

    # Contributors
    ws.merge_cells("A3:E3")
    c = ws["A3"]
    c.value = "TOP 3 CONTRIBUTORS"
    c.font = Font(bold=True, color=WHITE, size=10)
    c.fill = _fill(GREEN)
    c.alignment = Alignment(horizontal="center")

    hdrs = ["Ticker", "Sector", "Geography", "Actual P&L ($)", "Monthly Return (%)"]
    for j, h in enumerate(hdrs, 1):
        _hdr(ws, 4, j, h, bg=MID_BLUE)

    for i, row in contributors.iterrows():
        r = i + 5
        vals = [row["Ticker"], row["Sector"], row["Geography"],
                row["Actual P&L ($)"], row["Monthly Return (%)"]]
        fmts = ["@","@","@","#,##0.00",'0.00"%"']
        aligns = ["left","left","left","right","right"]
        for j, (val, fmt, aln) in enumerate(zip(vals, fmts, aligns), 1):
            c = _cell(ws, r, j, val, fmt=fmt, bg=_fill("E9F7EF").fgColor, align=aln)
            c.fill = _fill("E9F7EF")
            if j == 4: c.font = Font(color=GREEN, bold=True, size=9)

    # Detractors
    ws.merge_cells("A9:E9")
    c = ws["A9"]
    c.value = "TOP 3 DETRACTORS"
    c.font = Font(bold=True, color=WHITE, size=10)
    c.fill = _fill(RED)
    c.alignment = Alignment(horizontal="center")

    for j, h in enumerate(hdrs, 1):
        _hdr(ws, 10, j, h, bg=MID_BLUE)

    for i, row in detractors.reset_index(drop=True).iterrows():
        r = i + 11
        vals = [row["Ticker"], row["Sector"], row["Geography"],
                row["Actual P&L ($)"], row["Monthly Return (%)"]]
        fmts = ["@","@","@","#,##0.00",'0.00"%"']
        aligns = ["left","left","left","right","right"]
        for j, (val, fmt, aln) in enumerate(zip(vals, fmts, aligns), 1):
            c = _cell(ws, r, j, val, fmt=fmt, align=aln)
            c.fill = _fill("FDEDEC")
            if j == 4: c.font = Font(color=RED, bold=True, size=9)

    _set_widths(ws, {"A": 10, "B": 20, "C": 16, "D": 16, "E": 18})


# ─── MAIN ENTRY POINT ────────────────────────

def generate_pnl_report(summary, position_df, sector_df, geo_df, contributors, detractors, month_label):
    timestamp = datetime.today().strftime("%Y%m%d")
    safe_month = month_label.replace(" ", "_")
    filename = f"PnL_Attribution_{safe_month}_{timestamp}.xlsx"
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)

    # Write placeholder sheets
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        pd.DataFrame([summary]).to_excel(writer, sheet_name="Fund Summary",  index=False)
        position_df.to_excel(            writer, sheet_name="Positions",     index=False)
        sector_df.to_excel(              writer, sheet_name="Sector",        index=False)
        geo_df.to_excel(                 writer, sheet_name="Geography",     index=False)
        contributors.to_excel(           writer, sheet_name="Top Movers",    index=False)

    # Apply formatting
    wb = load_workbook(output_path)
    _write_summary(   wb["Fund Summary"], summary)
    _write_positions( wb["Positions"],    position_df)
    _write_attribution(wb["Sector"],     sector_df,  "SECTOR P&L ATTRIBUTION",    "Sector")
    _write_attribution(wb["Geography"],  geo_df,     "GEOGRAPHY P&L ATTRIBUTION", "Geography")
    _write_top_movers(wb["Top Movers"],  contributors, detractors)

    # Tab colors
    wb["Fund Summary"].sheet_properties.tabColor  = "1F2D3D"
    wb["Positions"].sheet_properties.tabColor     = "2E86C1"
    wb["Sector"].sheet_properties.tabColor        = "1E8449"
    wb["Geography"].sheet_properties.tabColor     = "D68910"
    wb["Top Movers"].sheet_properties.tabColor    = "C0392B"

    wb.save(output_path)
    return output_path

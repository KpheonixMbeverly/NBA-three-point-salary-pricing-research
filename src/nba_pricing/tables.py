"""Publication-oriented table (no title or SE lines; full SEs remain in CSV)."""
from pathlib import Path
import math
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from matplotlib.font_manager import findfont, FontProperties
from .constants import POSITIONS, PERIODS, KEY_TERMS, LABELS


def stars(p: float) -> str:
    if pd.isna(p):
        return ""
    return "***" if p < .01 else "**" if p < .05 else "*" if p < .10 else ""


def _write_centered(draw, text, font, center_x, y, color="#20242b"):
    width = draw.textbbox((0, 0), text, font=font)[2]
    draw.text((center_x - width / 2, y), text, font=font, fill=color)


def draw_poster_table(detailed: pd.DataFrame, summary: pd.DataFrame, output: str | Path,
                      include_playoff: bool = False) -> None:
    keys = list(KEY_TERMS) + (["PlayoffTierLag_roll3"] if include_playoff else [])
    periods_short = ["00–10", "11–15", "16–20", "21–25"]
    columns = [(p, e) for p in POSITIONS for e in PERIODS]
    coef_index = detailed.set_index(["Position", "Period", "Variable"])
    summary_index = summary.set_index(["Position", "Period"])
    rows = [(LABELS[k], k) for k in keys] + [("Observations", "N"),
                                             ("R²", "R2"), ("Adjusted R²", "Adj_R2")]

    f_regular = findfont("DejaVu Sans")
    f_bold = findfont(FontProperties(family="DejaVu Sans", weight="bold"))
    reg = ImageFont.truetype(f_regular, 24)
    bold = ImageFont.truetype(f_bold, 25)
    header = ImageFont.truetype(f_bold, 27)
    notes = ImageFont.truetype(f_regular, 18)
    margin = 18
    col_name = 390
    col_val = 151
    row_height = 39
    group_h = 40
    period_h = 43
    footer_h = 87
    width = margin*2 + col_name + len(columns)*col_val
    table_height = group_h+period_h+len(rows)*row_height
    height = margin*2 + table_height + footer_h
    img = Image.new("RGB", (width, height), "white")
    canvas = ImageDraw.Draw(img)
    xstart = margin + col_name
    top = margin
    canvas.line([(margin, top), (width-margin, top)], fill="#20242b", width=4)
    for k, p in enumerate(POSITIONS):
        mid = xstart + (k*4+2)*col_val
        _write_centered(canvas, p, header, mid, top+4)
    y = top+group_h
    canvas.line([(margin, y), (width-margin, y)], fill="#aeb4bc", width=2)
    canvas.text((margin+8, y+8), "Variable", font=bold, fill="#20242b")
    for k, col in enumerate(columns):
        _write_centered(canvas, periods_short[k%4], bold,
                        xstart + (k+.5)*col_val, y+8)
    y += period_h
    canvas.line([(margin,y), (width-margin,y)], fill="#303742", width=3)
    for ir, (label, key) in enumerate(rows):
        top_row = y + ir * row_height
        if ir == len(keys):
            canvas.line([(margin,top_row),(width-margin,top_row)],
                        fill="#707782", width=2)
        if ir % 2:
            canvas.rectangle([margin+1, top_row+1, width-margin-1, top_row+row_height-1],
                             fill="#f6f8fa")
        font = bold if key == "Skill_3P_roll3" else reg
        canvas.text((margin+8, top_row+6), label, font=font, fill="#20242b")
        for j, (p, e) in enumerate(columns):
            if key in keys:
                r = coef_index.loc[(p, e, key)]
                text = f"{r['Coefficient']:.3f}{stars(r['p_value'])}"
            else:
                r = summary_index.loc[(p, e)]
                text = str(int(r[key])) if key == "N" else f"{r[key]:.3f}"
            _write_centered(canvas, text, font, xstart+(j+.5)*col_val, top_row+6)
    bottom_y = y + len(rows)*row_height
    canvas.line([(margin,bottom_y),(width-margin,bottom_y)], fill="#20242b",width=4)
    for idx in [4,8]:
        xx=xstart+idx*col_val
        canvas.line([(xx,top),(xx,bottom_y)], fill="#9aa1ab", width=3)
    if include_playoff:
        msg = "DV: ln(salary / retained-sample mean salary). Lagged team playoff tier: requires verified input."
    else:
        msg = "DV: ln(salary / retained-sample mean salary). NearMax25 = 1 if salary / cap >= 25%."
    canvas.text((margin+6,bottom_y+14),msg,font=notes,fill="#454d5a")
    canvas.text((margin+6,bottom_y+46),
                "Player-clustered SE for significance: *** p<0.01, ** p<0.05, * p<0.10. SE omitted for display.",
                font=notes,fill="#454d5a")
    img.save(output)

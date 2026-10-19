"""Legacy analysis settings recovered from the supplied poster and code history.

The salary-cap numbers are historical inputs from the earlier analysis; see
DATA_DICTIONARY.md. They are NOT a replacement for a verified cap dataset.
"""
CAP_BY_SEASON_END = {
    2000: 34000000, 2001: 35500000, 2002: 42500000, 2003: 40271000,
    2004: 43840000, 2005: 43870000, 2006: 49500000, 2007: 53135000,
    2008: 55630000, 2009: 58680000, 2010: 57700000, 2011: 58044000,
    2012: 58044000, 2013: 58679000, 2014: 58679000, 2015: 63065000,
    2016: 70000000, 2017: 94143000, 2018: 99093000, 2019: 101869000,
    2020: 109140000, 2021: 109140000, 2022: 112414000, 2023: 123655000,
    2024: 136021000, 2025: 140588000,
}

POSITIONS = ("Guard", "Forward", "Center")
PERIODS = ("2000-2010", "2011-2015", "2016-2020", "2021-2025")
KEY_TERMS = (
    "Skill_3P_roll3", "Z_2P_made_roll3", "Z_2P_pct_roll3",
    "Skill_FT_roll3", "TRB_roll3", "AST_roll3", "STL_roll3",
    "BLK_roll3", "Age_c_roll3", "Age_c_sq_roll3",
    "TeamPressure_roll3", "NearMax25",
)
LABELS = {
    "Skill_3P_roll3": "3P composite index", "Z_2P_made_roll3": "2P makes (z)",
    "Z_2P_pct_roll3": "2P% (z)", "Skill_FT_roll3": "FT composite index",
    "TRB_roll3": "Rebounds", "AST_roll3": "Assists", "STL_roll3": "Steals",
    "BLK_roll3": "Blocks", "Age_c_roll3": "Centered age",
    "Age_c_sq_roll3": "Centered age squared", "TeamPressure_roll3": "Team salary pressure",
    "NearMax25": "Near-max (25% cap) proxy",
    "PlayoffTierLag_roll3": "Lagged team playoff tier (3y avg)",
}

TEAM_ABBR_ALIASES = {
    "CHO": "CHO", "CHA": "CHA", "CHH": "CHH", "NOH": "NOH", "NOK": "NOK",
    "NOP": "NOP", "NJN": "NJN", "BRK": "BRK", "SEA": "SEA", "OKC": "OKC",
    "VAN": "VAN", "MEM": "MEM",
}

"""
Central configuration for all constants used in the dash app.
"""

# Time conversions
HOURS_PER_PT = 8  # 8 hours equals 1 Person Tag (PT)
DAYS_PER_WEEK = 5  # Working days per week
DAYS_PER_MONTH = 22  # Average working days per month

# Chart dimensions
DEFAULT_GAUGE_HEIGHT = 140
DEFAULT_BAR_HEIGHT = 400
DEFAULT_PIE_HEIGHT = 400
DEFAULT_INDICATOR_HEIGHT = 100

# Chart margins
STANDARD_MARGINS = {"l": 20, "r": 20, "t": 40, "b": 20}
GAUGE_MARGINS = {"t": 25, "l": 50, "r": 50, "b": 0}
INDICATOR_MARGINS = {"t": 75, "l": 50, "r": 50, "b": 50}

# Color schemes
FAKTURA_COLOR = "#636EFA"  # Blue
WERTSCHOEPFEND_COLOR = "#00CC96"  # Green
NON_FAKTURA_COLOR = "#EF553B"  # Red
OTHER_COLOR = "#FFA15A"  # Orange

# Interval mappings for time aggregation
INTERVAL_CONVERSION = {
    "D": (1, "Tag"),
    "W": (DAYS_PER_WEEK, "Woche"),
    "ME": (DAYS_PER_MONTH, "Monat"),
}

# Required columns for data import
REQUIRED_COLUMNS = [
    "Auftrag/Projekt/Kst.",
    "Leistung",
    "ProTime-Datum",
    "Erfasste Menge",
    "Kurztext",
    "Positionsbezeichnung",
]

# Project code prefixes
FAKTURA_PROJECT_PREFIXES = ("K", "X")
WERTSCHOEPFEND_PROJECT_PREFIX = "K"

# Special project names
ALLGEMEIN_PROJECT = "Stunden - CONET Solutions GmbH"

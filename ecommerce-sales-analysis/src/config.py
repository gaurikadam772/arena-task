"""Project-wide constants: paths, schema, thresholds and chart colours."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = BASE_DIR / "data" / "sales_data.csv"

# Schema expected in the raw CSV
REQUIRED_COLUMNS = ["date", "product", "category", "quantity", "unit_price"]

# An order worth at least this much (USD) counts as "high-ticket"
HIGH_TICKET_THRESHOLD = 500

# Chart palette (single-series blue + neutral ink, light surface)
SURFACE = "#fcfcfb"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
BLUE = "#2a78d6"
# Sequential blue ramp (light -> dark) used by the heatmap
BLUE_RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

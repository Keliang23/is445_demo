"""Data preparation for the Illinois building inventory report."""
from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).parent / "data" / "building_inventory.csv"
SOURCE_URL = "https://raw.githubusercontent.com/UIUC-iSchool-DataViz/is445_data/main/building_inventory.csv"


def load_inventory(path=DATA_PATH):
    raw = pd.read_csv(path)
    data = raw.rename(columns={
        "Agency Name": "agency", "Bldg Status": "status",
        "Year Constructed": "year", "Square Footage": "area",
    }).copy()
    for col in ("agency", "status"):
        data[col] = data[col].astype("string").str.strip().fillna("Not provided")
        data[col] = data[col].replace("", "Not provided")
    for col in ("year", "area"):
        data[col] = pd.to_numeric(data[col], errors="coerce")
    # A recorded year of zero is unknown, not an actual construction date.
    data["year"] = data["year"].where(data["year"].between(1, 2026) & data["year"].mod(1).eq(0))
    # Nonpositive / nonfinite areas do not contribute to floor-area sums.
    data["area"] = data["area"].where(data["area"].gt(0) & data["area"].lt(float("inf")))
    return data


def agency_summary(data):
    return data.groupby("agency", as_index=False).agg(
        records=("agency", "size"), area=("area", "sum"),
        known_area=("area", "count"),
    )


def decade_summary(data, start, end):
    selected = data.loc[data["year"].between(start, end)].copy()
    selected["decade"] = (selected["year"] // 10 * 10).astype(int)
    counts = selected.groupby("decade").size()
    # Preserve empty decades so gaps do not collapse the time axis.
    result = counts.reindex(range(start // 10 * 10, end // 10 * 10 + 1, 10), fill_value=0)
    result = result.rename_axis("decade").reset_index(name="records")
    result["end"] = result["decade"] + 10
    result["label"] = result["decade"].astype(str) + "s"
    return result

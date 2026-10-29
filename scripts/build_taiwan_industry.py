"""Chapter 6 - Industry: how much each Taiwan manufacturing industry produces.

Source: Ministry of Economic Affairs industrial production index by industry
(data/original/Manufacturing Industry.xlsx), monthly, January 2004 - December 2024.
The index measures production volume, with 2021 = 100.
Output: docs/data/taiwan_industry.json (yearly averages)
"""
import json, re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "original" / "Manufacturing Industry.xlsx"
OUT = ROOT / "docs" / "data" / "taiwan_industry.json"
# Rows that add up several industries; shown separately from single industries
GROUPS = {"Manufacturing", "Metal and Machinery", "Information and Electronic", "Chemical", "Consumer Goods"}


def year_of(text):
    m = re.search(r"(\d+)年\s*(\d+)月", str(text))
    return int(m.group(1)) + 1911 if m else None


def main():
    df = pd.read_excel(SRC, sheet_name=0)
    df["year"] = df.iloc[:, 0].map(year_of)
    df = df.dropna(subset=["year"])                     # drops the notes at the bottom of the sheet
    names = [c for c in df.columns[1:] if c != "year" and not str(c).startswith("Unnamed")]
    values = df[names].apply(pd.to_numeric, errors="coerce")
    yearly = values.groupby(df["year"].astype(int)).mean().round(2)
    years = yearly.index.tolist()
    industries = []
    for col in names:
        s = yearly[col]
        if s.isna().all():
            continue
        name = str(col).strip()
        first, last = s.iloc[0], s.iloc[-1]
        industries.append({
            "name": name,
            "group": name in GROUPS,
            "index": [None if pd.isna(v) else float(v) for v in s],
            "change_pct": round((last / first - 1) * 100, 1) if pd.notna(first) and pd.notna(last) else None,
        })
    out = {"note": "Production index, 2021 = 100 (yearly average of monthly values).", "years": years, "industries": industries}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1))
    by = {i["name"]: i for i in industries}
    print(f"{len(industries)} industries, {years[0]}-{years[-1]}. "
          f"2024 manufacturing {by['Manufacturing']['index'][-1]}, computers {by.get('Computers, Electronic Products, and Optical Products', {}).get('index', [None])[-1]}")


if __name__ == "__main__":
    main()

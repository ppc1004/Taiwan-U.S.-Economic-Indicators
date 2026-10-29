"""Chapter 4 - Export orders, and Chapter 5 - Investment.

Sources (Taiwan Ministry of Economic Affairs), saved as CSV in data/original/csv/:
- export_orders.csv, export_orders_by_country.csv: orders foreign buyers placed with
  Taiwan companies (million USD). "China" here includes Hong Kong.
- outward_investment_by_region_1.csv / _2.csv: approved overseas investment, excluding
  mainland China, by region and top countries (million USD).
- taiwan_investment_in_china.csv: approved investment in mainland China (million USD, projects).
- foreign_investment_in_taiwan.csv, china_investment_in_taiwan.csv: approved investment into Taiwan.
Outputs: docs/data/taiwan_orders.json, docs/data/taiwan_investment.json (billion USD)
"""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "data" / "original" / "csv"
OUT = ROOT / "docs" / "data"


def read(name):
    return pd.read_csv(CSV / name, header=None, dtype=str)


def year_table(name):
    """Files with rows: year, amount (million USD), count."""
    df = read(name)
    df = df[pd.to_numeric(df[0], errors="coerce").notna()]
    return {int(float(r[0])): (float(r[1]), int(float(r[2]))) for r in df.itertuples(index=False)}


def b(x):
    return None if x is None or pd.isna(x) else round(float(x) / 1000, 3)


def orders():
    total = year_table("export_orders.csv")
    df = read("export_orders_by_country.csv")
    df = df[pd.to_numeric(df[0], errors="coerce").notna()]
    cols = {"us": 1, "japan": 5, "china_hk": 9, "asean": 13, "europe": 17}
    years = [int(float(y)) for y in df[0]]
    return {
        "note": "Orders foreign buyers placed with Taiwan companies. China includes Hong Kong.",
        "years": years,
        "total": [b(total[y][0]) for y in years],
        "markets": {k: [b(v) for v in pd.to_numeric(df[c])] for k, c in cols.items()},
    }


def investment():
    china = year_table("taiwan_investment_in_china.csv")
    into_tw = year_table("foreign_investment_in_taiwan.csv")
    china_in = year_table("china_investment_in_taiwan.csv")       # starts in 2015

    reg = read("outward_investment_by_region_1.csv")
    years = [int(float(y)) for y in reg.iloc[0, 1:]]
    regions = {}
    for _, r in reg.iloc[2:8].iterrows():          # amount rows (the count table comes after)
        regions[r[0].strip()] = dict(zip(years, pd.to_numeric(r[1:]).tolist()))

    top = read("outward_investment_by_region_2.csv")
    top_years = [int(float(y)) for y in top.iloc[0, 1:]]
    us_row = top[top[0].str.strip() == "美國"].iloc[0]
    us = dict(zip(top_years, pd.to_numeric(us_row[1:]).tolist()))

    years = sorted(set(years) & set(china))
    other = {y: sum(regions[k][y] for k in regions) for y in years}
    return {
        "note": "Approved investment. Overseas = all countries except mainland China.",
        "years": years,
        "china": [b(china[y][0]) for y in years],
        "china_projects": [china[y][1] for y in years],
        "other_countries": [b(other[y]) for y in years],
        "china_share": [round(china[y][0] / (china[y][0] + other[y]) * 100, 1) for y in years],
        "regions": {k: [b(v[y]) for y in years] for k, v in regions.items()},
        "us": [b(us.get(y)) if y in us else None for y in years],
        "into_taiwan": [b(into_tw[y][0]) for y in years],
        "china_into_taiwan": [b(china_in[y][0]) if y in china_in else None for y in years],
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    o, i = orders(), investment()
    (OUT / "taiwan_orders.json").write_text(json.dumps(o, indent=1))
    (OUT / "taiwan_investment.json").write_text(json.dumps(i, indent=1))
    print(f"Orders {o['years'][0]}-{o['years'][-1]}: 2024 U.S. {o['markets']['us'][-1]}B of {o['total'][-1]}B")
    print(f"Investment 2024: mainland China {i['china'][-1]}B ({i['china_share'][-1]}%), U.S. {i['us'][-1]}B")


if __name__ == "__main__":
    main()

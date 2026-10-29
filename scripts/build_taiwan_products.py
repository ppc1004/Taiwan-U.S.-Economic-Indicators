"""Chapter 3 - Products: what Taiwan sells to and buys from the U.S. and mainland China.

Source: data/original/taiwan_trade.xlsx, four product sheets (thousand USD),
January 2004 - December 2024. Product groups follow the HS customs code sections.
"China" means mainland China only. Hong Kong is not included.
Detailed export groups (18 HS sections) come from data/original/US Export.xlsx and
China Export.xlsx. Each is checked against the official table above before use.
(US Import.xlsx is not used: its column names do not line up with its numbers.)
Output: docs/data/taiwan_products.json (billion USD, by year)
"""
import json, re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "original" / "taiwan_trade.xlsx"
OUT = ROOT / "docs" / "data" / "taiwan_products.json"

SHEETS = {  # (partner, flow): sheet name
    ("us", "exports"): "美國出口", ("us", "imports"): "美國進口",
    ("cn", "exports"): "中國大陸出口", ("cn", "imports"): "中國大陸進口",
}
NAMES = {
    "出口": "total", "進口": "total",
    "機械及電機設備": "Machinery and electrical equipment",
    "光學及精密儀器；鐘錶；樂器": "Optical and precision instruments",
    "化學品": "Chemicals",
    "塑膠、橡膠及其製品": "Plastics and rubber",
    "基本金屬及其製品": "Base metals",
    "紡織品": "Textiles",
    "珠寶及貴金屬製品": "Jewelry and precious metals",
    "礦產品": "Minerals and fuels",
    "調製食品；飲料及菸酒": "Food, drinks and tobacco",
    "植物產品": "Plant products",
    "動物產品": "Animal products",
}


def year_of(text):
    m = re.search(r"(\d+)年\s*(\d+)月", str(text))
    return int(m.group(1)) + 1911 if m else None


def main():
    out = {"units": "billion USD", "note": "China = mainland China, not including Hong Kong.", "data": {}}
    for (partner, flow), sheet in SHEETS.items():
        df = pd.read_excel(SRC, sheet_name=sheet)
        df["year"] = df.iloc[:, 0].map(year_of)
        df = df.dropna(subset=["year"])
        cols = {c: NAMES[c] for c in df.columns if c in NAMES}
        yearly = df[list(cols)].apply(pd.to_numeric, errors="coerce").groupby(df["year"].astype(int)).sum() / 1e6
        yearly = yearly.rename(columns=cols).round(2)
        out["data"][f"{partner}_{flow}"] = {
            "years": yearly.index.tolist(),
            **{name: yearly[name].tolist() for name in yearly.columns},
        }
    # Detailed export groups, checked against the official table
    out["detailed_exports"] = {}
    for partner, fname in {"us": "US Export.xlsx", "cn": "China Export.xlsx"}.items():
        df = pd.read_excel(ROOT / "data" / "original" / fname, sheet_name=0)
        df["year"] = df.iloc[:, 0].map(year_of)
        df = df.dropna(subset=["year"])
        cats = [c for c in df.columns[1:] if c != "year" and not str(c).startswith("Unnamed")]
        yearly = df[cats].apply(pd.to_numeric, errors="coerce").groupby(df["year"].astype(int)).sum() / 1e6
        yearly.columns = [" ".join(str(c).replace("&amp;", "and").replace("&", "and").split()) for c in yearly.columns]
        official = out["data"][f"{partner}_exports"]
        check = {"Machinery and Electrical Equipment": "Machinery and electrical equipment",
                 "Optical and Precision Instruments": "Optical and precision instruments"}
        for detail_name, official_name in check.items():
            a, b = yearly[detail_name].round(2).tolist(), official[official_name]
            if any(abs(x - y) > 0.05 for x, y in zip(a, b)):
                raise ValueError(f"{fname}: {detail_name} does not match the official table")
        out["detailed_exports"][partner] = {
            "years": yearly.index.tolist(),
            **{c: yearly[c].round(3).tolist() for c in yearly.columns},
        }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    m = out["data"]["us_exports"]["Machinery and electrical equipment"][-1]
    print(f"Saved {OUT.name}. 2024 machinery exports to the U.S.: {m:.1f}B")


if __name__ == "__main__":
    main()

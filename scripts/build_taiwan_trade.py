"""Chapter 2 - Trade: Taiwan's trade with the U.S. and mainland China.

Source: Taiwan Ministry of Economic Affairs trade data (data/original/taiwan_trade.xlsx),
January 2004 - December 2024.
Units in the original file: total exports/imports in million USD,
U.S. and China columns in thousand USD. Everything is converted to billion USD here.
Note: "China" means mainland China only. Hong Kong is not included.
Output: docs/data/taiwan_trade.json
"""
import json, re
from pathlib import Path
import pandas as pd
from statsmodels.tsa.seasonal import STL

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "original" / "taiwan_trade.xlsx"
OUT = ROOT / "docs" / "data" / "taiwan_trade.json"


def roc_to_date(text):
    """'93年 1月' (Taiwan calendar) -> '2004-01'"""
    m = re.search(r"(\d+)年\s*(\d+)月", str(text))
    return f"{int(m.group(1)) + 1911}-{int(m.group(2)):02d}" if m else None


def main():
    raw = pd.read_excel(SRC, sheet_name=0)
    raw["date"] = raw.iloc[:, 0].map(roc_to_date)
    raw = raw.dropna(subset=["date"]).set_index("date")

    df = pd.DataFrame({
        "total_exp": raw["Total Export"] / 1e3,     # million -> billion
        "total_imp": raw["Total Import"] / 1e3,
        "us_exp": raw["USA Export"] / 1e6,          # thousand -> billion
        "us_imp": raw["USA Import"] / 1e6,
        "cn_exp": raw["China Export"] / 1e6,
        "cn_imp": raw["China Import"] / 1e6,
    }).astype(float)

    # Long-term trend: STL removes the seasonal pattern and short-term noise
    trend = {}
    for col in ["us_exp", "cn_exp"]:
        s = pd.Series(df[col].values, index=pd.period_range(df.index[0], periods=len(df), freq="M"))
        trend[col] = STL(s, period=12, robust=True).fit().trend.round(3).tolist()

    yearly = df.groupby(df.index.str[:4]).sum()
    annual = []
    for year, r in yearly.iterrows():
        annual.append({
            "year": int(year),
            "us_exp": round(r.us_exp, 2), "cn_exp": round(r.cn_exp, 2),
            "us_imp": round(r.us_imp, 2), "cn_imp": round(r.cn_imp, 2),
            "total_exp": round(r.total_exp, 2),
            "us_share": round(r.us_exp / r.total_exp * 100, 1),
            "cn_share": round(r.cn_exp / r.total_exp * 100, 1),
            "us_surplus": round(r.us_exp - r.us_imp, 2),
            "cn_surplus": round(r.cn_exp - r.cn_imp, 2),
        })

    monthly = [{"date": d, **{k: round(v, 3) for k, v in row.items()}} for d, row in df.iterrows()]
    out = {
        "source": "Taiwan Ministry of Economic Affairs, trade statistics",
        "units": "billion USD",
        "note": "China = mainland China, not including Hong Kong.",
        "monthly": monthly,
        "trend": trend,
        "annual": annual,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1))
    a = {x["year"]: x for x in annual}
    print(f"{len(monthly)} months. 2024 exports: U.S. {a[2024]['us_exp']:.1f}B, China {a[2024]['cn_exp']:.1f}B")


if __name__ == "__main__":
    main()

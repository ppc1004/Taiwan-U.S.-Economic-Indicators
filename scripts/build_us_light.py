"""Calculate the U.S. business cycle light with Taiwan's method.

Steps:
1. Turn each indicator into its change from the same month last year (the factory
   survey is used as is).
2. Give each indicator 1-5 points by comparing it with its own history.
3. Add up the 9 indicators (9-45 points) and pick the light using Taiwan's official bands.
Input: data/us_raw.csv   Output: docs/data/us_light.json (read by the website)
"""
import json, sys
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from indicators import INDICATORS, LIGHTS, BASE_START, BASE_END, PERCENTILES

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def light_for(score):
    return next(l for l in LIGHTS if score >= l["min"])


def main():
    raw = pd.read_csv(DATA / "us_raw.csv", index_col="date")
    raw["FACTORY_REAL"] = raw["AMTMVS"] / raw["PCUOMFGOMFG"]   # sales value / prices = sales volume

    values = pd.DataFrame(index=raw.index)
    for ind in INDICATORS:
        col = "FACTORY_REAL" if ind["key"] == "factory" else ind["fred"]
        s = raw[col]
        values[ind["key"]] = s.pct_change(12, fill_method=None) * 100 if ind["transform"] == "yoy" else s

    base = values.loc[BASE_START:BASE_END]
    cutoffs = {k: [round(float(base[k].quantile(p)), 2) for p in PERCENTILES] for k in values.columns}

    points = pd.DataFrame(index=values.index)
    for k, c in cutoffs.items():
        v = values[k]
        points[k] = (1 + (v > c[0]).astype(int) + (v > c[1]) + (v > c[2]) + (v > c[3])).where(v.notna())

    complete = points.dropna().loc[BASE_START:]
    months = []
    for date, row in complete.iterrows():
        score = int(row.sum())
        months.append({
            "date": date,
            "score": score,
            "light": light_for(score)["light"],
            "recession": bool(raw.loc[date, "USREC"] == 1) if pd.notna(raw.loc[date, "USREC"]) else False,
            "indicators": {k: {"value": round(float(values.loc[date, k]), 2), "points": int(row[k])} for k in cutoffs},
        })

    out = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "latest": months[-1],
        "method": {
            "base_period": [BASE_START, BASE_END],
            "percentiles": PERCENTILES,
            "lights": LIGHTS,
        },
        "indicators": [{**ind, "cutoffs": cutoffs[ind["key"]]} for ind in INDICATORS],
        "months": months,
    }
    path = ROOT / "docs" / "data" / "us_light.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():   # keep the old "updated" date if nothing actually changed
        old = json.loads(path.read_text())
        if old.get("months") == months and old.get("indicators") == out["indicators"]:
            print("No new data, nothing to update.")
            return
    path.write_text(json.dumps(out, indent=1))
    last = months[-1]
    print(f"{len(months)} months, {months[0]['date']} to {last['date']}. "
          f"Latest: {last['score']} points = {last['light']}")


if __name__ == "__main__":
    main()

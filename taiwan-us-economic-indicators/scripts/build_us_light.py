"""Build a U.S. business cycle light using Taiwan's (NDC) scoring method.

Taiwan's method: 9 indicators, each gets 1-5 points (blue .. red) based on
where its year-over-year growth falls between 4 cutoff values. Points are
added up (9-45) and the total maps to one of five lights:
  9-16 blue, 17-22 yellow-blue, 23-31 green, 32-37 yellow-red, 38-45 red.

Here the cutoffs for each U.S. indicator come from that indicator's own
history (percentiles). Two versions:
  - fixed:     cutoffs from the full history (easy to read, uses hindsight)
  - real_time: cutoffs from data available before each month only
               (no hindsight; this is the fair test for past recessions)
"""
import json
import pandas as pd
import numpy as np

RAW = "data/raw/fred_us_monthly.csv"

# (FRED id, short name, plain-English label, Taiwan counterpart, transform)
INDICATORS = [
    ("M2SL", "money", "Money supply (M2)", "Money supply (M1B)", "yoy"),
    ("SPASTT01USM661N", "stocks", "Stock prices", "Stock price index", "yoy"),
    ("INDPRO", "production", "Industrial production", "Industrial production index", "yoy"),
    ("AWOTMAN", "overtime", "Factory overtime hours", "Overtime hours", "yoy"),
    ("BOPGEXP", "exports", "Goods exports", "Customs exports", "yoy"),
    ("NEWORDER", "equipment", "Business equipment orders", "Machinery & electrical imports", "yoy"),
    ("AMTMVS", "factory_sales", "Factory sales", "Manufacturing sales", "yoy"),
    ("RSAFS", "retail", "Retail & restaurant sales", "Wholesale, retail & food sales", "yoy"),
    ("GACDFSA066MSFRBPHI", "survey", "Factory survey (Philadelphia Fed)", "Manufacturing business climate survey", "level"),
]
PCTS = [10, 25, 75, 90]          # 4 cutoffs -> 5 bands per indicator
LIGHTS = [(9, 16, "blue"), (17, 22, "yellow-blue"), (23, 31, "green"),
          (32, 37, "yellow-red"), (38, 45, "red")]
MIN_HISTORY = 120                # real-time version needs 10 years of history


def light_of(score):
    for lo, hi, name in LIGHTS:
        if lo <= score <= hi:
            return name
    return None


def band(value, cuts):
    # 1 = below 1st cutoff ... 5 = above 4th cutoff
    return int(np.searchsorted(cuts, value, side="right")) + 1


def main():
    raw = pd.read_csv(RAW)
    raw["date"] = pd.to_datetime(raw["date"])
    raw = raw.set_index("date")

    sig = pd.DataFrame(index=raw.index)
    for fid, key, *_rest, how in INDICATORS:
        s = raw[fid]
        sig[key] = (s / s.shift(12) - 1) * 100 if how == "yoy" else s
    keys = [k for _, k, *_ in INDICATORS]
    sig = sig.dropna(how="all")

    # fixed cutoffs from full history (months where all 9 exist)
    complete = sig.dropna()
    fixed_cuts = {k: np.percentile(complete[k], PCTS) for k in keys}

    rows = []
    for d, r in sig.iterrows():
        if r[keys].isna().any():
            continue
        row = {"date": d.strftime("%Y-%m"), "recession": int(raw.loc[d, "USREC"]) if not pd.isna(raw.loc[d, "USREC"]) else None}
        # fixed version
        pts = {k: band(r[k], fixed_cuts[k]) for k in keys}
        row["fixed_score"] = sum(pts.values())
        row["fixed_light"] = light_of(row["fixed_score"])
        row["fixed_points"] = pts
        # real-time version: cutoffs from complete months strictly before d
        past = complete[complete.index < d]
        if len(past) >= MIN_HISTORY:
            rt = {k: band(r[k], np.percentile(past[k], PCTS)) for k in keys}
            row["rt_score"] = sum(rt.values())
            row["rt_light"] = light_of(row["rt_score"])
            row["rt_points"] = rt
        row["values"] = {k: round(float(r[k]), 2) for k in keys}
        rows.append(row)

    out = {
        "method": {
            "percentiles": PCTS,
            "score_bands": LIGHTS,
            "min_history_months": MIN_HISTORY,
        },
        "indicators": [
            {"fred_id": f, "key": k, "label": lab, "taiwan_match": tw, "transform": how,
             "fixed_cutoffs": [round(float(x), 2) for x in fixed_cuts[k]]}
            for f, k, lab, tw, how in INDICATORS
        ],
        "months": rows,
    }
    with open("data/us_light.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"{len(rows)} months, {rows[0]['date']} to {rows[-1]['date']}")


if __name__ == "__main__":
    main()

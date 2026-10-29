"""Taiwan's official business cycle light, from the National Development Council.

Input: data/taiwan_ndc/lights.csv (downloaded by fetch_taiwan_light.py)
Output: docs/data/taiwan_light.json
"""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "taiwan_ndc" / "lights.csv"
OUT = ROOT / "docs" / "data" / "taiwan_light.json"
COLORS = {"紅": "red", "黃紅": "yellow-red", "綠": "green", "黃藍": "yellow-blue", "藍": "blue"}


def main():
    df = pd.read_csv(SRC, dtype=str)
    df["景氣對策信號"] = df["景氣對策信號"].str.strip()   # the source file has stray spaces, e.g. "黃藍 "
    df = df[df["景氣對策信號"].isin(COLORS)]
    months = [{
        "date": f"{r.Date[:4]}-{r.Date[4:6]}",
        "score": int(float(r.景氣對策信號綜合分數)),
        "light": COLORS[r.景氣對策信號],
    } for r in df.itertuples(index=False)]
    out = {"source": "National Development Council, Taiwan (data.gov.tw dataset 6099)", "latest": months[-1], "months": months}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1))
    print(f"Taiwan light: {len(months)} months, {months[0]['date']} to {months[-1]['date']}. "
          f"Latest {months[-1]['score']} = {months[-1]['light']}")


if __name__ == "__main__":
    main()

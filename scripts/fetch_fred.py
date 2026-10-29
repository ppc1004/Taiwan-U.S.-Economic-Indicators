"""Download the U.S. indicators from FRED and save them as one monthly table.

Uses FRED's public download link (no key needed). If the repo has a FRED_API_KEY
secret, the official API is used instead.
Output: data/us_raw.csv
"""
import io, os, sys, time, json, urllib.request
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from indicators import FRED_SERIES

START = "1990-01-01"
OUT = Path(__file__).resolve().parent.parent / "data" / "us_raw.csv"
HEADERS = {"User-Agent": "Mozilla/5.0 (taiwan-us-economic-indicators; github.com/ppc1004)"}


def get(url):
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode()
        except Exception as e:
            print(f"  retry {attempt + 1}: {e}")
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"Could not download {url}")


def fetch(series_id):
    key = os.environ.get("FRED_API_KEY")
    if key:
        url = ("https://api.stlouisfed.org/fred/series/observations"
               f"?series_id={series_id}&api_key={key}&file_type=json"
               f"&observation_start={START}&frequency=m&aggregation_method=avg")
        obs = json.loads(get(url))["observations"]
        s = pd.Series({o["date"]: o["value"] for o in obs})
    else:
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&fq=Monthly&fam=avg&cosd={START}"
        df = pd.read_csv(io.StringIO(get(url)))
        s = pd.Series(df.iloc[:, 1].values, index=df.iloc[:, 0].values)
    s = pd.to_numeric(s.replace(".", None), errors="coerce")
    s.index = pd.to_datetime(s.index).strftime("%Y-%m")
    return s


def main():
    table = {}
    for sid in FRED_SERIES:
        print(f"Downloading {sid}")
        table[sid] = fetch(sid)
    df = pd.DataFrame(table).sort_index()
    df.index.name = "date"
    OUT.parent.mkdir(exist_ok=True)
    df.to_csv(OUT)
    print(f"Saved {len(df)} months to {OUT} (latest month: {df.index[-1]})")


if __name__ == "__main__":
    main()

"""Download Taiwan's official business cycle indicators and lights.

Source: National Development Council, "景氣指標及燈號" on Taiwan's open data portal
(data.gov.tw dataset 6099), updated monthly. The data comes as a ZIP of CSV files.
Output: data/taiwan_ndc_raw.csv (the table that holds the monthly light and score)
"""
import io, json, time, urllib.request, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "taiwan_ndc_raw.csv"
API = "https://data.gov.tw/api/v2/rest/dataset/6099"
HEADERS = {"User-Agent": "Mozilla/5.0 (taiwan-us-economic-indicators; github.com/ppc1004)"}


def get(url):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=90) as r:
                return r.read()
        except Exception as e:
            print(f"  retry {attempt + 1}: {e}")
            time.sleep(10 * (attempt + 1))
    raise RuntimeError(f"Could not download {url}")


def decode(raw):
    for enc in ("utf-8-sig", "cp950", "big5"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    raise ValueError("Unknown text encoding")


def main():
    meta = json.loads(get(API))
    url = next(d["resourceDownloadUrl"] for d in meta["result"]["distribution"] if d["resourceFormat"].upper() == "ZIP")
    z = zipfile.ZipFile(io.BytesIO(get(url)))
    found = None
    for info in z.infolist():
        name = info.filename.encode("cp437").decode("cp950", errors="replace") if not info.flag_bits & 0x800 else info.filename
        print(f"In ZIP: {name} ({info.file_size} bytes)")
        if name.lower().endswith(".csv"):
            text = decode(z.read(info))
            if "景氣對策信號" in text[:3000] and found is None:
                found = text
    if found is None:
        raise RuntimeError("No CSV with the business cycle light was found in the ZIP")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(found, encoding="utf-8")
    lines = found.splitlines()
    print(f"Saved {len(lines) - 1} rows. Header: {lines[0][:200]}")
    print(f"Last row: {lines[-1][:200]}")


if __name__ == "__main__":
    main()

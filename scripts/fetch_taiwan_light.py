"""Download Taiwan's official business cycle indicators and lights.

Source: National Development Council, "景氣指標及燈號" on Taiwan's open data portal
(data.gov.tw dataset 6099), updated monthly. The data comes as a ZIP of CSV files.
Outputs: data/taiwan_ndc/lights.csv      (monthly light, total score and indexes)
         data/taiwan_ndc/components.csv  (the 9 indicators behind the light)
"""
import io, json, time, urllib.request, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "taiwan_ndc"
WANTED = {"景氣指標與燈號.csv": "lights.csv", "景氣對策信號構成項目.csv": "components.csv"}
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
    OUT.mkdir(parents=True, exist_ok=True)
    saved = []
    for info in z.infolist():
        name = info.filename
        if not info.flag_bits & 0x800:          # old ZIPs store names without saying which encoding
            raw = name.encode("cp437")
            for enc in ("utf-8", "cp950"):
                try:
                    name = raw.decode(enc)
                    break
                except UnicodeDecodeError:
                    pass
        base = name.split("/")[-1]
        print(f"In ZIP: {name} ({info.file_size} bytes)")
        if base in WANTED:
            text = decode(z.read(info))
            (OUT / WANTED[base]).write_text(text, encoding="utf-8")
            lines = text.splitlines()
            print(f"  saved as {WANTED[base]}: {len(lines) - 1} rows, last: {lines[-1][:120]}")
            saved.append(base)
    missing = set(WANTED) - set(saved)
    if missing:
        raise RuntimeError(f"Not found in ZIP: {missing}")

if __name__ == "__main__":
    main()

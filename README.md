# Taiwan & U.S. Economic Indicators

A website that shows where the Taiwan and U.S. economies are in the business cycle,
using the same five-color lights that Taiwan's National Development Council publishes every month.

The U.S. has no official version of these lights, so this project builds one by
applying Taiwan's method to 9 matching U.S. indicators from FRED.

## How it works

| Step | File |
|---|---|
| Download 9 U.S. indicators from FRED | `scripts/fetch_fred.py` |
| Score each indicator 1-5 and add them up (9-45 points) | `scripts/build_us_light.py` |
| Indicator list and Taiwan's official color bands | `scripts/indicators.py` |
| Runs every week on GitHub and saves new data | `.github/workflows/update.yml` |

All data is public and free. Results are saved in `data/`.

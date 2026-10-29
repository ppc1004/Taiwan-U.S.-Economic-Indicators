# Taiwan & U.S. Economic Indicators

A website that shows where the Taiwan and U.S. economies are in the business cycle,
using the same five-color lights that Taiwan's National Development Council publishes every month.

It shows Taiwan's official light next to a U.S. version. The U.S. has no official
version, so this project builds one by applying Taiwan's method to the 9 closest
matching U.S. indicators from FRED. It also covers Taiwan's trade, products,
export orders and overseas investment with the U.S. and mainland China.

Website: https://ppc1004.github.io/Taiwan-U.S.-Economic-Indicators/

## How it works

| Step | File |
|---|---|
| Download Taiwan's official light (National Development Council open data) | `scripts/fetch_taiwan_light.py`, `scripts/build_taiwan_light.py` |
| Download 9 U.S. indicators from FRED | `scripts/fetch_fred.py` |
| Score each indicator 1-5 and add them up (9-45 points) | `scripts/build_us_light.py` |
| Indicator list and Taiwan's official color bands | `scripts/indicators.py` |
| Trade, products, export orders and investment (Ministry of Economic Affairs data in `data/original/`) | `scripts/build_taiwan_trade.py`, `scripts/build_taiwan_products.py`, `scripts/build_taiwan_orders_investment.py` |
| The website | `docs/` |
| Runs every week on GitHub and saves new data | `.github/workflows/update.yml` |

All data is public and free. Results for the website are saved in `docs/data/`.

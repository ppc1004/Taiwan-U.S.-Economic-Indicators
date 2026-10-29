"""The 9 U.S. indicators, matched to the 9 indicators in Taiwan's business cycle lights."""

INDICATORS = [
    # key,        FRED series,           how we measure it,            Taiwan indicator it replaces
    {"key": "money",    "fred": "M2SL",               "transform": "yoy",   "name": "Money supply (M2)",                     "taiwan": "Money supply (M1B)"},
    {"key": "stocks",   "fred": "NASDAQCOM",          "transform": "yoy",   "name": "Stock prices (Nasdaq)",                 "taiwan": "Stock price index (TAIEX)"},
    {"key": "industry", "fred": "INDPRO",             "transform": "yoy",   "name": "Industrial production",                 "taiwan": "Industrial production"},
    {"key": "hours",    "fred": "AWOTMAN",            "transform": "yoy",   "name": "Factory overtime hours",                "taiwan": "Overtime hours (industry and services)"},
    {"key": "exports",  "fred": "BOPTEXP",            "transform": "yoy",   "name": "Exports of goods",                      "taiwan": "Customs exports"},
    {"key": "equipment","fred": "NEWORDER",           "transform": "yoy",   "name": "New orders for business equipment",     "taiwan": "Imports of machinery and electrical equipment"},
    {"key": "factory",  "fred": "AMTMVS/PCUOMFGOMFG", "transform": "yoy",   "name": "Factory sales, after price changes",    "taiwan": "Manufacturing sales volume"},
    {"key": "retail",   "fred": "RSAFS",              "transform": "yoy",   "name": "Retail and restaurant sales",           "taiwan": "Wholesale, retail and food service sales"},
    {"key": "survey",   "fred": "GACDFSA066MSFRBPHI", "transform": "level", "name": "Factory survey (Philadelphia Fed)",     "taiwan": "Manufacturing business climate survey"},
]

# Every FRED series we need to download (USREC = official U.S. recession months, for the chart only)
FRED_SERIES = ["M2SL", "NASDAQCOM", "INDPRO", "AWOTMAN", "BOPTEXP", "NEWORDER",
               "AMTMVS", "PCUOMFGOMFG", "RSAFS", "GACDFSA066MSFRBPHI", "USREC"]

# Taiwan's official total-score bands (9 indicators x 1-5 points = 9 to 45)
LIGHTS = [
    {"light": "red",         "label": "Red",         "meaning": "Overheating",    "min": 38},
    {"light": "yellow-red",  "label": "Yellow-red",  "meaning": "Warming up",     "min": 32},
    {"light": "green",       "label": "Green",       "meaning": "Stable",         "min": 23},
    {"light": "yellow-blue", "label": "Yellow-blue", "meaning": "Cooling down",   "min": 17},
    {"light": "blue",        "label": "Blue",        "meaning": "Slump",          "min": 9},
]

# Cutoffs for each indicator come from its own history in this period
BASE_START, BASE_END = "1993-02", "2019-12"   # ends before COVID so 2020-21 swings don't distort them
PERCENTILES = [0.10, 0.30, 0.70, 0.90]        # bottom 10% -> 1 point (blue) ... top 10% -> 5 points (red)

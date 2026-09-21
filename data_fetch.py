"""
Fetches game data from the College Football Data API (CFBD) and saves it
as a CSV under data/raw/.

Requires a .env file in the project root with:
    CFBD_API_KEY=your_key_here
"""

import os

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()  # reads .env in the project root

CFBD_API_KEY = os.getenv("CFBD_API_KEY")

if not CFBD_API_KEY:
    raise RuntimeError(
        "CFBD_API_KEY not found. Copy .env.example to .env and add your key "
        "(get one at https://collegefootballdata.com/key)."
    )

# Call the CFBD API using the key loaded from .env
YEARS = [2023, 2024, 2025]

BASE_URL = "https://api.collegefootballdata.com"
HEADERS = {
    "Authorization": f"Bearer {CFBD_API_KEY}",
    "Accept": "application/json",
}

all_games = []
for year in YEARS:
    response = requests.get(
        f"{BASE_URL}/games",
        headers=HEADERS,
        params={"year": year, "seasonType": "regular"},
        timeout=30,
    )
    response.raise_for_status()
    year_games = response.json()
    print(f"Fetched {len(year_games)} rows for {year}.")
    all_games.extend(year_games)

df = pd.DataFrame(all_games)
print(f"Total rows across {len(YEARS)} seasons: {len(df)}")

# Export the fetched data so teammates can work from a static file
os.makedirs("data/raw", exist_ok=True)
output_path = f"data/raw/cfbd_games_{min(YEARS)}_{max(YEARS)}.csv"
df.to_csv(output_path, index=False)

print(f"Saved to {output_path}")
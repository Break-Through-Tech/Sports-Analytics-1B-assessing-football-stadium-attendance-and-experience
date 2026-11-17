# Additional data sources for college football attendance project (2021–2025)

Place the original raw CSV files in `data/raw/` (or the repository’s agreed `data/` location). Do not overwrite originals.

| Files | Source | Notes |
|---|---|---|
| `football2021historicaldata.csv`, `football2022historicaldata.csv`, `cfbd_games_2023_2025.csv` | CollegeFootballData (CFBD) API: https://collegefootballdata.com/ | Game schedules, teams, venues, dates, attendance. 2023–2025 file uses lowercase/camel-case field names. |
| `betting2021.csv` through `betting2025.csv` | CFBD betting lines API | Includes spread, over/under, line provider; multiple providers/rows per game may occur. |
| `rankings2021.csv` through `rankings2025.csv` | CFBD rankings API | Includes AP Top 25 and Coaches Poll, **also other polls**; filter `Poll` to the desired types for modeling. |
| `recovered_weather_2021_2025_fbs.csv` | Open-Meteo Historical Weather API https://open-meteo.com/en/docs/historical-weather-api , using stadium geocoding and CFBD game dates | 4,333 / 4,412 FBS home games have matched weather. 79 unmatched; validate venue matches before use. Historical observed weather is not a pregame forecast. |
| `stadiums-geocoded.csv` | Existing stadium coordinates reference dataset | Verify its original provenance in your project before attributing. |
| `season_openers_2021_2025_candidates.csv` | Derived from the available CFBD game CSVs | First recorded game for each team each season; candidates need verification if game coverage is incomplete. |
| `rivalry_homecoming_events_template.csv` | Research template; no events verified yet | Add actual event dates and official athletics schedule/source URLs; avoid treating unverified rows as labels. |

## Remaining work
1. Verify rivalry and homecoming dates against official university athletics schedules and add source URLs.
2. Review season opener candidates for missing earlier games.
3. Upload CSVs and this README to the project branch under `data/`; link the PR in Issue #19.

Join game-level data using game IDs; rankings are season/week/team-level and betting lines may have multiple providers.

# Expanded Features Documentation (2021–2025) — Issue #20

## Generated Outputs
* **Master cleaned dataset:** `data/processed/expanded_fbs_games_2021_2025.csv` (3,905 rows, 69 columns; post-game leakage columns removed)
* **Encoded train/test splits:** `data/processed/features_expanded/train_features_expanded.csv` (3,099 rows, seasons 2021–2024) and `test_features_expanded.csv` (806 rows, season 2025)
* **Preprocessing artifacts:** `data/processed/features_expanded/preprocessor_expanded.joblib` and `feature_config_expanded.json`
* **Reproducible pipeline script:** `build_expanded_features.py`

---

## Cleaning & Harmonization Summary
* **Schema alignment (2021–2025):** Stripped UTF-8 BOMs (`\ufeff`) and normalized `PascalCase` columns in 2021–2022 game, betting, and ranking CSVs to match the `camelCase` 2023–2025 schema.
* **Filtering & stadium validation:** Applied the Notebook 01 rules across all 5 seasons (completed regular-season non-neutral FBS home games with reported attendance; mapped 20 team-name variants to `stadiums-geocoded.csv`; dropped UAB and relocated/wrong-stadium venues; corrected outdated capacities where median attendance > 110% of listed capacity; removed >125% outliers and capped turnout at `1.0`).
* **Target thresholds (train-only 2021–2024):** `low <= 0.671`, `0.671 < medium <= 0.940`, `high > 0.940`.

---

## Standardized Join Keys
| Column | Description |
| :--- | :--- |
| `game_id` | Integer CFBD game identifier (`id` / `Id`), primary key for games, betting, weather, and special events. |
| `season` | Integer regular season year (`2021`–`2025`). |
| `game_date` | Standardized UTC kickoff date (`YYYY-MM-DD`). |
| `home_team_std` / `away_team_std` | Lowercased, whitespace-normalized, punctuation-stripped team names used to join weekly rankings (`season`, `week`, `team_std`). |
| `venue_std` | Lowercased, quote-stripped stadium/venue name. |

---

## New Features & Missing-Value Handling
| Group | Column | Type | Definition & Missing-Value Rule |
| :--- | :--- | :--- | :--- |
| **Betting** | `betting_spread` | float | Consensus closing point spread (falls back to median across providers, then opening spread). Missing values imputed with train-set median inside `ColumnTransformer`. |
| **Betting** | `betting_spread_abs` | float | Absolute value of `betting_spread` (captures expected game competitiveness). |
| **Betting** | `betting_over_under` | float | Consensus closing over/under total (median fallback). Train-set median imputed. |
| **Betting** | `betting_missing` | int (0/1) | `1` if no betting line was matched for the game (0.5% of games). |
| **Rankings** | `is_ranked_home` | int (0/1) | `1` if home team appeared in FBS polls (priority: AP Top 25 > CFP Rankings > Coaches Poll; FCS polls excluded) for that `(season, week)`. |
| **Rankings** | `is_ranked_opponent` | int (0/1) | `1` if away team appeared in FBS polls for that `(season, week)`. |
| **Rankings** | `both_ranked` | int (0/1) | `1` if both home and away teams were ranked entering the game. |
| **Special Events** | `is_rivalry` | int (0/1) | `1` if matched to the curated known-rivalry list (`is_known_rivalry`). |
| **Special Events** | `is_rivalry_week_candidate` | int (0/1) | Heuristic flag (`1` for known rivalries in the home team's final regular-season week). |
| **Special Events** | `is_season_opener_home` | int (0/1) | `1` if the game is the home team's first observed regular-season game of that season. |
| **Special Events** | `homecoming_status` | category | `"verified_yes"` (33 games) or `"unknown"`. Per `SPECIAL_EVENTS_EXPANDED_VERIFICATION_NOTES.md`, blank values are preserved as `"unknown"` rather than filled with `0`. One-hot encoded for modeling. |
| **Conference** | `is_conference_game` | int (0/1) | `1` for conference matchups, `0` for non-conference matchups. |
| **Weather** | `weather_temp_c` | float | Kickoff-hour 2m temperature (°C) from Open-Meteo (`weather_status == "ok"` only). Train-set median imputed. |
| **Weather** | `weather_precip_mm` | float | Kickoff-hour precipitation (mm). Train-set median imputed. |
| **Weather** | `weather_humidity_pct` | float | Kickoff-hour relative humidity (%). Train-set median imputed. |
| **Weather** | `weather_wind_kmh` | float | Kickoff-hour 10m wind speed (km/h). Train-set median imputed. |
| **Weather** | `has_precipitation` | int (0/1) | `1` if `weather_precip_mm > 0.1` mm. |
| **Weather** | `weather_missing` | int (0/1) | `1` if Open-Meteo weather was unmatched/unavailable (0.5% of games). |

> **Note on Weather:** `recovered_weather_2021_2025_fbs.csv` contains historical observed weather at kickoff rather than pre-game forecast data.

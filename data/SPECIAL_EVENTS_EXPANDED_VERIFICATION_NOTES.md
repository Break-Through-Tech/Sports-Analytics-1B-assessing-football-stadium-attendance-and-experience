# Special events dataset — expanded verification notes

Dataset: `special_events_2021_2025_expanded_verification.csv`

## Coverage and limitations

- 4,412 FBS home-team games, seasons 2021–2025.
- 34 games positively identified as homecomings; 26 newly added in this verification pass.
- 153 known-rivalry candidates from the existing curated rivalry list; this is not an exhaustive national rivalry list.
- 84 `is_rivalry_week_candidate` flags: known-rivalry matchups occurring in the home team's last observed regular-season week. This is a **heuristic**, not an officially verified rivalry-week designation. The original `is_rivalry_week_verified` column remains unfilled where no direct evidence was found.
- `is_homecoming_verified` blank means **unknown**, not false. Do not fill blanks with 0 without additional evidence.
- `is_season_opener_*` fields are based on first observed games in available records, not independently verified complete schedules.

## Sources and methods

- Game identifiers, seasons, teams, dates and weeks: existing College Football Data API exports supplied by the project.
- Existing 8 positively identified homecoming games retained from prior version.
- 2025 Big Ten homecomings: https://fbschedules.com/big-ten-reveals-2025-homecoming-football-games-for-all-18-teams/ (conference announcement reported by FBSchedules; independently corroborated for Illinois and Maryland via university sources).
- Illinois 2025: https://d1iubivivot1gj.cloudfront.net/news/2024/12/11/big-ten-announces-2025-illinois-football-schedule
- Maryland 2025: https://umterps.com/news/2025/2/10/football-announces-theme-games-for-2025-season
- Clemson 2025: https://data.clemsontigers.com/pdf/football/2025-26/ClemsonSchedule.pdf
- BYU 2025: https://byucougars.com/news/2025/02/4/2025-football-schedule
- Stanford 2025: https://gostanford.com/news/2025/01/28/2025-football-schedule-announced
- Auburn 2025: https://auburntigers.com/sports/football/schedule/season/2025
- Tennessee 2025: https://utsports.com/news/2025/5/12/2025-football-game-designations-unveiled
- Missouri 2025: https://mutigers.com/sports/football/schedule/season/2025
- UConn 2024: https://uconnhuskies.com/sports/football/schedule/2024
- Missouri 2024: https://mutigers.com/sports/football/schedule/season/2024
- Colorado 2024: https://cubuffs.com/sports/football/schedule/2024
- Michigan 2024: https://mgoblue.com/sports/football/schedule/2024
- Penn State 2024: https://gopsusports.com/sports/football/schedule/season/2024

Each newly identified homecoming row includes a `homecoming_source_url`. Matches were made by season, exact home-team name, and exact away-team name; unmatched candidate records were not silently assigned.

## Remaining work

This dataset is **not a complete census of homecomings** for 2021–2025. More than 100 schools across five seasons require individual schedule/event verification. Additional official athletics sources and/or systematic schedule collection are required before claiming complete coverage. For modeling, preserve missing homecoming labels as unknown rather than treating them as confirmed non-homecoming games.

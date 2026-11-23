from __future__ import annotations

import json
import re
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
OUT_FEATURES_DIR = PROCESSED_DIR / "features_expanded"
OUT_FEATURES_DIR.mkdir(parents=True, exist_ok=True)

# Team-name mappings from Notebook 01 (games -> geocoded stadiums)
STADIUM_TEAM_MAPPING = {
    "App State": "Appalachian State",
    "Coastal Carolina": "Coastal Carolina Chanticleers",
    "Jacksonville State": "Jacksonville State Gamecocks",
    "James Madison": "James Madison Dukes",
    "Kennesaw State": "Kennesaw State Owls",
    "Liberty": "Liberty Flames",
    "Louisiana": "Louisiana-Lafayette",
    "Missouri State": "Missouri State Bears",
    "Sam Houston": "Sam Houston State Bearkats",
    "San José State": "San Jose State",
    "USC": "Southern California",
    "Ole Miss": "Mississippi",
    "UConn": "Connecticut",
    "Hawai'i": "Hawaii",
    "Massachusetts": "UMass",
    "Florida International": "FIU",
    "South Florida": "USF",
    "UL Monroe": "Louisiana-Monroe",
    "Northern Illinois": "NIU",
    "Delaware": "Delaware Fightin' Blue Hens",
}

TEAMS_IN_DIFFERENT_STADIUM = [
    "Georgia State",
    "Hawai'i",
    "UNLV",
    "San Diego State",
    "Colorado State",
    "South Alabama",
]

PASCAL_TO_CAMEL = {
    "Id": "id",
    "Season": "season",
    "Week": "week",
    "SeasonType": "seasonType",
    "StartDate": "startDate",
    "StartTimeTBD": "startTimeTBD",
    "Completed": "completed",
    "NeutralSite": "neutralSite",
    "ConferenceGame": "conferenceGame",
    "Attendance": "attendance",
    "VenueId": "venueId",
    "Venue": "venue",
    "HomeId": "homeId",
    "HomeTeam": "homeTeam",
    "HomeClassification": "homeClassification",
    "HomeConference": "homeConference",
    "HomePoints": "homePoints",
    "HomeLineScores": "homeLineScores",
    "HomePostgameWinProbability": "homePostgameWinProbability",
    "HomePregameElo": "homePregameElo",
    "HomePostgameElo": "homePostgameElo",
    "AwayId": "awayId",
    "AwayTeam": "awayTeam",
    "AwayClassification": "awayClassification",
    "AwayConference": "awayConference",
    "AwayPoints": "awayPoints",
    "AwayLineScores": "awayLineScores",
    "AwayPostgameWinProbability": "awayPostgameWinProbability",
    "AwayPregameElo": "awayPregameElo",
    "AwayPostgameElo": "awayPostgameElo",
    "ExcitementIndex": "excitementIndex",
    "Highlights": "highlights",
    "Notes": "notes",
}


def to_bool_series(s: pd.Series) -> pd.Series:
    return s.astype(str).str.strip().str.lower().map({"true": True, "1": True, "false": False, "0": False})


def standardize_text_key(s: pd.Series) -> pd.Series:
    return (
        s.fillna("")
        .astype(str)
        .str.replace('"', "", regex=False)
        .str.replace("'", "", regex=False)
        .str.replace("é", "e", regex=False)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", " ", regex=True)
    )


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = p2 - p1
    dlmb = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlmb / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


def load_and_clean_games() -> pd.DataFrame:
    frames = []
    for fname in ["football2021historicaldata.csv", "football2022historicaldata.csv"]:
        df = pd.read_csv(RAW_DIR / fname, encoding="utf-8-sig", low_memory=False)
        df.columns = [c.strip().strip('"') for c in df.columns]
        df = df.rename(columns=PASCAL_TO_CAMEL)
        frames.append(df)

    df_23_25 = pd.read_csv(RAW_DIR / "cfbd_games_2023_2025.csv", encoding="utf-8-sig", low_memory=False)
    frames.append(df_23_25)

    shared_cols = [c for c in df_23_25.columns if c in frames[0].columns]
    games = pd.concat([f[shared_cols] for f in frames], ignore_index=True)

    games["id"] = pd.to_numeric(games["id"], errors="coerce").astype("Int64")
    games = games.dropna(subset=["id"]).drop_duplicates(subset=["id"], keep="last").copy()
    games["id"] = games["id"].astype(int)

    for bcol in ["completed", "neutralSite", "conferenceGame", "startTimeTBD"]:
        games[bcol] = to_bool_series(games[bcol]).fillna(False)

    games["season"] = pd.to_numeric(games["season"], errors="coerce").astype(int)
    games["week"] = pd.to_numeric(games["week"], errors="coerce").astype(int)
    games["attendance"] = pd.to_numeric(games["attendance"], errors="coerce")
    games["homePregameElo"] = pd.to_numeric(games["homePregameElo"], errors="coerce")
    games["awayPregameElo"] = pd.to_numeric(games["awayPregameElo"], errors="coerce")
    games["startDate"] = pd.to_datetime(games["startDate"], utc=True, errors="coerce")
    games["venue"] = games["venue"].astype(str).str.replace('"', "", regex=False).str.strip()

    for col in games.select_dtypes(include=["object", "string"]).columns:
        games[col] = games[col].astype(str).str.strip().replace({"nan": np.nan, "": np.nan})

    print(f"Raw combined games (2021-2025): {len(games)}")

    # Filter to completed regular-season FBS home games with attendance (non-neutral)
    clean = games[
        (games["seasonType"].str.lower() == "regular")
        & (games["completed"])
        & (~games["neutralSite"])
        & (games["homeClassification"].str.lower() == "fbs")
        & (games["attendance"].notna())
        & (games["attendance"] > 0)
    ].copy()
    print(f"After FBS regular-season non-neutral attendance filter: {len(clean)}")

    # Merge geocoded stadium data
    stad = pd.read_csv(RAW_DIR / "stadiums-geocoded.csv", encoding="utf-8-sig")
    stad_info = stad[["team", "stadium", "capacity", "latitude", "longitude"]].rename(
        columns={"team": "stadium_team"}
    )
    clean["stadium_team"] = clean["homeTeam"].replace(STADIUM_TEAM_MAPPING)
    clean = clean.merge(stad_info, on="stadium_team", how="left")

    unmatched = clean.loc[clean["capacity"].isna(), "homeTeam"].value_counts()
    if len(unmatched):
        print("Unmatched stadium teams dropped:\n", unmatched.to_dict())
    clean = clean[clean["capacity"].notna()].copy()

    # Remove teams in wrong/relocated stadiums
    wrong_stadium = (
        clean["homeTeam"].isin(TEAMS_IN_DIFFERENT_STADIUM)
        | ((clean["homeTeam"] == "Northwestern") & (clean["venue"] != "Ryan Field"))
    )
    clean = clean[~wrong_stadium].copy()

    # Fix outdated capacities (median attendance > 110% of listed capacity)
    team_med = clean.groupby("homeTeam")["attendance"].transform("median")
    team_max = clean.groupby("homeTeam")["attendance"].transform("max")
    outdated = team_med > clean["capacity"] * 1.10
    clean["capacity_listed"] = clean["capacity"]
    clean.loc[outdated, "capacity"] = team_max[outdated]

    # Turnout rate & outlier cap
    clean["turnout_rate"] = clean["attendance"] / clean["capacity"]
    clean = clean[clean["turnout_rate"] <= 1.25].copy()
    clean["turnout_rate"] = clean["turnout_rate"].clip(upper=1.0)

    # Handle missing pregame Elo cleanly
    clean["awayElo_missing"] = clean["awayPregameElo"].isna().astype(int)
    min_away_elo = clean["awayPregameElo"].min()
    clean["awayPregameElo"] = clean["awayPregameElo"].fillna(min_away_elo)

    clean["homeElo_missing"] = clean["homePregameElo"].isna().astype(int)
    clean["homePregameElo"] = clean["homePregameElo"].fillna(clean["homePregameElo"].median())

    # Standardized join keys (Issue #20)
    clean["game_id"] = clean["id"]
    clean["game_date"] = clean["startDate"].dt.strftime("%Y-%m-%d")
    clean["home_team_std"] = standardize_text_key(clean["homeTeam"])
    clean["away_team_std"] = standardize_text_key(clean["awayTeam"])
    clean["venue_std"] = standardize_text_key(clean["venue"])

    clean = clean.drop(columns=["stadium_team"]).sort_values(["startDate", "id"]).reset_index(drop=True)
    print(f"Cleaned FBS home games (2021-2025): {len(clean)} | Seasons: {clean['season'].value_counts().sort_index().to_dict()}")
    return clean


def load_betting_features() -> pd.DataFrame:
    frames = []
    for yr in range(2021, 2026):
        df = pd.read_csv(RAW_DIR / f"betting{yr}.csv", encoding="utf-8-sig")
        df.columns = [c.strip().strip('"') for c in df.columns]
        frames.append(df)
    bet = pd.concat(frames, ignore_index=True)

    bet["game_id"] = pd.to_numeric(bet["Id"], errors="coerce")
    bet = bet.dropna(subset=["game_id"]).copy()
    bet["game_id"] = bet["game_id"].astype(int)

    for col in ["Spread", "OverUnder", "OpeningSpread", "OpeningOverUnder"]:
        bet[col] = pd.to_numeric(bet[col], errors="coerce")

    # Fill missing closing lines with opening lines from the same provider row if available
    bet["spread_val"] = bet["Spread"].fillna(bet["OpeningSpread"])
    bet["ou_val"] = bet["OverUnder"].fillna(bet["OpeningOverUnder"])
    bet["is_consensus"] = bet["LineProvider"].astype(str).str.strip().str.lower().eq("consensus")

    # Prefer consensus provider; otherwise median across all providers per game_id
    consensus = (
        bet[bet["is_consensus"]]
        .groupby("game_id", as_index=False)[["spread_val", "ou_val"]]
        .median()
        .rename(columns={"spread_val": "spread_cons", "ou_val": "ou_cons"})
    )
    all_prov = (
        bet.groupby("game_id", as_index=False)[["spread_val", "ou_val"]]
        .median()
        .rename(columns={"spread_val": "spread_med", "ou_val": "ou_med"})
    )

    merged = all_prov.merge(consensus, on="game_id", how="left")
    merged["betting_spread"] = merged["spread_cons"].fillna(merged["spread_med"])
    merged["betting_over_under"] = merged["ou_cons"].fillna(merged["ou_med"])
    return merged[["game_id", "betting_spread", "betting_over_under"]]


def load_rankings_features() -> pd.DataFrame:
    frames = []
    for yr in range(2021, 2026):
        df = pd.read_csv(RAW_DIR / f"rankings{yr}.csv", encoding="utf-8-sig")
        df.columns = [c.strip().strip('"') for c in df.columns]
        frames.append(df)
    rk = pd.concat(frames, ignore_index=True)

    rk = rk[rk["SeasonType"].astype(str).str.strip().str.lower() == "regular"].copy()
    # Keep FBS polls only (exclude FCS Coaches Poll, etc.)
    fbs_polls = {"AP Top 25": 1, "Playoff Committee Rankings": 2, "Coaches Poll": 3}
    rk = rk[rk["Poll"].isin(fbs_polls)].copy()
    rk["poll_priority"] = rk["Poll"].map(fbs_polls)

    rk["season"] = pd.to_numeric(rk["Season"], errors="coerce").astype(int)
    rk["week"] = pd.to_numeric(rk["Week"], errors="coerce").astype(int)
    rk["rank"] = pd.to_numeric(rk["Rank"], errors="coerce")
    rk["team_std"] = standardize_text_key(rk["School"])

    # Keep highest-priority poll rank per (season, week, team_std)
    rk = (
        rk.sort_values("poll_priority")
        .drop_duplicates(subset=["season", "week", "team_std"], keep="first")
        [["season", "week", "team_std", "rank"]]
    )
    return rk


def load_weather_features() -> pd.DataFrame:
    w = pd.read_csv(RAW_DIR / "recovered_weather_2021_2025_fbs.csv", encoding="utf-8-sig")
    w = w[w["weather_status"].astype(str).str.strip().str.lower() == "ok"].copy()
    w["game_id"] = pd.to_numeric(w["game_id"], errors="coerce").astype(int)
    w = w.drop_duplicates(subset=["game_id"], keep="first")

    rename_map = {
        "temperature_2m": "weather_temp_c",
        "precipitation": "weather_precip_mm",
        "relative_humidity_2m": "weather_humidity_pct",
        "wind_speed_10m": "weather_wind_kmh",
    }
    w = w.rename(columns=rename_map)
    for col in rename_map.values():
        w[col] = pd.to_numeric(w[col], errors="coerce")

    return w[["game_id"] + list(rename_map.values())]


def load_special_events() -> pd.DataFrame:
    se = pd.read_csv(RAW_DIR / "special_events_2021_2025_expanded_verification.csv", encoding="utf-8-sig")
    se["game_id"] = pd.to_numeric(se["game_id"], errors="coerce").astype(int)
    se = se.drop_duplicates(subset=["game_id"], keep="first")

    se["is_rivalry"] = pd.to_numeric(se["is_known_rivalry"], errors="coerce").fillna(0).astype(int)
    se["is_rivalry_week_candidate"] = (
        pd.to_numeric(se["is_rivalry_week_candidate"], errors="coerce").fillna(0).astype(int)
    )
    se["is_season_opener_home"] = (
        pd.to_numeric(se["is_season_opener_home_team"], errors="coerce").fillna(0).astype(int)
    )
    # Preserve blank as unknown per SPECIAL_EVENTS_EXPANDED_VERIFICATION_NOTES.md
    hc_num = pd.to_numeric(se["is_homecoming_verified"], errors="coerce")
    se["is_homecoming_verified"] = hc_num
    se["homecoming_status"] = np.where(hc_num == 1, "verified_yes", "unknown")

    return se[
        [
            "game_id",
            "is_rivalry",
            "is_rivalry_week_candidate",
            "is_season_opener_home",
            "is_homecoming_verified",
            "homecoming_status",
        ]
    ]


def engineer_all_features(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Join betting lines
    bet = load_betting_features()
    df = df.merge(bet, on="game_id", how="left")
    df["betting_missing"] = df["betting_spread"].isna().astype(int)
    df["betting_spread_abs"] = df["betting_spread"].abs()

    # 2. Join rankings (home and away)
    rk = load_rankings_features()
    df = df.merge(
        rk.rename(columns={"team_std": "home_team_std", "rank": "home_rank"}),
        on=["season", "week", "home_team_std"],
        how="left",
    )
    df = df.merge(
        rk.rename(columns={"team_std": "away_team_std", "rank": "away_rank"}),
        on=["season", "week", "away_team_std"],
        how="left",
    )
    df["is_ranked_home"] = df["home_rank"].notna().astype(int)
    df["is_ranked_opponent"] = df["away_rank"].notna().astype(int)
    df["both_ranked"] = ((df["is_ranked_home"] == 1) & (df["is_ranked_opponent"] == 1)).astype(int)

    # 3. Join weather
    weather = load_weather_features()
    df = df.merge(weather, on="game_id", how="left")
    df["weather_missing"] = df["weather_temp_c"].isna().astype(int)
    df["has_precipitation"] = (df["weather_precip_mm"].fillna(0) > 0.1).astype(int)

    # 4. Join special events (rivalry, homecoming, opener)
    se = load_special_events()
    df = df.merge(se, on="game_id", how="left")
    df["is_rivalry"] = df["is_rivalry"].fillna(0).astype(int)
    df["is_rivalry_week_candidate"] = df["is_rivalry_week_candidate"].fillna(0).astype(int)
    df["is_season_opener_home"] = df["is_season_opener_home"].fillna(0).astype(int)
    df["homecoming_status"] = df["homecoming_status"].fillna("unknown")

    # 5. Core pre-game features (matching Notebook 01)
    df["is_conference_game"] = df["conferenceGame"].astype(int)
    df["away_is_fcs"] = (df["awayClassification"].str.lower() != "fbs").astype(int)
    df["elo_diff"] = df["homePregameElo"] - df["awayPregameElo"]
    df["elo_abs_diff"] = df["elo_diff"].abs()

    # Local kickoff time features
    start = df["startDate"]
    nov1 = pd.to_datetime(start.dt.year.astype(str) + "-11-01", utc=True)
    dst_end = nov1 + pd.to_timedelta((6 - nov1.dt.dayofweek) % 7, unit="D") + pd.Timedelta(hours=9)
    dst_hours = ((start.dt.month >= 3) & (start < dst_end)).astype(int)
    local_time = start + pd.to_timedelta(df["longitude"] / 15 + dst_hours, unit="h")
    local_hour = local_time.dt.hour + local_time.dt.minute / 60
    local_dow = local_time.dt.dayofweek

    df["day_type"] = np.select(
        [local_dow == 5, local_dow == 4], ["saturday", "friday"], default="other_day"
    )
    df["kickoff_slot"] = np.select(
        [df["startTimeTBD"].astype(bool), local_hour < 13.5, local_hour < 17.5],
        ["unknown", "midday", "afternoon"],
        default="evening",
    )

    # Stadium & travel distance
    df["log_capacity"] = np.log1p(df["capacity"])
    team_loc = (
        df.groupby("homeId")[["latitude", "longitude"]]
        .median()
        .rename(columns={"latitude": "away_base_lat", "longitude": "away_base_lon"})
    )
    df = df.join(team_loc, on="awayId")
    df["away_travel_km"] = haversine_km(
        df["away_base_lat"], df["away_base_lon"], df["latitude"], df["longitude"]
    )
    df = df.drop(columns=["away_base_lat", "away_base_lon"])

    # Leakage-safe historical turnout features (strictly prior games)
    df = df.sort_values(["startDate", "id"]).reset_index(drop=True)
    by_home = df.groupby("homeId")["turnout_rate"]
    df["home_prior_turnout"] = by_home.transform(lambda s: s.shift(1).expanding().mean())
    last3 = by_home.transform(lambda s: s.shift(1).rolling(3, min_periods=1).mean())
    df["home_turnout_trend"] = last3 - df["home_prior_turnout"]
    df["home_prior_games"] = by_home.transform(lambda s: s.shift(1).expanding().count())

    df["_lift"] = df["turnout_rate"] - df["home_prior_turnout"]
    df["away_draw_lift_prior"] = df.groupby("awayId")["_lift"].transform(
        lambda s: s.shift(1).expanding().mean()
    )
    df = df.drop(columns=["_lift"])

    return df


def main():
    df = load_and_clean_games()
    df = engineer_all_features(df)

    # Diagnostics
    print("\n=== JOIN COVERAGE DIAGNOSTICS ===")
    print(f"Betting matched:        {(1 - df['betting_missing'].mean()) * 100:.1f}%")
    print(f"Weather matched:        {(1 - df['weather_missing'].mean()) * 100:.1f}%")
    print(f"Ranked home games:      {df['is_ranked_home'].sum()} ({df['is_ranked_home'].mean()*100:.1f}%)")
    print(f"Ranked opponent games:  {df['is_ranked_opponent'].sum()} ({df['is_ranked_opponent'].mean()*100:.1f}%)")
    print(f"Known rivalry games:    {df['is_rivalry'].sum()} ({df['is_rivalry'].mean()*100:.1f}%)")
    print(f"Verified homecomings:   {(df['homecoming_status'] == 'verified_yes').sum()}")
    print(f"Conference games:       {df['is_conference_game'].sum()} ({df['is_conference_game'].mean()*100:.1f}%)")

    # Save clean expanded master file (strictly excluding post-game leakage columns)
    post_game_cols = [
        "homePoints", "awayPoints", "homeLineScores", "awayLineScores",
        "homePostgameWinProbability", "awayPostgameWinProbability",
        "homePostgameElo", "awayPostgameElo", "excitementIndex",
    ]
    clean_export = df.drop(columns=[c for c in post_game_cols if c in df.columns])
    master_path = PROCESSED_DIR / "expanded_fbs_games_2021_2025.csv"
    clean_export.to_csv(master_path, index=False)
    print(f"\nSaved master cleaned dataset -> {master_path} ({clean_export.shape})")

    # Build model-ready train (2021-2024) / test (2025) feature matrices
    numeric_features = [
        "week",
        "is_conference_game",
        "away_is_fcs",
        "homePregameElo",
        "elo_diff",
        "elo_abs_diff",
        "log_capacity",
        "latitude",
        "longitude",
        "away_travel_km",
        "home_prior_turnout",
        "home_turnout_trend",
        "home_prior_games",
        "away_draw_lift_prior",
        # New Issue #20 numeric features
        "betting_spread",
        "betting_spread_abs",
        "betting_over_under",
        "betting_missing",
        "is_ranked_home",
        "is_ranked_opponent",
        "both_ranked",
        "is_rivalry",
        "is_rivalry_week_candidate",
        "is_season_opener_home",
        "weather_temp_c",
        "weather_precip_mm",
        "weather_humidity_pct",
        "weather_wind_kmh",
        "has_precipitation",
        "weather_missing",
    ]
    categorical_features = ["day_type", "kickoff_slot", "homeConference", "homecoming_status"]
    all_features = numeric_features + categorical_features

    test_season = int(df["season"].max())
    train_df = df[df["season"] < test_season].copy()
    test_df = df[df["season"] == test_season].copy()

    q1, q2 = train_df["turnout_rate"].quantile([1 / 3, 2 / 3])
    y_train = np.select([train_df["turnout_rate"] <= q1, train_df["turnout_rate"] <= q2], [0, 1], default=2)
    y_test = np.select([test_df["turnout_rate"] <= q1, test_df["turnout_rate"] <= q2], [0, 1], default=2)

    preprocessor = ColumnTransformer(
        [
            ("num", SimpleImputer(strategy="median"), numeric_features),
            (
                "conf",
                OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=30, sparse_output=False),
                ["homeConference"],
            ),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                ["day_type", "kickoff_slot", "homecoming_status"],
            ),
        ],
        verbose_feature_names_out=False,
    )
    preprocessor.set_output(transform="pandas")

    X_train = preprocessor.fit_transform(train_df[all_features])
    X_test = preprocessor.transform(test_df[all_features])

    assert not X_train.isna().any().any(), "NaNs found in X_train!"
    assert not X_test.isna().any().any(), "NaNs found in X_test!"

    trace_cols = ["game_id", "season", "game_date", "home_team_std", "away_team_std", "venue_std"]
    X_train.assign(
        target=y_train,
        turnout_rate=train_df["turnout_rate"].values,
        **{c: train_df[c].values for c in trace_cols},
    ).to_csv(OUT_FEATURES_DIR / "train_features_expanded.csv", index=False)

    X_test.assign(
        target=y_test,
        turnout_rate=test_df["turnout_rate"].values,
        **{c: test_df[c].values for c in trace_cols},
    ).to_csv(OUT_FEATURES_DIR / "test_features_expanded.csv", index=False)

    joblib.dump(preprocessor, OUT_FEATURES_DIR / "preprocessor_expanded.joblib")

    config = {
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "class_labels": {"0": "low", "1": "medium", "2": "high"},
        "low_max": float(q1),
        "medium_max": float(q2),
        "train_seasons": sorted(train_df["season"].unique().tolist()),
        "test_season": test_season,
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "output_columns": list(X_train.columns),
    }
    with open(OUT_FEATURES_DIR / "feature_config_expanded.json", "w") as f:
        json.dump(config, f, indent=2)

    print(f"Saved encoded features -> {OUT_FEATURES_DIR}")
    print(f"X_train: {X_train.shape} | X_test: {X_test.shape}")
    print(f"Thresholds (train-only): low <= {q1:.3f} < medium <= {q2:.3f} < high")


if __name__ == "__main__":
    main()

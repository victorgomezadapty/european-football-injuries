# Public source schema and aggregate data dictionary

The registered original CSV has 11 columns. This public dictionary describes the source fields without republishing any person's row or example values. Original data: Sanan Muzaffarov, European Football Injuries (2020–2025), Kaggle version 2, CC BY-SA 4.0. Typed conversions and aggregate analysis by Víctor Andrés Gómez López (2026).

| Exact source column | Canonical field | Type and unit | Interpretation |
| --- | --- | --- | --- |
| Season | season | String | Source season context; not day-by-day absence allocation |
| Injury | injury_type_raw | String | Recorded injury, illness or other absence label |
| Days | reported_days_out | Integer parsed from text with day suffix | Reported duration, retained separately from calculated duration |
| Games missed | games_missed | Integer, matches | Reported missed matches; competition and eligibility coverage unverified |
| injury_from_parsed | injury_start | Explicit US month/day/year date | Recorded onset, not independently verified clinical onset |
| injury_until_parsed | injury_end | Explicit US month/day/year date | Recorded endpoint, not independently verified medical clearance |
| player_name | player_name | String | Recorded name; no verified identity or birth date |
| player_age | age_recorded | Numeric, years | Recorded age; effective date unverified |
| player_position | position | String | Detailed source position; effective date unverified |
| club | club | String | Source context; may repeat an interval across clubs |
| league | league | String | Source league context; no exposure denominator |

All 15,603 source durations equal exclusive date difference plus one day. Both reported and calculated durations remain separate in local analytical outputs. Obtain the original rows from the credited source rather than this public derivative release.

## Aggregate fields

`injury_burden.csv` uses one row per trimmed raw absence label, preserving case. `injury_count` is retained record frequency. `unique_recorded_names` counts exact-name surrogates, not verified identities. `valid_days_count` and `valid_games_count` are metric-specific sample sizes. `median_days_out`, `mean_days_out`, `max_days_out`, `p25_days_out`, `p75_days_out`, `p90_days_out`, `p95_days_out` and `iqr_days_out` summarize reported episode durations in days. `total_days_out` sums episode-days; `total_games_missed` sums reported match losses. `median_games_missed` is a per-record summary.

These sums may double count repeated or overlapping records. Candidate sensitivity keeps the first source row per matching name, normalized label and date interval; it does not adjudicate an independent clinical episode or the correct club. Other tables use the same definitions grouped by league, source season or position. The records-per-name distribution contains aggregate counts, without names or histories.

No field is an availability percentage, incidence rate, clinical prognosis or prospective injury probability. See the methodology, availability definition, data license and scientific discussion for provenance and limits.

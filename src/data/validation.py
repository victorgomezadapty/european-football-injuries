import pandas as pd
from .clean_data import text


def quality_flags(df, as_of):
    flags = pd.DataFrame(index=df.index)
    for col in ['reported_days_out','games_missed','age_recorded','injury_start','injury_end']:
        flags[col + '_parse_failure'] = text(df[col + '_source']).notna() & df[col].isna()
    flags['missing_player'] = df.player_id.isna()
    flags['missing_injury_type'] = df.injury_type_raw.isna()
    flags['missing_start'] = df.injury_start.isna()
    flags['missing_end'] = df.injury_end.isna()
    flags['end_before_start'] = df.calculated_days_out.lt(0)
    flags['negative_reported_days'] = df.reported_days_out.lt(0)
    flags['negative_games_missed'] = df.games_missed.lt(0)
    flags['noninteger_reported_days'] = df.reported_days_out.mod(1).ne(0) & df.reported_days_out.notna()
    flags['noninteger_games_missed'] = df.games_missed.mod(1).ne(0) & df.games_missed.notna()
    flags['zero_reported_days'] = df.reported_days_out.eq(0)
    flags['zero_games_missed'] = df.games_missed.eq(0)
    flags['duration_above_365_days_review'] = df.reported_days_out.gt(365)
    flags['age_outside_12_60_review'] = ~df.age_recorded.between(12,60) & df.age_recorded.notna()
    flags['start_after_analysis_date'] = df.injury_start.gt(as_of)
    flags['end_after_analysis_date'] = df.injury_end.gt(as_of)
    flags['duration_discrepancy_beyond_one_day'] = df.duration_difference.abs().gt(1)
    for col in ['exact_duplicate','exact_duplicate_member','potential_duplicate_episode','same_day_player_records']:
        flags[col] = df[col]
    return flags.fillna(False).astype(bool)


def missingness(raw):
    return pd.DataFrame([{'column': c, 'missing_count': int(text(raw[c]).isna().sum()),
                          'missing_pct': float(text(raw[c]).isna().mean()*100),
                          'unique_nonmissing': int(text(raw[c]).nunique()),
                          'source_dtype': str(raw[c].dtype)} for c in raw])

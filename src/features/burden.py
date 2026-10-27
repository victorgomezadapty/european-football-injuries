import pandas as pd


def summarize_burden(df, by):
    """Episode sums; no exposure denominator or unique-absence interpretation."""
    grouped = df.groupby(by, dropna=False, observed=True)
    result = grouped.agg(injury_count=('event_id','size'),
        unique_recorded_names=('player_id','nunique'),
        valid_days_count=('days_out','count'), median_days_out=('days_out','median'),
        mean_days_out=('days_out','mean'), max_days_out=('days_out','max'),
        valid_games_count=('games_missed_valid','count'),
        median_games_missed=('games_missed_valid','median')).reset_index()
    for column, dest in [('days_out','total_days_out'),('games_missed_valid','total_games_missed')]:
        totals=grouped[column].sum(min_count=1).rename(dest).reset_index()
        result=result.merge(totals,on=by,how='left',validate='one_to_one')
    for percentile in [.25,.75,.9,.95]:
        result=result.merge(grouped.days_out.quantile(percentile).rename(f'p{int(percentile*100)}_days_out').reset_index(),on=by,how='left',validate='one_to_one')
    result['iqr_days_out'] = result.p75_days_out - result.p25_days_out
    return result.sort_values('injury_count',ascending=False,kind='stable')

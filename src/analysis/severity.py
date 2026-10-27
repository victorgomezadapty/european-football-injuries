def numeric_distribution(df):
    return df[['age_recorded','reported_days_out','calculated_days_out','games_missed']].describe(
        percentiles=[.01,.25,.5,.75,.9,.95,.99]).rename_axis('statistic').reset_index()

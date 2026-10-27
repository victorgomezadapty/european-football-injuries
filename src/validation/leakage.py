POST_ONSET_OR_FULL_HISTORY = {
    'days_out','reported_days_out','calculated_days_out','injury_end','games_missed',
    'games_missed_valid','total_days_out','total_games_missed','median_days_out','max_days_out',
    'career_injury_count_in_dataset','recorded_interval_union_days',
    'same_label_after_recorded_end_count','days_since_previous_injury','previous_injury_end',
}


def assert_onset_features(columns):
    forbidden=POST_ONSET_OR_FULL_HISTORY.intersection(columns)
    if forbidden:
        raise ValueError(f'Post-onset/full-history features require exclusion or timing audit: {sorted(forbidden)}')
    # Passing this guard does not establish that all remaining fields were known at onset.

def recurrence_summary(events):
    """Repeated recorded labels are not confirmed clinical reinjuries."""
    usable=events[events.injury_start.notna() & events.player_id.notna() & events.injury_label_key.notna()]
    return usable.groupby('injury_label_key',dropna=False).agg(
        dated_labeled_events=('event_id','size'),
        repeated_same_label_events=('previous_same_injury_count',lambda s:int(s.gt(0).sum())),
        same_label_after_recorded_end_events=('same_label_after_recorded_end_count',lambda s:int(s.gt(0).sum())),
        players_with_label=('player_id','nunique')).reset_index().sort_values('repeated_same_label_events',ascending=False)

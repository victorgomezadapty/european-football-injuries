def assert_prior_dates(history):
    comparable=history.previous_injury_date.notna() & history.injury_start.notna()
    if not (history.loc[comparable,'previous_injury_date'] < history.loc[comparable,'injury_start']).all():
        raise AssertionError('Previous injury dates must be strictly before the current onset.')

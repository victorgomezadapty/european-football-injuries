from ..features.burden import summarize_burden


def calendar_burden(events):
    return summarize_burden(events, 'injury_month').sort_values('injury_month')

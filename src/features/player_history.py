from collections import Counter
import pandas as pd


def build_history(events):
    """Counts use strictly earlier starts. End-date gaps remain retrospective."""
    result=events.copy()
    counts=['previous_injury_count','previous_same_injury_count','same_label_after_recorded_end_count']
    for c in counts:
        result[c]=pd.Series(pd.NA,index=result.index,dtype='Int64')
    result['previous_injury_date']=pd.NaT
    result['previous_injury_end']=pd.NaT
    result['days_since_previous_injury']=pd.Series(pd.NA,index=result.index,dtype='Float64')
    result['overlaps_any_prior_record']=pd.Series(pd.NA,index=result.index,dtype='boolean')
    dated=result[result.player_id.notna() & result.injury_start.notna()]
    for _,player in dated.groupby('player_id',sort=False):
        prior_count=0
        prior_labels=Counter()
        ended_by_label={}
        previous_date=pd.NaT
        previous_end=pd.NaT
        maximum_end=pd.NaT
        for date,batch in player.sort_values(['injury_start','source_row']).groupby('injury_start',sort=True):
            # Batch ties: no artificial order among events on the same day.
            for idx,row in batch.iterrows():
                label=row.injury_label_key
                result.at[idx,'previous_injury_count']=prior_count
                if pd.notna(label):
                    result.at[idx,'previous_same_injury_count']=prior_labels[label]
                    result.at[idx,'same_label_after_recorded_end_count']=sum(end < date for end in ended_by_label.get(label,[]))
                result.at[idx,'previous_injury_date']=previous_date
                result.at[idx,'previous_injury_end']=previous_end
                if pd.notna(previous_end):
                    result.at[idx,'days_since_previous_injury']=(date-previous_end).days
                result.at[idx,'overlaps_any_prior_record']=bool(pd.notna(maximum_end) and date <= maximum_end)
            prior_count+=len(batch)
            for _,row in batch.iterrows():
                if pd.notna(row.injury_label_key):
                    prior_labels[row.injury_label_key]+=1
                    if pd.notna(row.injury_end) and row.injury_end >= date:
                        ended_by_label.setdefault(row.injury_label_key,[]).append(row.injury_end)
            previous_date=date
            # Latest-start tie has no unique previous event. Gap is deliberately unavailable.
            previous_end=batch.iloc[0].injury_end if len(batch)==1 and pd.notna(batch.iloc[0].calculated_days_out) and batch.iloc[0].calculated_days_out>=0 else pd.NaT
            valid_ends=batch.loc[batch.calculated_days_out.ge(0),'injury_end']
            if len(valid_ends) and pd.notna(valid_ends.max()):
                maximum_end=max(maximum_end,valid_ends.max()) if pd.notna(maximum_end) else valid_ends.max()
    return result


def interval_union_days(player):
    """Union of closed recorded date intervals, matching the observed inclusive convention."""
    valid=player[player.calculated_days_out.ge(0) & player.injury_start.notna() & player.injury_end.notna()]
    total=0
    start=end=None
    for row in valid.sort_values('injury_start').itertuples():
        row_start=row.injury_start.date().toordinal()
        row_end=row.injury_end.date().toordinal()+1
        if end is None:
            start,end=row_start,row_end
        elif row_start <= end:
            end=max(end,row_end)
        else:
            total+=end-start
            start,end=row_start,row_end
    return total + (end-start if end is not None else 0) if len(valid) else pd.NA


def player_profiles(events):
    from .burden import summarize_burden
    valid=events[events.player_id.notna()]
    profiles=summarize_burden(valid,['player_id','player_name']).rename(columns={'injury_count':'career_injury_count_in_dataset'})
    rows=[]
    for player_id,p in valid.groupby('player_id',sort=False):
        rows.append({'player_id':player_id,
            'recorded_interval_union_days':interval_union_days(p),
            'valid_interval_count':int((p.calculated_days_out.ge(0)).sum()),
            'repeated_same_label_events':int(p.previous_same_injury_count.gt(0).sum()),
            'same_label_after_recorded_end_events':int(p.same_label_after_recorded_end_count.gt(0).sum()),
            'overlapping_prior_events':int(p.overlaps_any_prior_record.sum()),
            'first_recorded_start':p.injury_start.min(),'last_recorded_end':p.injury_end.max()})
    return profiles.merge(pd.DataFrame(rows),on='player_id',how='left',validate='one_to_one')

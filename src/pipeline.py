"""Rebuild Milestone 1 from the checksum-verified Kaggle CSV."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import json
import platform
import sys
import numpy as np
import pandas as pd
from .data.load_data import load_raw
from .data.clean_data import clean_data, text
from .data.validation import quality_flags, missingness
from .features.burden import summarize_burden
from .features.injury_features import draft_taxonomy
from .features.player_history import build_history, player_profiles
from .features.recurrence import recurrence_summary
from .analysis.epidemiology import frequencies
from .analysis.severity import numeric_distribution
from .analysis.temporal import calendar_burden
from .validation.temporal import assert_prior_dates

ROOT=Path(__file__).resolve().parents[1]


def write_csv(table,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    table.to_csv(path,index=False,encoding='utf-8',date_format='%Y-%m-%d')


def md(table,columns=None,n=10):
    t=table[columns] if columns else table
    def cell(v):
        if pd.isna(v): return 'Unavailable'
        if isinstance(v,(float,np.floating)): return f'{v:,.1f}'
        return str(v).replace('|','/').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(t.columns)+' |','| '+' | '.join(['---']*len(t.columns))+' |']+
                     ['| '+' | '.join(cell(v) for v in row)+' |' for row in t.head(n).itertuples(index=False,name=None)])


def run(root=ROOT,as_of='2026-10-26',figures=True):
    root=Path(root)
    as_of=pd.Timestamp(as_of)
    raw,manifest=load_raw(root)
    clean,mapping=clean_data(raw)
    flags=quality_flags(clean,as_of)
    tables=root/'reports/tables'
    tables.mkdir(parents=True,exist_ok=True)
    (root/'docs').mkdir(exist_ok=True)
    (root/'handoff').mkdir(exist_ok=True)
    write_csv(clean,root/'data/interim/injury_records_standardized.csv')
    events=build_history(clean.loc[~clean.exact_duplicate].copy())
    assert_prior_dates(events)
    write_csv(events,root/'data/processed/injury_events.csv')
    profiles=player_profiles(events)
    write_csv(profiles,root/'data/processed/player_burden_profiles.csv')
    write_csv(profiles,tables/'player_burden_profiles.csv')
    write_csv(missingness(raw),tables/'missingness.csv')
    write_csv(flags.sum().rename_axis('check').reset_index(name='flagged_rows'),tables/'quality_summary.csv')
    write_csv(pd.concat([clean[['event_id','source_row']],flags],axis=1),tables/'row_quality_flags.csv')
    write_csv(clean.loc[flags.any(axis=1)],tables/'records_for_review.csv')
    write_csv(clean.loc[clean.exact_duplicate_member],tables/'exact_duplicates.csv')
    write_csv(clean.loc[clean.potential_duplicate_episode],tables/'potential_duplicate_episodes.csv')
    write_csv(clean.loc[clean.duration_difference.notna()].groupby('duration_difference').size().rename('record_count').reset_index(),tables/'duration_comparison.csv')
    write_csv(clean.loc[clean.duration_difference.abs().gt(1)],tables/'duration_discrepancies.csv')
    write_csv(numeric_distribution(events),tables/'numeric_distributions.csv')
    taxonomy=draft_taxonomy(events.injury_type_raw)
    write_csv(taxonomy,tables/'injury_taxonomy_draft.csv')
    variants=taxonomy[taxonomy.duplicated('normalization_key',keep=False)].sort_values('normalization_key')
    write_csv(variants,tables/'label_normalization_variants.csv')
    burdens={}
    for key in ['injury_type_raw','position','age_recorded','age_group','league','season','club']:
        write_csv(frequencies(events,key),tables/f'distribution_{key}.csv')
        burdens[key]=summarize_burden(events,key)
        write_csv(burdens[key],tables/f'burden_by_{key}.csv')
    write_csv(summarize_burden(events,['league','season']),tables/'burden_by_league_season.csv')
    write_csv(summarize_burden(events,['club','season']),tables/'burden_by_club_season.csv')
    for metric in ['injury_count','median_days_out','total_days_out','total_games_missed']:
        ranking=burdens['injury_type_raw'].sort_values([metric,'injury_type_raw'],ascending=[False,True])
        write_csv(ranking,tables/f'injury_ranking_{metric}.csv')
    write_csv(frequencies(profiles,'career_injury_count_in_dataset').sort_values('career_injury_count_in_dataset'),tables/'injuries_per_player_distribution.csv')
    recurrence=recurrence_summary(events)
    write_csv(recurrence,tables/'recurrence_by_label.csv')
    write_csv(events[['event_id','player_id','player_name','injury_type_raw','injury_start','injury_end','previous_injury_date','previous_injury_end','days_since_previous_injury','previous_injury_count','previous_same_injury_count','same_label_after_recorded_end_count','overlaps_any_prior_record']],tables/'player_event_sequences.csv')
    gaps=events.loc[events.days_since_previous_injury.notna(),['event_id','player_name','days_since_previous_injury','overlaps_any_prior_record']]
    write_csv(gaps,tables/'inter_record_gaps.csv')
    write_csv(gaps[['days_since_previous_injury']].describe(percentiles=[.25,.5,.75,.9,.95]).rename_axis('statistic').reset_index(),tables/'inter_record_gap_distribution.csv')
    temporal=calendar_burden(events)
    write_csv(temporal,tables/'calendar_month_burden.csv')
    identity=events.groupby(['player_id','player_name']).agg(record_count=('event_id','size'),min_age=('age_recorded','min'),max_age=('age_recorded','max'),clubs=('club','nunique'),leagues=('league','nunique')).reset_index()
    write_csv(identity,tables/'name_identity_audit.csv')
    # Sensitivity only. Same name/label/dates can be transfer-related repeated records.
    episode_key=['player_id','injury_start','injury_end','injury_label_key']
    complete=events[episode_key].notna().all(axis=1)
    candidate=pd.concat([events.loc[complete].drop_duplicates(episode_key),events.loc[~complete]]).sort_values('source_row')
    candidate=build_history(candidate)
    candidate_profiles=player_profiles(candidate)
    write_csv(candidate,root/'data/processed/candidate_episodes_sensitivity.csv')
    write_csv(candidate_profiles,tables/'player_profiles_candidate_sensitivity.csv')
    write_csv(recurrence_summary(candidate),tables/'recurrence_candidate_sensitivity.csv')
    write_csv(summarize_burden(candidate,'injury_type_raw'),tables/'injury_burden_candidate_sensitivity.csv')
    sensitivity=pd.DataFrame([{'cohort':name,'record_count':len(d),'total_days_out':d.days_out.sum(min_count=1),
        'total_games_missed':d.games_missed_valid.sum(min_count=1),
        'players_with_multiple_records':int(p.career_injury_count_in_dataset.gt(1).sum()),
        'repeated_same_label_events':int(d.previous_same_injury_count.gt(0).sum())}
        for name,d,p in [('source_records_exact_deduplicated',events,profiles),('candidate_episode_collapsed_sensitivity',candidate,candidate_profiles)]])
    write_csv(sensitivity,tables/'duplicate_sensitivity.csv')
    joined=events[episode_key+['event_id','club','season','reported_days_out','games_missed']].copy()
    duplicate_groups=joined.loc[complete].groupby(episode_key,dropna=False).agg(
        record_count=('event_id','size'),club_count=('club','nunique'),season_count=('season','nunique'),
        reported_days_values=('reported_days_out','nunique'),games_missed_values=('games_missed','nunique')).reset_index()
    write_csv(duplicate_groups[duplicate_groups.record_count.gt(1)],tables/'duplicate_episode_group_audit.csv')
    date_spans={c:{'min':str(clean[c].min().date()) if clean[c].notna().any() else None,
                   'max':str(clean[c].max().date()) if clean[c].notna().any() else None} for c in ['injury_start','injury_end']}
    summary={
        'raw_rows':len(raw),'raw_columns':len(raw.columns),'analysis_records':len(events),
        'unique_recorded_player_names':int(events.player_id.nunique()),'clubs':int(events.club.nunique()),
        'leagues':sorted(events.league.dropna().unique().tolist()),'seasons':sorted(events.season.dropna().unique().tolist()),
        'positions':sorted(events.position.dropna().unique().tolist()),'raw_injury_labels':int(raw[mapping['injury_type_raw']].nunique()),
        'dates':date_spans,'reported_total_days_out':float(events.days_out.sum(min_count=1)),
        'reported_total_games_missed':float(events.games_missed_valid.sum(min_count=1)),
        'median_reported_days_out':float(events.days_out.median()),
        'median_reported_games_missed':float(events.games_missed_valid.median()),
        'players_with_multiple_records':int(profiles.career_injury_count_in_dataset.gt(1).sum()),
        'players_with_repeated_same_label':int(profiles.repeated_same_label_events.gt(0).sum()),
        'potential_duplicate_rows':int(clean.potential_duplicate_episode.sum()),
        'candidate_episode_count_sensitivity':len(candidate),'as_of':str(as_of.date()),
        'scope':'Milestone 1. No survival modeling, prediction or external-data integration.'}
    (root/'reports/dataset_summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    run_info={'generated_at_utc':datetime.now(timezone.utc).isoformat(),'python':platform.python_version(),
              'executable':sys.executable,'pandas':pd.__version__,'numpy':np.__version__,
              'source_csv_sha256':manifest['files'][0]['sha256'],'parameters':{'as_of':str(as_of.date()),'figures':figures},
              'record_policy':'Exclude exact whole-row duplicates only; retain flagged candidate duplicates.',
              'source_to_canonical':mapping}
    (root/'reports/run_manifest.json').write_text(json.dumps(run_info,indent=2)+'\n',encoding='utf-8')
    dictionary=[]
    for c in raw:
        canonical=next((k for k,v in mapping.items() if v==c),'unmapped')
        dictionary.append({'raw_column':c,'raw_type':'UTF-8 string on ingestion','canonical_column':canonical,
            'parsed_dtype':str(clean[canonical].dtype) if canonical in clean else 'unmapped',
            'missing_count':int(text(raw[c]).isna().sum()),'unique_nonmissing':int(text(raw[c]).nunique()),
            'example':str(raw[c].iloc[0])})
    dictionary=pd.DataFrame(dictionary)
    write_csv(dictionary,tables/'data_dictionary.csv')
    (root/'docs/data_dictionary.md').write_text('# Data dictionary\n\nVerified from the manifest-registered CSV. Original file is immutable. `_source` columns preserve each original field before typed conversion.\n\n'+md(dictionary,n=len(dictionary))+'\n\n`Days` is parsed as a nonnegative integer number of days. Reported values remain in `reported_days_out`; valid analysis values are in `days_out`. `calculated_days_out = injury_end - injury_start` is exclusive.\n\n`player_age` is retained as `age_recorded`: its exact timing has not been independently established. It must not be assumed to be known at injury onset. `player_id` hashes the exact normalized player name; same-name people cannot be distinguished and alternate spellings are not merged.\n\nSee `handoff/feature_catalog.csv` for derived fields and `methodology.md` for exclusions, missingness, identity and date conventions.\n',encoding='utf-8')
    if figures:
        from .visualization.injury_plots import bar_chart,burden_matrix,distributions,temporal_plot,position_heatmap,age_plot
        from .visualization.player_timelines import plot_timelines
        directory=root/'reports/figures'
        injury=burdens['injury_type_raw']
        for metric,title,xlabel,name in [
            ('injury_count','Which absence labels are recorded most often?','Recorded events','top_injury_frequency'),
            ('total_days_out','Which labels account for the greatest reported time loss?','Reported episode-days summed','top_time_loss_burden'),
            ('total_games_missed','Which labels account for the greatest match loss?','Reported missed matches summed','top_match_loss_burden')]:
            bar_chart(injury,'injury_type_raw',metric,title,xlabel,directory,name)
        burden_matrix(injury,directory)
        distributions(events,directory)
        temporal_plot(temporal,directory)
        position_heatmap(events,directory)
        age_plot(events,directory)
        examples=plot_timelines(events,profiles,directory)
        write_csv(examples,tables/'example_player_timelines.csv')
    write_report(root,summary,burdens,flags,profiles,sensitivity,recurrence,events)
    print(json.dumps(summary,indent=2,ensure_ascii=True))
    return summary


def write_report(root,s,burdens,flags,profiles,sensitivity,recurrence,events):
    injury=burdens['injury_type_raw']
    severity=injury.sort_values('median_days_out',ascending=False)
    supported=severity[severity.valid_days_count.ge(20)]
    quality=flags.sum().rename_axis('check').reset_index(name='flagged_rows')
    dates=s['dates']
    total_days=s['reported_total_days_out']
    reduction=100*(1-sensitivity.iloc[1].total_days_out/total_days) if total_days else 0
    top_frequency=injury.iloc[0]
    top_days=injury.sort_values('total_days_out',ascending=False).iloc[0]
    top_games=injury.sort_values('total_games_missed',ascending=False).iloc[0]
    report=f'''# Milestone 1 — Injury Dataset & Burden Understanding

Status: completed for review. Analysis date: {s['as_of']}. Stop here before Phase 2.

## Verified dataset dimensions and coverage

The official Kaggle version 2 CSV contains **{s['raw_rows']:,} rows × {s['raw_columns']} columns**, {s['unique_recorded_player_names']:,} distinct recorded player names, {s['clubs']} club labels, {len(s['leagues'])} league labels and {s['raw_injury_labels']} raw absence labels. These counts are computed from the file; player names are not verified identity IDs.

Injury starts span **{dates['injury_start']['min']} to {dates['injury_start']['max']}**. Recorded ends span **{dates['injury_end']['min']} to {dates['injury_end']['max']}**. Ends extend beyond the 2024/25 season; the dataset title is not an observation cutoff or censoring date.

Seasons: {', '.join(s['seasons'])}. Leagues: {', '.join(s['leagues'])}.

There are {len(s['positions'])} position labels. Complete club, position, age, league and season inventories are in `reports/tables/distribution_*.csv`.

## What does one row represent?

One row is a recorded player injury **or other reason for absence** with club/season context. Illness, quarantine, fitness and rest appear alongside musculoskeletal labels. A row is not a healthy-player observation, exposure unit, confirmed new injury, or prospectively monitored clinical episode.

The primary analysis retains {s['analysis_records']:,} records after excluding exact whole-row duplicates. Different-club records can describe the same interval. All headlines below are record-level totals; they should not be described as counts of independently confirmed clinical injuries.

## Data quality, dates and duration conventions

{md(quality,n=len(quality))}

All observed reported durations equal `(end - start) + 1`. This is consistent with inclusive calendar-date counting. The original `Days` field is never overwritten. Both exclusive calculated days and the difference from reported days are exported. An end date is a recorded endpoint, not independently verified medical clearance or first match return.

Missingness, zero values, parsing errors and extreme durations are checked separately. Durations above 365 days are retained and flagged for review, not assigned a severity class or deleted. The longest recorded duration is {events.days_out.max():,.0f} days. No severe-injury threshold is imposed.

**{s['potential_duplicate_rows']:,} rows** share name, normalized label and dates with another record, despite differing context or other fields. Candidate collapsing yields {s['candidate_episode_count_sensitivity']:,} rows and reduces summed days by {reduction:.1f}%:

{md(sensitivity,n=2)}

Candidate collapsing keeps the earliest source row for sensitivity only. It does not establish an authoritative club or merge conflicting match counts. Check `duplicate_episode_group_audit.csv` for conflicts before interpreting its totals. Exact duplicates and candidate duplicates have separate exports.

## What injuries are most frequent?

The most frequent recorded label is **{top_frequency.injury_type_raw}**, with {top_frequency.injury_count:,} records. Raw label counts include medical and non-injury reasons for absence.

{md(injury,['injury_type_raw','injury_count','median_days_out','total_days_out','total_games_missed'])}

![Recorded frequency](figures/top_injury_frequency.png)

## What injuries create the greatest time-loss burden?

**{top_days.injury_type_raw}** accounts for the greatest summed reported time loss ({top_days.total_days_out:,.0f} episode-days). Across all records the sum is **{s['reported_total_days_out']:,.0f} episode-days**. This is an episode sum; repeated and overlapping records can count the same calendar day more than once.

{md(injury.sort_values('total_days_out',ascending=False),['injury_type_raw','injury_count','median_days_out','total_days_out'])}

![Time-loss burden](figures/top_time_loss_burden.png)

Continuous reported time loss has median {events.days_out.median():.0f} days, IQR {events.days_out.quantile(.25):.0f}–{events.days_out.quantile(.75):.0f}, mean {events.days_out.mean():.1f}, P90 {events.days_out.quantile(.9):.0f} and P95 {events.days_out.quantile(.95):.0f} days. Every label has mean, median, IQR, percentiles, maxima and nonmissing sample size in the severity table.

Highest median durations across **all labels**, including rare categories:

{md(severity,['injury_type_raw','injury_count','median_days_out','p25_days_out','p75_days_out'])}

For a more stable descriptive comparison, labels with at least 20 valid durations are shown below. This is a reporting support filter, not a clinical cutoff. Small categories remain in all exports and burden totals.

{md(supported,['injury_type_raw','injury_count','median_days_out','p25_days_out','p75_days_out'])}

## Which injuries create the greatest match-loss burden?

**{top_games.injury_type_raw}** leads in reported match loss ({top_games.total_games_missed:,.0f} matches summed). The overall record-level sum is **{s['reported_total_games_missed']:,.0f}**, with median {s['median_reported_games_missed']:.0f} per record. This cannot be converted to a proportion of eligible fixtures, and overlapping episodes may count a match repeatedly.

{md(injury.sort_values('total_games_missed',ascending=False),['injury_type_raw','injury_count','median_games_missed','total_games_missed'])}

![Match-loss burden](figures/top_match_loss_burden.png)

## Frequency, severity and burden together

![Injury burden matrix](figures/injury_burden_matrix.png)

Each bubble is a source label; its area increases with summed games missed. Reference lines split the observed medians across labels and have no clinical meaning. Frequent, shorter absences and rare, longer absences imply different rehabilitation planning demands. These are descriptive resource-planning signals, not intervention effects or individual risk estimates.

## Burden by position, league and season

Position:

{md(burdens['position'],['position','injury_count','median_days_out','total_days_out','total_games_missed'],n=30)}

League:

{md(burdens['league'],['league','injury_count','median_days_out','total_days_out','total_games_missed'])}

Season label:

{md(burdens['season'].sort_values('season'),['season','injury_count','median_days_out','total_days_out','total_games_missed'])}

Season and club totals use the source context, not day-by-day allocation to the season when each absence day occurred. Injuries spanning seasons, loans and transfers require additional attribution work. Raw differences reflect dataset coverage, player mix and recording as well as injury patterns. Position counts do not estimate position-specific risk.

Recorded age is summarized continuously and in descriptive bands <=20, 21–25, 26–30, 31–35, 36+. The event-weighted age median is {events.age_recorded.median():.0f}, range {events.age_recorded.min():.0f}–{events.age_recorded.max():.0f}. These summaries overweight frequently recorded players and do not represent all league squads. No biological causal effect is inferred.

![Age and duration](figures/age_duration.png)

![Position injury mix](figures/position_injury_mix.png)

## How heterogeneous are player injury histories?

**{s['players_with_multiple_records']:,} of {s['unique_recorded_player_names']:,} names** have multiple records. Record counts per name range from {profiles.career_injury_count_in_dataset.min()} to {profiles.career_injury_count_in_dataset.max()}, with median {profiles.career_injury_count_in_dataset.median():.0f}. **{s['players_with_repeated_same_label']:,} names** have a later record with the same case/whitespace-normalized label.

The profiles include cumulative reported days and games, median/max duration, repeated-label events, date coverage and the union of recorded inclusive intervals. The union avoids counting overlapping date intervals twice; it remains a count of recorded absence dates and has no availability denominator.

{md(profiles.sort_values('total_days_out',ascending=False),['player_name','career_injury_count_in_dataset','total_days_out','total_games_missed','recorded_interval_union_days'])}

This selection highlights large recorded burdens for illustration, not a clinical ranking or claim about current fitness.

## Initial recurrence and event sequences

{md(recurrence,n=10)}

Same-label repetition uses strictly earlier start dates; same-day records do not create an artificial event order. The additional `same_label_after_recorded_end_count` requires a previous same-label interval with its recorded end strictly before the new onset. Neither confirms reinjury, anatomical side, injury mechanism, or clinical recovery.

`days_since_previous_injury` is current onset minus the end of the latest-start earlier record. Negative values flag overlap; zero is a shared endpoint. Ties in the preceding onset make that gap unavailable. This retrospective gap can depend on future-known end dates and is not automatically safe at onset. Candidate-collapsed history and recurrence are exported separately.

![Example histories](figures/player_injury_timelines.png)

Examples are selected deterministically by the largest record counts, then player name. Bars represent source records. Unshaded periods have no recorded absence; they do not establish availability.

## Calendar patterns

![Calendar event distribution](figures/monthly_recorded_events.png)

The calendar table counts onsets by month and assigns each episode's full reported burden to its onset month. It does not measure actual days unavailable in that month. Coverage at the edges and changing activity can affect counts. No compressed-schedule or World Cup effect is established without contextual/exposure data.

## What does this dataset tell us about availability?

It supports recorded event counts, episode duration distributions, cumulative reported time loss, reported matches missed, repeated-label histories and interval unions. These form a **Recorded Availability Burden Profile**. They describe documented absence consequences among players who appear in the file.

## What can it NOT tell us about availability?

It cannot establish an availability percentage, true healthy-day intervals, games available, or all eligible player-seasons. Missing denominators include registration/squad membership intervals, eligibility, complete club fixture schedules, competitions included, transfer intervals and a reliable observation window for every player. The first/last injury date must not be used as the observation denominator. No `player_availability` percentage is computed.

## Why can we not estimate true injury incidence from this dataset alone?

There are no match/training player-hours or healthy-player exposure records. Injury counts divided by the number of injured players in this file would not estimate incidence in the league population. More records in a position or league do not imply greater individual risk. Historical associations do not establish future injury predictions.

## Initial taxonomy and future leakage

Raw labels remain the primary analytical categories. `injury_taxonomy_draft.csv` inventories every observed label, proposed broad group, normalization key and review status. Case variants are listed separately. Vague symptoms are left unresolved; anatomical-region recurrence is deferred until the mapping and laterality are reviewed.

Post-onset outcomes include reported/calculated duration, games missed, injury end and future recurrence. Full-history player totals also leak future information when assigned to an earlier injury. Previous counts use earlier starts, but knowledge of those records at that time is not verified. Age, position, club, league and diagnosis timing also require audit. See `docs/leakage_audit.md` and the feature catalog.

## Which external data would most improve the analysis?

Verified player IDs and transfer/registration intervals would improve identity and context first. Fixture schedules, eligibility and competition definitions would support missed-match reconciliation and eventually availability denominators. Training and match player-hours would be needed for exposure-based incidence; match minutes alone omit training exposure. Medical clearance and return-to-training dates would improve endpoint interpretation. No external rows have been integrated.

## What should Phase 2 investigate?

1. Review same-interval repeated records, club attribution and player-name identity.
2. Validate the taxonomy with clinical input, keeping symptoms, illness and non-injury absence distinct.
3. Audit whether recorded ends represent return or expected dates, and establish observation cutoffs/censoring before any time-to-return analysis.
4. After review, consider selected well-supported recovery curves with confidence intervals and repeated-player dependence addressed.
5. Scope external exposure joins and an onset-feature timing audit before any modeling. No prospective injury-risk model is justified by the current file alone.

## Reproducibility and sources

Run `python -m src.pipeline --as-of {s['as_of']}` from the project root. The pipeline verifies the raw CSV checksum, writes derived data separately and generates this report. See `reports/run_manifest.json` and `data/raw/manifest.json`.

Source: Sanan Muzaffarov, [European Football Injuries (2020–2025), Kaggle version 2](https://www.kaggle.com/datasets/sananmuzaffarov/european-football-injuries-2020-2025/versions/2), downloaded 2026-10-26. Dataset license displayed by Kaggle: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Associated DOI supplied in the brief: `10.34740/KAGGLE/DSV/14465228`; its version correspondence has not been independently verified.

**Milestone 1 review gate: stop. Survival modeling, prediction and external-data integration have not been performed.**
'''
    (root/'reports/milestone_01_summary.md').write_text(report,encoding='utf-8')
    (root/'handoff/findings.md').write_text('# Initial findings\n\n'+
        f'Computed from Kaggle version 2: {s["raw_rows"]:,} rows; {s["unique_recorded_player_names"]:,} names; '+
        f'{s["clubs"]} clubs; {s["raw_injury_labels"]} raw labels.\n\n'+
        f'All reported durations follow inclusive date counting. {s["potential_duplicate_rows"]:,} rows belong to possible repeated-episode groups. '+
        'Burden sums require this sensitivity context.\n\n'+
        f'Leading frequency: {top_frequency.injury_type_raw}. Leading summed days: {top_days.injury_type_raw}. Leading summed missed matches: {top_games.injury_type_raw}.\n\n'+
        'Full evidence, tables and interpretation: `reports/milestone_01_summary.md`. Phase 2 awaits review.\n',encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--as-of',default='2026-10-26',help='Explicit analysis date for future-date checks (YYYY-MM-DD)')
    parser.add_argument('--no-figures',action='store_true')
    args=parser.parse_args()
    run(as_of=args.as_of,figures=not args.no_figures)

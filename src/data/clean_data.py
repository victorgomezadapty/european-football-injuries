"""Keep original variables alongside typed analytical columns; never impute outcomes."""
import hashlib
import pandas as pd

ALIASES = {
    'season': ['Season', 'season'], 'injury_type_raw': ['Injury', 'injury'],
    'reported_days_out': ['Days', 'days_out'], 'games_missed': ['Games missed', 'Games Missed', 'games_missed'],
    'injury_start': ['injury_from_parsed', 'Injury From'],
    'injury_end': ['injury_until_parsed', 'Injury Until'],
    'player_name': ['player_name', 'Player'], 'age_recorded': ['player_age', 'Player Age'],
    'position': ['player_position', 'Player Position'], 'club': ['club', 'Club'], 'league': ['league', 'League'],
}
MISSING = {'', '-', '--', 'n/a', 'na', 'nan', 'null', 'none', '?', 'unknown'}


def text(series):
    result = series.astype('string').str.strip().str.normalize('NFC')
    return result.mask(result.str.casefold().isin(MISSING))


def numeric(series, days=False):
    pattern = r'([+-]?\d+(?:\.\d+)?)\s*(?:days?|d)?' if days else r'([+-]?\d+(?:\.\d+)?)'
    return pd.to_numeric(text(series).str.casefold().str.extract('^' + pattern + '$', expand=False), errors='coerce').astype('Float64')


def dates(series):
    """Explicit US dates confirmed in the Kaggle file; ISO also supported without guessing."""
    s = text(series)
    us = pd.to_datetime(s, format='%m/%d/%Y', errors='coerce')
    iso = pd.to_datetime(s, format='%Y-%m-%d', errors='coerce')
    return us.fillna(iso)


def clean_data(raw):
    df = raw.copy()
    mapping = {}
    # Snapshot before adding canonical names, some of which also exist in the source.
    source = raw.copy()
    for dest, aliases in ALIASES.items():
        found = [a for a in aliases if a in source]
        if len(found) != 1:
            raise ValueError(f'Expected one source column for {dest}; found {found}. Headers: {list(raw)}')
        mapping[dest] = found[0]
        df[dest + '_source'] = source[found[0]]
        df[dest] = text(source[found[0]])
    df['source_row'] = range(2, len(raw) + 2)
    df['event_id'] = df.source_row.map(lambda r: f'row-{r:06d}')
    df['exact_duplicate'] = raw.duplicated(keep='first')
    df['exact_duplicate_member'] = raw.duplicated(keep=False)
    for col in ['reported_days_out', 'games_missed', 'age_recorded']:
        df[col] = numeric(df[col + '_source'], days=(col == 'reported_days_out'))
    for col in ['injury_start', 'injury_end']:
        df[col] = dates(df[col + '_source'])
    df['calculated_days_out'] = (df.injury_end - df.injury_start).dt.days.astype('Float64')
    df['duration_difference'] = df.reported_days_out - df.calculated_days_out
    # Keep names intact. IDs are only exact-name surrogates, not verified identities.
    df['player_id'] = df.player_name.map(lambda x: 'name-' + hashlib.sha256(str(x).encode('utf-8')).hexdigest()[:16] if pd.notna(x) else pd.NA).astype('string')
    df['injury_label_key'] = df.injury_type_raw.str.casefold().str.replace(r'\s+', ' ', regex=True)
    df['days_out'] = df.reported_days_out.where(df.reported_days_out.ge(0) & df.reported_days_out.mod(1).eq(0))
    df['games_missed_valid'] = df.games_missed.where(df.games_missed.ge(0) & df.games_missed.mod(1).eq(0))
    df['injury_month'] = df.injury_start.dt.to_period('M').astype('string').mask(df.injury_start.isna())
    df['age_group'] = pd.cut(df.age_recorded, [0, 20, 25, 30, 35, float('inf')], labels=['<=20','21-25','26-30','31-35','36+']).astype('string')
    df['potential_duplicate_episode'] = False
    complete_key = df[['player_id','injury_start','injury_end','injury_label_key']].notna().all(axis=1)
    df.loc[complete_key, 'potential_duplicate_episode'] = df.loc[complete_key].duplicated(['player_id','injury_start','injury_end','injury_label_key'], keep=False)
    df['same_day_player_records'] = False
    dated = df.player_id.notna() & df.injury_start.notna() & ~df.exact_duplicate
    df.loc[dated, 'same_day_player_records'] = df.loc[dated].duplicated(['player_id','injury_start'], keep=False)
    return df, mapping

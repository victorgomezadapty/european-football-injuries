"""Independent stdlib reconciliation of real CSV and final aggregate outputs."""
from pathlib import Path
from collections import Counter
from datetime import datetime
import csv
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[1]


def verify():
    manifest=json.loads((ROOT/'data/raw/manifest.json').read_text(encoding='utf-8'))
    item=manifest['files'][0]
    path=ROOT/'data/raw'/item['name']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256']
    with path.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        headers=reader.fieldnames
        rows=list(reader)
    summary=json.loads((ROOT/'reports/dataset_summary.json').read_text(encoding='utf-8'))
    assert len(rows)==summary['raw_rows']
    assert len(headers)==summary['raw_columns']
    assert len({r['player_name'].strip() for r in rows})==summary['unique_recorded_player_names']
    assert len({r['club'].strip() for r in rows})==summary['clubs']
    assert len({r['Injury'] for r in rows})==summary['raw_injury_labels']
    days=sum(int(re.fullmatch(r'(\d+) days?',r['Days']).group(1)) for r in rows)
    games=sum(int(r['Games missed']) for r in rows)
    assert days==summary['reported_total_days_out']
    assert games==summary['reported_total_games_missed']
    for r in rows:
        start=datetime.strptime(r['injury_from_parsed'],'%m/%d/%Y')
        end=datetime.strptime(r['injury_until_parsed'],'%m/%d/%Y')
        assert int(re.fullmatch(r'(\d+) days?',r['Days']).group(1))==(end-start).days+1
    with (ROOT/'reports/tables/burden_by_injury_type_raw.csv').open(encoding='utf-8',newline='') as f:
        burden=list(csv.DictReader(f))
    assert sum(int(r['injury_count']) for r in burden)==len(rows)
    assert sum(float(r['total_days_out']) for r in burden)==days
    assert sum(float(r['total_games_missed']) for r in burden)==games
    for group in ['position','league','season','club','age_group']:
        with (ROOT/f'reports/tables/burden_by_{group}.csv').open(encoding='utf-8',newline='') as f:
            grouped=list(csv.DictReader(f))
        assert sum(int(r['injury_count']) for r in grouped)==len(rows)
        assert sum(float(r['total_days_out']) for r in grouped)==days
    with (ROOT/'data/processed/player_burden_profiles.csv').open(encoding='utf-8',newline='') as f:
        profiles=list(csv.DictReader(f))
    assert sum(int(r['career_injury_count_in_dataset']) for r in profiles)==len(rows)
    assert all(float(r['recorded_interval_union_days']) <= float(r['total_days_out']) for r in profiles)
    counts=Counter(r['player_name'].strip() for r in rows)
    assert sum(n>1 for n in counts.values())==summary['players_with_multiple_records']
    episode_counts=Counter((r['player_name'].strip(),re.sub(r'\s+',' ',r['Injury'].strip().casefold()),r['injury_from_parsed'],r['injury_until_parsed']) for r in rows)
    assert len(episode_counts)==summary['candidate_episode_count_sensitivity']
    assert sum(n for n in episode_counts.values() if n>1)==summary['potential_duplicate_rows']
    assert not list((ROOT/'reports/figures').glob('*.tmp'))
    assert len([p for p in (ROOT/'notebooks').glob('*.ipynb') if p.name!='public_review.ipynb'])==10
    for path in (ROOT/'notebooks').glob('*.ipynb'):
        nb=json.loads(path.read_text(encoding='utf-8'))
        assert not [o for c in nb['cells'] for o in c.get('outputs',[]) if o.get('output_type')=='error'],path
        if path.name.startswith(('07_','10_')):
            assert all(c['cell_type']=='markdown' for c in nb['cells']),path
        else:
            assert all(c['execution_count'] is not None for c in nb['cells'] if c['cell_type']=='code'),path
    result={'status':'passed','raw_rows_reconciled':len(rows),'source_sha256':item['sha256'],
            'independent_total_days':days,'independent_total_games':games,
            'checks':'source checksum; dimensions; identity-label counts; all duration conventions; group totals; player totals; interval-union upper bound; executed notebooks; deferred phases'}
    (ROOT/'reports/verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    verify()

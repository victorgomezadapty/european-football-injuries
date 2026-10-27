"""Build an aggregate-only notebook that runs locally and as a Kaggle public review."""
from pathlib import Path
import argparse
import json
import shutil
import nbformat as nbf
from nbclient import NotebookClient

ROOT=Path(__file__).resolve().parents[1]


def build(execute=False):
    cells=[nbf.v4.new_markdown_cell('''# Football Injury Burden — Reproducible Public Review

**Víctor Andrés Gómez López · 2026**

An independent aggregate analysis of recorded football absences. The original data were created by **Sanan Muzaffarov**, [European Football Injuries (2020–2025), Kaggle version 2](https://www.kaggle.com/datasets/sananmuzaffarov/european-football-injuries-2020-2025/versions/2), listed as **CC BY-SA 4.0**. Derived data and figures retain that license; original notebook code/prose is MIT. Transformations: explicit date/duration parsing, record-quality audit, raw-label aggregation and candidate same-interval sensitivity. See the bundled data-license notice.

This review loads **derived aggregate statistics**, not the original raw CSV or individual medical histories. It does not estimate true injury incidence, availability percentages, clinical recovery prognosis or prospective injury risk. No independent medical-source verification has been completed.

[Interactive bilingual study](https://european-football-injuries.vercel.app) · [GitHub and full event-level reproduction](https://github.com/victorgomezadapty/european-football-injuries) · [Scientific discussion](https://european-football-injuries.vercel.app/evidence)
''')]
    def code(s):cells.append(nbf.v4.new_code_cell(s))
    def md(s):cells.append(nbf.v4.new_markdown_cell(s))
    code('''from pathlib import Path
import json
import hashlib
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Markdown

local = Path.cwd() / 'publication' / 'kaggle'
if (local / 'injury_burden.csv').exists():
    bundle = local
else:
    matches = list(Path('/kaggle/input').rglob('project_aggregate_views.json'))
    if len(matches) != 1:
        raise FileNotFoundError('Attach only the European Football Injuries Burden Analysis derivative dataset.')
    bundle = matches[0].parent

project = json.loads((bundle / 'project_aggregate_views.json').read_text(encoding='utf-8'))
injury = pd.read_csv(bundle / 'injury_burden.csv')
sensitivity = pd.read_csv(bundle / 'duplicate_sensitivity.csv')
manifest = json.loads((bundle / 'publication_manifest.json').read_text(encoding='utf-8'))
for item in manifest['files']:
    assert hashlib.sha256((bundle / item['name']).read_bytes()).hexdigest() == item['sha256'], item['name']
print('Aggregate release integrity checks passed.')
display(pd.DataFrame([{'original_records': project['summary']['raw_rows'],
                       'source_columns': project['summary']['raw_columns'],
                       'recorded_names': project['summary']['unique_recorded_player_names'],
                       'club_labels': project['summary']['clubs'],
                       'absence_labels': project['summary']['raw_injury_labels']}]))
''')
    md('''## Reconcile the record-level summaries

Frequency, continuous reported duration and cumulative episode burden are distinct. The file includes illnesses, quarantine, fitness/rest and injuries. Summed days and matches can repeat across overlapping episodes or club contexts. The injury-label table retains its source wording.
''')
    code('''assert int(injury.injury_count.sum()) == project['summary']['raw_rows']
assert injury.total_days_out.sum() == project['summary']['reported_total_days_out']
assert injury.total_games_missed.sum() == project['summary']['reported_total_games_missed']
display(injury.sort_values('injury_count', ascending=False).head(12))
''')
    code('''fig, axes = plt.subplots(1, 2, figsize=(14, 5), layout='constrained')
for ax, metric, label in zip(axes, ['injury_count', 'total_days_out'], ['Recorded events', 'Reported episode-days summed']):
    selected = injury.nlargest(10, metric).iloc[::-1]
    ax.barh(selected.injury_type_raw, selected[metric], color='#177b7b')
    ax.set_xlabel(label)
    ax.spines[['top', 'right']].set_visible(False)
fig.suptitle('Frequency and cumulative time loss answer different questions')
plt.show()
''')
    md('''## Candidate repeated-interval sensitivity

The source has no exact whole-row duplicates, but **981 groups (1,973 rows)** repeat the same recorded name, normalized label and date interval across clubs. Within these groups, reported days and matches agree. Keeping the first source row per complete key yields **14,611 candidate rows**. This is a sensitivity assumption, not verification of clinical episode identity or club attribution.
''')
    code('''display(sensitivity)
days_reduction = 100 * (1 - sensitivity.iloc[1].total_days_out / sensitivity.iloc[0].total_days_out)
print(f'Summed reported days change by {days_reduction:.2f}% under candidate collapsing.')
''')
    md('''## Inspect a league/season combination

Change the selectors below to inspect exact precomputed subset summaries. Their medians come from the corresponding underlying records; medians are never averaged across groups. The candidate view keeps first-row context for sensitivity, so it is not an authoritative transfer or club attribution.
''')
    code('''view = 'raw'  # 'raw' or 'candidate'
league = 'all'  # all, Bundesliga, La Liga, Ligue 1, Premier League, Serie A
season = 'all'  # all, 20/21, 21/22, 22/23, 23/24, 24/25
subset = project['views'][view][league + '|' + season]
subset_table = pd.DataFrame(subset['injuries'])
assert subset_table['count'].sum() == subset['count']
display(subset_table.sort_values('days', ascending=False).head(15))
''')
    md('''## Availability and incidence denominators are absent

Eligible fixtures, squad-registration and transfer intervals, complete observation windows and player match/training hours are missing. The first and last recorded injury dates are not valid observation denominators. A recorded end is not independently verified medical clearance. Gaps without records are not verified healthy time. No survival curve or prediction model is added to compensate for these missing definitions.

The public web therefore reports **Recorded Availability Burden Profiles** and aggregate consequences, without giving a player availability percentage. Repeated labels do not establish clinical reinjury.
''')
    md((ROOT/'docs/discussion.md').read_text(encoding='utf-8'))
    md('''## Reproduce from the original source

1. Clone the linked GitHub repository and install `requirements.txt`.
2. Download the official version 2 ZIP from the credited creator.
3. Run `python scripts/acquire_data.py --archive path/to/archive.zip`; the registered source checksum must match.
4. Run `python -m unittest discover -s tests -v`, then `python -m src.pipeline --as-of 2026-10-26`.
5. Rebuild detailed local notebooks with `python scripts/build_notebooks.py --execute`.

Raw and individual-history files are excluded from the public release. The public website can be rebuilt without the original raw CSV using `npm test` and `npm run build`. A fresh event-level recomputation intentionally requires obtaining the original source.

The accompanying `reproducible_source.zip`, methodology, search record, DOI bibliography and `DATA_LICENSE.md` describe the transformations and rights boundaries. This notebook's code license does not relicense source data or the scientific articles.
''')
    nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}})
    if execute:
        NotebookClient(nb,timeout=120,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}}).execute()
    nbf.validate(nb)
    path=ROOT/'notebooks/public_review.ipynb'
    nbf.write(nb,path)
    target=ROOT/'publication/kaggle-notebook';target.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(path,target/'football_burden_review.ipynb')
    metadata={'id':'vctorandrsgmezlpez/european-football-injury-burden-review','title':'European Football Injury Burden Review',
              'code_file':'football_burden_review.ipynb','language':'python','kernel_type':'notebook',
              'is_private':False,'enable_gpu':False,'enable_internet':False,
              'dataset_sources':['vctorandrsgmezlpez/european-football-injuries-burden-analysis'],
              'competition_sources':[],'kernel_sources':[],'model_sources':[],'license_name':'mit'}
    (target/'kernel-metadata.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    print('Aggregate-only public notebook '+('executed and saved.' if execute else 'built.'))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true')
    build(parser.parse_args().execute)

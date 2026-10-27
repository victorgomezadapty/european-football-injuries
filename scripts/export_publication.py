"""Prepare only aggregate data, own code and rights notices for the public release."""
from pathlib import Path
import json
import hashlib
import shutil
import zipfile
import csv
import pandas as pd
import mistune
from src.data.load_data import load_raw
from src.data.clean_data import clean_data
from src.features.burden import summarize_burden

ROOT=Path(__file__).resolve().parents[1]
GITHUB='https://github.com/victorgomezadapty/european-football-injuries'
SOURCE='https://www.kaggle.com/datasets/sananmuzaffarov/european-football-injuries-2020-2025/versions/2'


def write_json(value,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n',encoding='utf-8',newline='\n')


def aggregate_view(events):
    table=summarize_burden(events,'injury_type_raw')
    return {'count':len(events),'days':int(events.days_out.sum()),'games':int(events.games_missed_valid.sum()),
        'names':int(events.player_id.nunique()),'median':float(events.days_out.median()),
        'injuries':[{'label':str(r.injury_type_raw),'count':int(r.injury_count),'median':float(r.median_days_out),
                     'days':int(r.total_days_out),'games':int(r.total_games_missed),'n':int(r.valid_days_count),
                     'q1':round(float(r.p25_days_out),2),'q3':round(float(r.p75_days_out),2)} for r in table.itertuples()]}


def export():
    web=ROOT/'web'
    raw,manifest=load_raw(ROOT)
    clean,_=clean_data(raw)
    events=clean.loc[~clean.exact_duplicate].copy()
    summary=json.loads((ROOT/'reports/dataset_summary.json').read_text(encoding='utf-8'))
    complete=events[['player_id','injury_start','injury_end','injury_label_key']].notna().all(axis=1)
    candidate=pd.concat([events.loc[complete].drop_duplicates(['player_id','injury_start','injury_end','injury_label_key']),events.loc[~complete]])
    views={}
    for mode,frame in [('raw',events),('candidate',candidate)]:
        views[mode]={}
        for league in ['all']+summary['leagues']:
            for season in ['all']+summary['seasons']:
                subset=frame
                if league!='all':subset=subset.loc[subset.league.eq(league)]
                if season!='all':subset=subset.loc[subset.season.eq(season)]
                if len(subset):views[mode][league+'|'+season]=aggregate_view(subset)
    counts=events.groupby('player_id').size().value_counts().sort_index()
    payload={'schema_version':1,'summary':summary,'source':{'author':'Sanan Muzaffarov','version':2,'url':SOURCE,
        'license':'CC BY-SA 4.0','license_url':'https://creativecommons.org/licenses/by-sa/4.0/',
        'csv_sha256':manifest['files'][0]['sha256'],'retrieved':'2026-10-26',
        'transformations':'Typed dates and durations; exact-row duplicate audit; label-level and context-level aggregation; candidate-episode sensitivity. No independent clinical-source verification.'},
        'analysis_author':'Víctor Andrés Gómez López','views':views,
        'player_record_distribution':[{'records':int(k),'names':int(v)} for k,v in counts.items()]}
    write_json(payload,web/'data/project.json')
    if not (web/'data/links.json').exists():
        write_json({'github':GITHUB,'kaggle':SOURCE,'site':'https://european-football-injuries.vercel.app','portfolio':'https://victor-gomez-portfolio.vercel.app'},web/'data/links.json')
    downloads=web/'downloads';downloads.mkdir(exist_ok=True)
    files={
        'injury_burden.csv':'reports/tables/burden_by_injury_type_raw.csv',
        'injury_burden_candidate_sensitivity.csv':'reports/tables/injury_burden_candidate_sensitivity.csv',
        'duplicate_sensitivity.csv':'reports/tables/duplicate_sensitivity.csv',
        'burden_by_league.csv':'reports/tables/burden_by_league.csv',
        'burden_by_season.csv':'reports/tables/burden_by_season.csv',
        'burden_by_position.csv':'reports/tables/burden_by_position.csv',
        'injuries_per_player_distribution.csv':'reports/tables/injuries_per_player_distribution.csv',
        'quality_summary.csv':'reports/tables/quality_summary.csv',
        'methodology.md':'docs/methodology.md','availability_definition.md':'docs/availability_definition.md',
        'data_dictionary.md':'docs/public_data_dictionary.md','data_license.md':'DATA_LICENSE.md',
        'notebook_license.md':'NOTEBOOK_LICENSE.md',
        'references.bib':'references/references.bib','literature_search.md':'docs/literature_search.md',
    }
    for dest,source in files.items():
        if not (ROOT/source).exists():raise FileNotFoundError(f'Publication prerequisite missing: {source}')
        (downloads/dest).write_text((ROOT/source).read_text(encoding='utf-8'),encoding='utf-8',newline='\n')
    refs=json.loads((ROOT/'references/references.json').read_text(encoding='utf-8'))
    write_json(refs,web/'data/references.json')
    evidence_template=(ROOT/'web/evidence.template.html').read_text(encoding='utf-8')
    render=mistune.create_markdown(escape=True,plugins=['table'])
    for lang,file in [('es','discussion_es.md'),('en','discussion.md')]:
        content=(ROOT/'docs'/file).read_text(encoding='utf-8')
        article=render(content).replace('href="literature_search.md"','href="/downloads/literature_search.md"').replace('href="../references/references.json"','href="/data/references.json"')
        evidence_template=evidence_template.replace('{{DISCUSSION_'+lang.upper()+'}}',article)
    (web/'evidence.html').write_text(evidence_template,encoding='utf-8')
    public_manifest={'release':'1.0.0','source':payload['source'],'analysis_author':payload['analysis_author'],
        'data_license':'CC-BY-SA-4.0','code_license':'MIT','publication_scope':'Aggregate statistics and independently authored reproducibility materials. No original raw CSV, individual player medical records, third-party article text or third-party figures are included.',
        'files':[{'name':name,'sha256':hashlib.sha256((downloads/name).read_bytes()).hexdigest()} for name in files]}
    write_json(public_manifest,downloads/'publication_manifest.json')
    bundle=ROOT/'publication/kaggle';bundle.mkdir(parents=True,exist_ok=True)
    for path in downloads.iterdir():
        if path.is_file():shutil.copyfile(path,bundle/path.name)
    write_json(payload,bundle/'project_aggregate_views.json')
    shutil.copyfile(ROOT/'references/references.json',bundle/'references.json')
    for file in ['discussion.md','discussion_es.md','final_scientific_audit.md']:
        if (ROOT/'docs'/file).exists():shutil.copyfile(ROOT/'docs'/file,bundle/file)
    # The downloadable code archive excludes all original data and named histories.
    with zipfile.ZipFile(bundle/'reproducible_source.zip','w',compression=zipfile.ZIP_DEFLATED) as archive:
        for folder in ['src','scripts','tests','docs','references','web']:
            for file in (ROOT/folder).rglob('*'):
                if file.is_file() and '__pycache__' not in file.parts and file.suffix!='.zip' and file!=ROOT/'docs/data_dictionary.md':archive.write(file,file.relative_to(ROOT))
        for file in ['requirements.txt','requirements-lock.txt','README.md','LICENSE','DATA_LICENSE.md','NOTEBOOK_LICENSE.md','CITATION.cff','package.json','vercel.json']:
            archive.write(ROOT/file,file)
        archive.write(ROOT/'data/raw/manifest.json','data/raw/manifest.json')
        archive.write(ROOT/'reports/dataset_summary.json','reports/dataset_summary.json')
        if (ROOT/'notebooks/public_review.ipynb').exists():
            archive.write(ROOT/'notebooks/public_review.ipynb','notebooks/public_review.ipynb')
    shutil.copyfile(bundle/'reproducible_source.zip',downloads/'reproducible_source.zip')
    # Files are the derived work; preserve original creator and ShareAlike attribution.
    write_json({'title':'European Football Injuries Burden Analysis',
        'id':'vctorandrsgmezlpez/european-football-injuries-burden-analysis',
        'licenses':[{'name':'CC-BY-SA-4.0'}],
        'subtitle':'Aggregate injury burden, sensitivity audit, citations and reproducible code',
        'description':(ROOT/'docs/kaggle_description.md').read_text(encoding='utf-8')},bundle/'dataset-metadata.json')
    print(f'Exported {len(views["raw"])} filter combinations per view; aggregate-only public data. Kaggle bundle: {bundle}')


if __name__=='__main__':
    export()

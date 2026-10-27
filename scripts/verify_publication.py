"""Verify the aggregate-only release boundary and publication checksums."""
from pathlib import Path
import csv
import hashlib
import json
import re
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def verify():
    bundle=ROOT/'publication/kaggle'
    manifest=json.loads((bundle/'publication_manifest.json').read_text(encoding='utf-8'))
    for item in manifest['files']:
        assert hashlib.sha256((bundle/item['name']).read_bytes()).hexdigest()==item['sha256'],item['name']
        assert (ROOT/'web/downloads'/item['name']).read_bytes()==(bundle/item['name']).read_bytes()
    forbidden_columns={'player_name','player_id','injury_start','injury_end','source_row','previous_injury_date'}
    for file in bundle.glob('*.csv'):
        with file.open(encoding='utf-8',newline='') as f:
            reader=csv.reader(f)
            assert not forbidden_columns.intersection(next(reader)),file.name
    with zipfile.ZipFile(bundle/'reproducible_source.zip') as archive:
        for name in archive.namelist():
            assert not re.search(r'(^|/)(\.git|\.vercel|node_modules|__pycache__)/',name),name
            assert not (name.startswith('data/raw/') and name!='data/raw/manifest.json'),name
            assert 'player_injury_timelines' not in name,name
            assert 'injury_events.csv' not in name,name
    nb=json.loads((ROOT/'notebooks/public_review.ipynb').read_text(encoding='utf-8'))
    for cell in nb['cells']:
        if cell['cell_type']=='code':assert cell['execution_count'] is not None,'Public notebook not executed'
        assert not any(o.get('output_type')=='error' for o in cell.get('outputs',[]))
    for file in [ROOT/'web/data/project.json',ROOT/'notebooks/public_review.ipynb']:
        body=file.read_text(encoding='utf-8')
        assert not re.search(r'gh[o_up]_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16}',body),file.name
    result={'status':'passed','public_data':'aggregate statistics only','data_license':'CC-BY-SA-4.0','code_license':'MIT',
            'checked':'release file hashes; public/bundle byte equality; no individual CSV fields; no raw data or credential directories in source zip; executed public notebook'}
    (ROOT/'reports/publication_verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':verify()

"""Acquire the public Kaggle archive without changing an existing raw file."""
from pathlib import Path
import hashlib
import io
import json
import zipfile
from datetime import datetime, timezone
import requests
import argparse

ROOT = Path(__file__).resolve().parents[1]
DATASET = 'sananmuzaffarov/european-football-injuries-2020-2025'
URL = f'https://www.kaggle.com/api/v1/datasets/download/{DATASET}?datasetVersionNumber=2'

def acquire(archive=None):
    from_browser = archive is not None
    raw = ROOT / 'data/raw'
    raw.mkdir(parents=True, exist_ok=True)
    manifest = raw / 'manifest.json'
    expected = None
    if manifest.exists():
        expected = json.loads(manifest.read_text(encoding='utf-8'))
        archive_file = raw / 'kaggle_version_2.zip'
        present = archive_file.exists() and all((raw / item['name']).exists() for item in expected['files'])
        if present:
            if hashlib.sha256(archive_file.read_bytes()).hexdigest() != expected['archive_sha256']:
                raise ValueError('Raw archive checksum mismatch.')
        for item in expected['files']:
            path = raw / item['name']
            if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
                raise ValueError(f'Raw checksum mismatch: {path.name}')
        if present:
            print('Existing immutable raw data verified.')
            return
    if archive:
        content_zip = Path(archive).read_bytes()
    else:
        response = requests.get(URL, timeout=90)
        response.raise_for_status()
        content_zip = response.content
    if not zipfile.is_zipfile(io.BytesIO(content_zip)):
        raise ValueError('Expected a Kaggle ZIP archive; use --archive after browser download.')
    if expected and hashlib.sha256(content_zip).hexdigest() != expected['archive_sha256']:
        raise ValueError('This archive does not match the registered source version/checksum.')
    archive_path = raw / 'kaggle_version_2.zip'
    if archive_path.exists() and archive_path.read_bytes() != content_zip:
        raise FileExistsError('Refusing to replace a different raw archive.')
    archive_path.write_bytes(content_zip)
    files = []
    with zipfile.ZipFile(io.BytesIO(content_zip)) as archive:
        for entry in archive.infolist():
            if entry.is_dir():
                continue
            name = Path(entry.filename).name
            if not name.lower().endswith('.csv'):
                continue
            path = raw / name
            content = archive.read(entry)
            if expected:
                registered = next((f for f in expected['files'] if f['name'] == name), None)
                if not registered or hashlib.sha256(content).hexdigest() != registered['sha256']:
                    raise ValueError(f'CSV does not match registered source: {name}')
            if path.exists() and path.read_bytes() != content:
                raise FileExistsError(f'Refusing to overwrite {name}')
            path.write_bytes(content)
            files.append({'name': name, 'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()})
    if not files:
        raise ValueError('No CSV found in Kaggle archive.')
    info = {'dataset': DATASET, 'version': 2, 'source_url': URL,
            'dataset_page': f'https://www.kaggle.com/datasets/{DATASET}',
            'retrieved_at_utc': datetime.now(timezone.utc).isoformat(),
            'acquisition_method': 'browser_download' if from_browser else 'public_api',
            'license_as_shown_on_kaggle': 'CC BY-SA 4.0',
            'archive_sha256': hashlib.sha256(content_zip).hexdigest(), 'files': files}
    if expected:
        info = expected
    else:
        manifest.write_text(json.dumps(info, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(info, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, help='Official version 2 ZIP downloaded from Kaggle')
    acquire(parser.parse_args().archive)

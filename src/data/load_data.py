from pathlib import Path
import hashlib
import json
import pandas as pd


def load_raw(root: Path):
    """Read only the manifest-registered CSV, preserving strings and blank tokens."""
    raw_dir = root / 'data/raw'
    manifest = json.loads((raw_dir / 'manifest.json').read_text(encoding='utf-8'))
    files = [f for f in manifest['files'] if f['name'].endswith('.csv')]
    if len(files) != 1:
        raise ValueError('Select exactly one registered injury CSV before analysis.')
    item = files[0]
    path = raw_dir / item['name']
    if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
        raise ValueError('Raw CSV checksum changed. Analysis stopped.')
    df = pd.read_csv(path, dtype='string', encoding='utf-8-sig', keep_default_na=False)
    if df.empty:
        raise ValueError('The CSV contains no records.')
    return df, manifest

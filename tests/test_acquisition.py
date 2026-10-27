"""Test restoring a clone that tracks provenance but intentionally omits raw data."""
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from scripts import acquire_data


class AcquisitionIntegrity(unittest.TestCase):
    def fixture(self,root):
        content=b'column\nfixture-only\n'
        archive=root/'download.zip'
        with zipfile.ZipFile(archive,'w') as z:z.writestr('fixture.csv',content)
        raw=root/'data/raw';raw.mkdir(parents=True)
        info={'dataset':'test-fixture','version':2,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
              'files':[{'name':'fixture.csv','bytes':len(content),'sha256':hashlib.sha256(content).hexdigest()}]}
        manifest=raw/'manifest.json';manifest.write_text(json.dumps(info),encoding='utf-8')
        return archive,raw,manifest,content

    def test_fresh_clone_restores_exact_registered_archive(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            archive,raw,manifest,content=self.fixture(root)
            registered=manifest.read_bytes()
            with patch.object(acquire_data,'ROOT',root),redirect_stdout(io.StringIO()):
                acquire_data.acquire(archive)
                acquire_data.acquire()
            self.assertEqual((raw/'fixture.csv').read_bytes(),content)
            self.assertEqual(manifest.read_bytes(),registered)

    def test_different_archive_is_rejected_before_extracting(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            archive,raw,manifest,_=self.fixture(root)
            with zipfile.ZipFile(archive,'w') as z:z.writestr('fixture.csv',b'changed bytes')
            with patch.object(acquire_data,'ROOT',root),self.assertRaises(ValueError):
                acquire_data.acquire(archive)
            self.assertFalse((raw/'fixture.csv').exists())


if __name__=='__main__':unittest.main()

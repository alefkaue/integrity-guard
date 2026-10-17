import hashlib
from pathlib import Path
import tempfile
import unittest
from integrity_guard import snapshot, validate, compare

class IntegrityTests(unittest.TestCase):
    def test_full_change_lifecycle(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'keep').write_bytes(b'original')
            (root / 'remove').write_bytes(b'data')
            old = snapshot(root)
            self.assertEqual(old['keep'], hashlib.sha256(b'original').hexdigest())
            self.assertFalse(any(compare(old, snapshot(root)).values()))
            (root / 'keep').write_bytes(b'changed')
            (root / 'remove').unlink()
            (root / 'new').write_bytes(b'new')
            self.assertEqual(compare(old, snapshot(root)), dict(added=['new'], removed=['remove'], modified=['keep']))

    def test_malformed_baselines(self):
        for data in [[], {}, {'version': 2, 'files': {}}, {'version': 1, 'files': {'../escape': 'a'*64}}, {'version': 1, 'files': {'file': 'bad'}}]:
            with self.subTest(data=data), self.assertRaises(ValueError):
                validate(data)

    def test_nested_empty_and_unicode(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(snapshot(root), {})
            (root / 'sub').mkdir()
            (root / 'sub' / 'ação.txt').write_bytes(b'')
            self.assertEqual(list(snapshot(root)), ['sub/ação.txt'])

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'real').write_bytes(b'data')
            try:
                (root / 'link').symlink_to(root / 'real')
            except OSError:
                self.skipTest('symlink privilege unavailable')
            with self.assertRaises(ValueError):
                snapshot(root)

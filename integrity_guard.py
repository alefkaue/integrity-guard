"""SHA-256 file inventory with explicit input validation and fail-closed traversal."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys

def snapshot(root):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError('root must be a directory, not a symlink')
    files = {}
    def walk_error(error):
        raise error
    for directory, dirs, names in os.walk(root, followlinks=False, onerror=walk_error):
        for name in sorted(dirs + names):
            path = Path(directory) / name
            before = path.lstat()
            if stat.S_ISLNK(before.st_mode):
                raise ValueError(f'symlink rejected: {path}')
            if stat.S_ISDIR(before.st_mode):
                continue
            if not stat.S_ISREG(before.st_mode):
                raise ValueError(f'non-regular file rejected: {path}')
            digest = hashlib.sha256()
            with path.open('rb') as stream:
                opened = os.fstat(stream.fileno())
                if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
                    raise ValueError(f'file replaced while opening: {path}')
                for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                    digest.update(chunk)
                after = os.fstat(stream.fileno())
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns) or (opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                raise ValueError(f'file changed while hashing: {path}')
            files[path.relative_to(root).as_posix()] = digest.hexdigest()
    return dict(sorted(files.items()))

def validate(data):
    if not isinstance(data, dict) or data.get('version') != 1 or not isinstance(data.get('files'), dict):
        raise ValueError('unsupported or invalid baseline')
    for name, digest in data['files'].items():
        if not isinstance(name, str) or not name or '\\' in name or ':' in name or PurePosixPath(name).is_absolute() or any(part in ('', '.', '..') for part in name.split('/')):
            raise ValueError('unsafe baseline path')
        if not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest):
            raise ValueError('invalid SHA-256 digest')
    return data['files']

def compare(old, new):
    return dict(added=sorted(new.keys() - old.keys()), removed=sorted(old.keys() - new.keys()),
        modified=sorted(name for name in old.keys() & new.keys() if old[name] != new[name]))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['baseline', 'check'])
    parser.add_argument('root', type=Path)
    parser.add_argument('inventory', type=Path, help='Store outside the monitored directory')
    args = parser.parse_args()
    try:
        if args.inventory.resolve().is_relative_to(args.root.resolve()):
            raise ValueError('inventory must be outside the monitored directory')
        current = snapshot(args.root)
        if args.command == 'baseline':
            # Exclusive creation prevents accidentally trusting a changed baseline.
            with args.inventory.open('x', encoding='utf-8') as stream:
                json.dump(dict(version=1, files=current), stream, indent=2)
            print(json.dumps(dict(baseline=str(args.inventory), files=len(current))))
            return 0
        old = validate(json.loads(args.inventory.read_text(encoding='utf-8')))
        report = compare(old, current)
    except (OSError, ValueError) as error:
        parser.exit(2, f'Error: {error}\n')
    print(json.dumps(report, indent=2))
    return 1 if any(report.values()) else 0

if __name__ == '__main__':
    sys.exit(main())

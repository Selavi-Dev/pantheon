"""Generate/check wheel resources from canonical reviewed source directories."""
import argparse
import hashlib
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'pantheon/resources'
TREES = ('profiles', 'skills', 'registry', 'governance', 'schemas')

def index(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for name in TREES:
        source, target = ROOT / name, DEST / name
        if args.check:
            if index(source) != index(target):
                raise SystemExit(f'Out-of-sync resources: {name}; run scripts/sync_resources.py')
        else:
            if target.exists(): shutil.rmtree(target)
            shutil.copytree(source, target)
    print('Package resources are synchronized.')

if __name__ == '__main__': main()

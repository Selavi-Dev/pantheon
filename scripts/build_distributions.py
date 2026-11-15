"""Generate eight standalone distribution ZIPs, no publishing or remote operations."""
import argparse
import hashlib
import zipfile
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=True)
    agents = json.loads((ROOT/'registry/agents.json').read_text(encoding='utf-8'))['agents']
    targets = [(a, out/(a['profile']+'.zip')) for a in agents]
    if any(p.exists() for _,p in targets) or (out/'SHA256SUMS').exists():
        raise SystemExit('Output already contains generated files; use a fresh directory.')
    sums=[]
    for a,path in targets:
        root=ROOT/'profiles'/a['id']
        with zipfile.ZipFile(path,'x',compression=zipfile.ZIP_DEFLATED) as z:
            for f in sorted(root.rglob('*')):
                if f.is_symlink(): raise RuntimeError(f'Symlink refused: {f}')
                if f.is_file(): z.write(f,f.relative_to(root).as_posix())
        sums.append(f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}')
    (out/'SHA256SUMS').write_text('\n'.join(sums)+'\n', encoding='utf-8', newline='\n')
    print(f'Generated {len(targets)} native distribution archives in {out}. Extract before local Hermes installation.')
if __name__=='__main__': main()

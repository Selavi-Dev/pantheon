"""Verify wheel/sdist contents against canonical profile resources and hash files."""
import argparse, hashlib, tarfile, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--dist', type=Path, required=True); a=p.parse_args()
    wheel, = a.dist.glob('*.whl'); sdist, = a.dist.glob('*.tar.gz')
    resources=ROOT/'pantheon/resources'
    with zipfile.ZipFile(wheel) as z:
        assert z.testzip() is None
        for f in resources.rglob('*'):
            if f.is_file(): assert z.read('pantheon/resources/'+f.relative_to(resources).as_posix())==f.read_bytes(),f
    with tarfile.open(sdist) as t:
        names=set(t.getnames()); prefix=next(iter(names)).split('/')[0]
        for f in resources.rglob('*'):
            if f.is_file(): assert prefix+'/pantheon/resources/'+f.relative_to(resources).as_posix() in names,f
    files=sorted(x for x in a.dist.rglob('*') if x.is_file() and x.name!='SHA256SUMS')
    (a.dist/'SHA256SUMS').write_text(''.join(f'{hashlib.sha256(x.read_bytes()).hexdigest()}  {x.relative_to(a.dist).as_posix()}\n' for x in files), encoding='utf-8', newline='\n')
    print('Wheel and sdist resource verification passed.')
if __name__=='__main__': main()

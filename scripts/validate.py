"""Offline repository consistency and secret-path checks (not a comprehensive secret scanner)."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]

def load(p): return json.loads((ROOT/p).read_text())

def main():
    a=load('registry/agents.json')['agents']; g=load('registry/groups.json')['groups']; r=load('registry/routines.json')['routines']
    ids={x['id'] for x in a}; assert len(a)==len(ids)==8
    assert {p.name for p in (ROOT/'profiles').iterdir() if p.is_dir()}==ids
    skills={p.parent.name for p in (ROOT/'skills').glob('*/SKILL.md')}; assert len(skills)==24
    charter=(ROOT/'governance/CHARTER.md').read_text().rstrip()
    for x in a:
        p=ROOT/'profiles'/x['id']; assert (p/'SOUL.md').read_text().startswith(charter+'\n')
        manifest=(p/'distribution.yaml').read_text(); assert f'name: {x["profile"]}\n' in manifest and 'version: 0.1.0\n' in manifest
        assert (p/'config.yaml').exists() and (p/'LICENSE').exists()
        assert {f.parent.name for f in (p/'skills').glob('*/SKILL.md')}==set(x['skills'])
        for s in x['skills']: assert s in skills and (p/'skills'/s/'SKILL.md').read_bytes()==(ROOT/'skills'/s/'SKILL.md').read_bytes()
    assert len(g)==len({x['id'] for x in g})==7
    for x in g: assert x['lead'] in x['members'] and set(x['members'])<=ids and 2<=len(x['members'])<=6 and len(set(x['members']))==len(x['members'])
    assert len(r)==len({x['id'] for x in r})==20
    assert len({x['purpose_key'] for x in r})==len(r)
    lookup={x['id']:set(x['skills']) for x in a}
    for x in r: assert x['owner'] in ids and x['enabled'] is False and x['skill'] in lookup[x['owner']] and (x['schedule'] is None or len(x['schedule'].split())==5)
    for p in ROOT.rglob('*'):
        if not p.is_file() or any(x in ('.git','.local','__pycache__','.venv') for x in p.relative_to(ROOT).parts): continue
        assert p.name not in ('.env','auth.json','state.db') and p.suffix not in ('.pem','.key'),f'Forbidden secret path: {p}'
    for p in ROOT.glob('schemas/*.json'): json.loads(p.read_text())
    print(f'PASS: {len(a)} profiles, {len(skills)} canonical skills, {len(g)} groups, {len(r)} inactive routines; template consistency and secret-path checks.')
if __name__=='__main__':
    try: main()
    except (AssertionError,ValueError,KeyError,OSError) as e:
        print('FAIL:',e,file=sys.stderr); raise SystemExit(1)

"""Offline source consistency and privacy checks; not a production security audit."""
from pathlib import Path
import json
import re
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_AGENTS = {'hermes', 'athena', 'argus', 'themis', 'hephaestus', 'apollo', 'mnemosyne', 'socrates'}
SKIP = {'.git', '.local', '__pycache__', '.venv', 'build', 'dist', 'release-artifacts'}
FORBIDDEN_DIRS = {'vault', 'private', 'sessions', 'memories', 'logs', 'mcp-tokens', 'platforms'}
# Deliberately narrow recognizable credential patterns. Values are never printed.
SECRET_PATTERNS = [
    re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(r'\bgh[pousr]_[A-Za-z0-9]{30,}\b'),
    re.compile(r'\bgithub_pat_[A-Za-z0-9_]{50,}\b'),
    re.compile(r'\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{24,}\b'),
    re.compile(r'\bAKIA[0-9A-Z]{16}\b'),
    re.compile(r'\b\d{7,12}:[A-Za-z0-9_-]{30,}\b'),
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def resources(directory):
    result = {}
    for path in directory.rglob('*'):
        require(not path.is_symlink(), f'Symlink is not distributable: {path.relative_to(ROOT)}')
        if path.is_file():
            result[path.relative_to(directory).as_posix()] = path.read_bytes()
    return result


def main():
    # Do not use assert for release gates: python -O strips assertions.
    version_text = (ROOT / 'pantheon/__init__.py').read_text(encoding='utf-8')
    match = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", version_text)
    require(match is not None, 'Missing source version')
    version = match.group(1)
    agents = load('registry/agents.json')['agents']
    groups = load('registry/groups.json')['groups']
    registry = load('registry/routines.json')
    routines = registry['routines']
    ZoneInfo(registry['timezone'])
    ids = {a['id'] for a in agents}
    require(len(agents) == len(ids) == 8 and ids == EXPECTED_AGENTS, 'Expected eight unique agents')
    require({p.name for p in (ROOT / 'profiles').iterdir() if p.is_dir()} == ids, 'Profile roster drift')
    skills = {p.parent.name for p in (ROOT / 'skills').glob('*/SKILL.md')}
    require(len(skills) == 25 and 'self-improvement' in skills, 'Expected 25 canonical skills including self-improvement')
    charter = (ROOT / 'governance/CHARTER.md').read_text(encoding='utf-8').rstrip()
    for agent in agents:
        aid = agent['id']
        profile = ROOT / 'profiles' / aid
        require(bool(agent['role'].strip()), f'{aid}: missing role')
        require(agent['profile'] == 'pantheon-' + aid, f'{aid}: unsafe profile name')
        require((profile / 'SOUL.md').read_text(encoding='utf-8').startswith(charter + '\n'), f'{aid}: charter drift')
        manifest = (profile / 'distribution.yaml').read_text(encoding='utf-8')
        require(f'name: {agent["profile"]}\n' in manifest and f'version: {version}\n' in manifest, f'{aid}: manifest/version drift')
        require(re.search(r"^hermes_requires: '>=\d+\.\d+\.\d+'$", manifest, re.M) is not None, f'{aid}: missing single-comparison hermes_requires')
        require((profile / 'config.yaml').is_file() and (profile / 'LICENSE').is_file(), f'{aid}: missing configuration/license')
        grants = agent['skills']
        require(len(grants) == len(set(grants)) and 'self-improvement' in grants, f'{aid}: duplicate/missing shared grant')
        require({p.parent.name for p in (profile / 'skills').glob('*/SKILL.md')} == set(grants), f'{aid}: skill grant drift')
        for skill in grants:
            require(skill in skills, f'{aid}: unknown skill {skill}')
            require(resources(profile / 'skills' / skill) == resources(ROOT / 'skills' / skill), f'{aid}: incomplete/stale skill bundle {skill}')
    require(len(groups) == len({g['id'] for g in groups}) == 7, 'Expected seven unique groups')
    for group in groups:
        require(group['lead'] in group['members'] and set(group['members']) <= ids and 2 <= len(group['members']) <= 6 and len(set(group['members'])) == len(group['members']), f'Invalid group: {group["id"]}')
    require(len(routines) == len({r['id'] for r in routines}) == 22, 'Expected 22 unique routines')
    require(len({r['purpose_key'].strip().casefold() for r in routines}) == len(routines), 'Duplicate routine ownership')
    require({r['owner'] for r in routines} == ids, 'Every agent needs a defined routine')
    lookup = {a['id']: set(a['skills']) for a in agents}
    for routine in routines:
        rid = routine['id']
        require(routine['owner'] in ids and routine['enabled'] is False and routine['skill'] in lookup[routine['owner']], f'{rid}: owner/skill/disabled invariant')
        require(routine['schedule'] is None or len(routine['schedule'].split()) == 5, f'{rid}: malformed schedule')
    extension = load('registry/self-improvement.json')
    require(set(extension['agents']) == ids and extension['extension_version'] == version, 'Improvement roster/version drift')
    require(extension['automatic_deployment'] is False and extension['external_delivery'] is False, 'Improvement must remain draft-only')
    for rid in extension['routines']:
        matches = [r for r in routines if r['id'] == rid]
        require(len(matches) == 1 and matches[0]['skill'] == 'self-improvement' and matches[0]['delivery'] == 'local', f'{rid}: missing local improvement routine')
    for path in ROOT.rglob('*'):
        rel = path.relative_to(ROOT)
        if any(part in SKIP or part.endswith('.egg-info') for part in rel.parts):
            continue
        require(not path.is_symlink(), f'Symlink in source: {rel}')
        if not path.is_file():
            continue
        forbidden_name = ((path.name == '.env' or path.name.startswith('.env.')) and path.name not in {'.env.example', '.env.EXAMPLE'})
        forbidden_name = forbidden_name or path.name.startswith(('auth.json', 'state.db')) or path.suffix in {'.pem', '.key', '.sqlite', '.sqlite3', '.db'}
        require(not forbidden_name and not (set(rel.parts[:-1]) & FORBIDDEN_DIRS), f'Private path in source: {rel}')
        content = path.read_text(encoding='utf-8')
        require(not any(pattern.search(content) for pattern in SECRET_PATTERNS), f'Possible credential in source: {rel}')
        if path.suffix == '.json':
            json.loads(content)
    print(f'PASS: {len(agents)} profiles, {len(skills)} canonical skills, {len(groups)} groups, {len(routines)} inactive routines; complete bundles, versions and privacy checks.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print('FAIL:', exc, file=sys.stderr)
        raise SystemExit(1)

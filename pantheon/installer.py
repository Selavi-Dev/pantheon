"""Native Hermes adapter. No force, silent confirmation, or gateway activation."""
from pathlib import Path
import json
import re
import os
import shutil
import subprocess
import tempfile
from . import __version__

RESOURCES = Path(__file__).resolve().parent / 'resources'
PRESETS = {
    'executive': ('hermes', 'athena', 'argus', 'themis'),
    'developer': ('hermes', 'hephaestus', 'themis', 'mnemosyne'),
    'creative': ('hermes', 'apollo', 'athena'),
    'academy': ('hermes', 'socrates', 'athena', 'mnemosyne'),
    'research': ('argus', 'themis', 'mnemosyne'),
    'full': ('hermes', 'athena', 'argus', 'themis', 'hephaestus', 'apollo', 'mnemosyne', 'socrates'),
}

def registry(name):
    return json.loads((RESOURCES / 'registry' / f'{name}.json').read_text(encoding='utf-8'))

def select(preset=None, agents=None):
    if preset and agents: raise ValueError('Choose either --preset or --agents, not both.')
    if preset and preset not in PRESETS: raise ValueError(f'Unknown preset: {preset}')
    requested = agents.split(',') if agents is not None else PRESETS[preset or 'executive']
    ids = tuple(dict.fromkeys(x.strip().lower() for x in requested))
    if not ids or any(x not in PRESETS['full'] for x in ids):
        raise ValueError('Unknown or empty agent selection; use pantheon agents.')
    return ids

def data_root():
    return Path(os.environ.get('PANTHEON_HOME', str(Path.home()/'.pantheon'))).expanduser().resolve()

def source_path(agent):
    if agent not in PRESETS['full']: raise ValueError('Unknown agent')
    return data_root() / 'distributions' / __version__ / agent

def tree_bytes(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*') if p.is_file()}

def stage(agent):
    """Keep an immutable versioned local origin for Hermes; never replace user edits."""
    source = RESOURCES / 'profiles' / agent
    dest = source_path(agent)
    if not (source/'distribution.yaml').is_file(): raise RuntimeError('Packaged distribution missing')
    if dest.is_symlink(): raise RuntimeError(f'Refusing symlinked distribution: {dest}')
    if dest.exists():
        if not dest.is_dir() or tree_bytes(dest) != tree_bytes(source):
            raise RuntimeError(f'Existing source differs; review manually: {dest}')
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=dest.parent) as tmp:
        work = Path(tmp)/'bundle'
        shutil.copytree(source, work)
        work.rename(dest)
    return dest

def executable():
    path = shutil.which('hermes')
    if not path: raise RuntimeError('Hermes CLI not found on PATH; install upstream Hermes first.')
    return path

def run_native(args, capture=False):
    return subprocess.run([executable(), *args], check=True, text=True, encoding='utf-8', errors='replace',
                          capture_output=capture, timeout=30 if capture else None)

_LABELLED = re.compile(r'^(?P<display>.+?) \((?P<id>[^()\s]+)\)\s+(?P<rest>.*)$')

def _parse_profile_row(line):
    """(profile_id, gateway_state) for one `hermes profile list` row, else None.

    Hermes prints ` <marker><label> <model> <gateway> <alias> <distribution>`, where the label is
    the bare id or `display name (id)`. Only the Gateway column is read, never the alias.
    """
    body = line.strip().lstrip('\u25c6*').strip()
    if not body or body.startswith('\u2500') or body.split()[:3] == ['Profile', 'Model', 'Gateway']:
        return None
    m = _LABELLED.match(body)
    if m:
        pid, rest = m.group('id'), m.group('rest').split()
    else:
        parts = body.split()
        pid, rest = parts[0], parts[1:]
    if len(rest) < 2 or rest[1] not in ('running', 'stopped'):
        return None
    return pid, rest[1]

def running_gateways():
    """Profile ids whose gateway Hermes reports as running, parsed from `hermes profile list`.

    Best effort: returns [] when Hermes is missing or the output is unrecognised. A running
    default gateway in current Hermes multiplexes named profiles, so a profile installed while
    it runs can be served at once (no bot token in Pantheon profiles, so no platform connects).
    """
    try:
        out = run_native(['profile', 'list'], capture=True).stdout or ''
    except (OSError, RuntimeError, subprocess.SubprocessError):
        return []
    rows = (_parse_profile_row(line) for line in out.splitlines())
    return [pid for pid, state in filter(None, rows) if state == 'running']

def require_distributions():
    run_native(['profile', 'install', '--help'], capture=True)
    run_native(['profile', 'update', '--help'], capture=True)

def install_agents(agents, alias=False):
    require_distributions()
    # Hermes itself refuses existing names without --force. Never bypass that guard.
    for agent in agents:
        command = ['profile', 'install', str(stage(agent))]
        if alias: command.append('--alias')
        run_native(command)

def profile_name(agent):
    if agent not in PRESETS['full']: raise ValueError('Unknown agent')
    return 'pantheon-' + agent

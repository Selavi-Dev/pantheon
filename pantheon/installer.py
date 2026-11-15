"""Native Hermes adapter. No force, silent confirmation, or gateway activation."""
from pathlib import Path
import json
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
    return subprocess.run([executable(), *args], check=True, text=True,
                          capture_output=capture, timeout=30 if capture else None)

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

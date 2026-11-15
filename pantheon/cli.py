"""Pantheon's opt-in CLI. Native Hermes handles profile and credential operations."""
from pathlib import Path
from typing import Optional
import json
import shlex
import subprocess
import typer
from rich.console import Console
from rich.table import Table
from . import __version__, installer as i

app = typer.Typer(no_args_is_help=True, add_completion=False, help='Install and inspect Pantheon specialist agents.')
console = Console()

def fail(exc):
    console.print(f'Error: {exc}', markup=False, style='red')
    raise typer.Exit(1)

def selection(preset, agents):
    try: return i.select(preset, agents)
    except ValueError as exc: fail(exc)

def native(args):
    try: i.run_native(args)
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc: fail(exc)

@app.command()
def version():
    console.print(__version__)

@app.command()
def agents():
    """List bundled agents (not installed status)."""
    table = Table('ID', 'Profile', 'Role')
    for a in i.registry('agents')['agents']: table.add_row(a['id'], a['profile'], a['role'])
    console.print(table)

@app.command()
def groups():
    """Print proposed native room memberships; does not create rooms."""
    console.print_json(json.dumps(i.registry('groups')))

@app.command()
def routines():
    """Print inactive routine definitions; does not create jobs."""
    console.print_json(json.dumps(i.registry('routines')))

GATEWAY_NOTE = ('A Hermes gateway is already running ({names}). Current Hermes multiplexes named profiles '
                'from the default gateway, so profiles installed now may be served by it immediately. '
                'Pantheon profiles ship no bot tokens or jobs; stop it first with `hermes gateway stop` '
                'if nothing should be served.')

def warn_running_gateway():
    names = i.running_gateways()
    if names:
        console.print('Warning: ' + GATEWAY_NOTE.format(names=', '.join(names)), markup=False, style='yellow')
    return names

def install_plan(ids, apply, alias):
    for a in ids:
        command = ['hermes','profile','install', str(i.source_path(a))]
        if alias: command.append('--alias')
        console.print(shlex.join(command), markup=False)
    if not apply:
        console.print('Plan only. No files staged or profiles installed. Use --apply to proceed.')
        return
    warn_running_gateway()
    try: i.install_agents(ids, alias)
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc: fail(exc)
    console.print('Native install commands completed. Configure models and review tools before starting agents.')
    served = sorted(set(i.running_gateways()) & {i.profile_name(a) for a in ids})
    if served:
        console.print('Now served by a running gateway: ' + ', '.join(served) + '. Pantheon started no gateway; '
                      'run `hermes gateway stop` or remove them from the multiplexer if unintended.', markup=False, style='yellow')

@app.command()
def install(preset: Optional[str] = None, agents: Optional[str] = None,
            apply: bool = typer.Option(False, '--apply'), alias: bool = typer.Option(False, '--alias')):
    """Plan installation; apply explicitly, retaining native confirmations."""
    install_plan(selection(preset, agents), apply, alias)

@app.command()
def init(preset: Optional[str] = None, apply: bool = typer.Option(False, '--apply')):
    """Guided preset selection. Default is a dry run."""
    if preset is None:
        console.print('Presets: ' + ', '.join(i.PRESETS))
        preset = typer.prompt('Preset', default='executive')
    ids = selection(preset, None)
    console.print('Selected: ' + ', '.join(ids))
    install_plan(ids, apply, False)
    console.print('Next: pantheon configure --agent <id>; pantheon doctor. Pantheon starts no gateways or routines.')

@app.command()
def doctor():
    """Check bundled resources and native distribution command availability."""
    try:
        for a in i.PRESETS['full']:
            for f in ('distribution.yaml','SOUL.md','config.yaml'):
                if not (i.RESOURCES/'profiles'/a/f).is_file(): raise RuntimeError(f'Missing resource: {a}/{f}')
        console.print(f'Pantheon {__version__}: eight profile bundles present.')
        i.require_distributions()
        result = i.run_native(['--version'], capture=True)
        console.print(result.stdout.strip() or result.stderr.strip(), markup=False)
        console.print('Hermes distribution command help checks passed. Live compatibility and permissions still require testing.')
        warn_running_gateway()
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc: fail(exc)

@app.command()
def configure(agent: str = typer.Option(..., '--agent'), apply: bool = typer.Option(False, '--apply')):
    """Delegate model/configuration setup to Hermes, without gateway start."""
    name = 'pantheon-' + selection(None, agent)[0]
    if ',' in agent: fail(ValueError('Configure one agent at a time.'))
    command = ['-p', name, 'setup']
    console.print(shlex.join(['hermes',*command]), markup=False)
    if apply: native(command)
    else: console.print('Plan only. Use --apply to open native setup; skip gateway setup if not desired.')

@app.command()
def status(agent: Optional[str] = None):
    """Inspect native installed profiles or one named Pantheon profile."""
    if agent is None: native(['profile','list'])
    else:
        ids = selection(None, agent)
        if len(ids) != 1: fail(ValueError('Specify one agent.'))
        native(['profile','show',i.profile_name(ids[0])])

@app.command()
def update(agent: str = typer.Option(..., '--agent'), apply: bool = typer.Option(False, '--apply')):
    """Update from the profile's recorded native origin (not a wheel migration)."""
    ids = selection(None, agent)
    if len(ids) != 1: fail(ValueError('Specify one agent.'))
    name = i.profile_name(ids[0])
    console.print('Native update follows the recorded origin. Bundled local origins are versioned and do not automatically migrate on wheel upgrades.')
    console.print(f'hermes profile update {name}')
    if apply:
        native(['profile','info',name])
        if not typer.confirm('Update from this recorded origin? Local SOUL/skill edits may be replaced.', default=False):
            raise typer.Abort()
        native(['profile','update',name])
    else: console.print('Plan only. Use --apply after review and backup.')

@app.command()
def backup(agent: str = typer.Option(..., '--agent'), output: Path = typer.Option(..., '--output'),
           apply: bool = typer.Option(False, '--apply')):
    """Export a native profile snapshot; excludes credentials, may contain private data."""
    ids = selection(None, agent)
    if len(ids) != 1: fail(ValueError('Specify one agent.'))
    if output.exists() or output.is_symlink(): fail(ValueError('Output already exists. Choose a new file.'))
    if not output.parent.is_dir(): fail(ValueError('Output parent must exist.'))
    command = ['profile','export',i.profile_name(ids[0]),'--output',str(output.resolve())]
    console.print(shlex.join(['hermes',*command]), markup=False)
    if apply: native(command)
    else: console.print('Plan only. Use --apply. Treat exported history as private; credentials are not backed up.')

if __name__ == '__main__': app()

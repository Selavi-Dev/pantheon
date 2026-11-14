"""Print or interactively install local Hermes distributions; no force or gateway start."""
import argparse, json, shlex, shutil, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    agents=json.loads((ROOT/'registry/agents.json').read_text())['agents']
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--agent',action='append',choices=[x['id'] for x in agents]); p.add_argument('--apply',action='store_true')
    a=p.parse_args()
    if a.apply and not shutil.which('hermes'): p.error('Hermes CLI not found')
    for agent in agents:
        if a.agent and agent['id'] not in a.agent: continue
        command=['hermes','profile','install',str(ROOT/'profiles'/agent['id']),'--alias']
        print(shlex.join(command),flush=True)
        if a.apply: subprocess.run(command,check=True)
    if not a.apply: print('Dry run only. Use --apply after inventory and review.')
if __name__=='__main__': main()

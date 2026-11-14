"""Generate paused, local-only cron commands after exact purpose-key conflict checks."""
import argparse,json,shlex
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]

def plan(reg,inventory,only=None,timezone=None):
    tz=timezone or reg['timezone']; ZoneInfo(tz)
    if not isinstance(inventory,dict) or not isinstance(inventory.get('routines'),list): raise ValueError('Inventory must contain routines list')
    occupied=set(); ids=set()
    for r in inventory['routines']:
        if not isinstance(r,dict) or not all(isinstance(r.get(k),str) and r[k].strip() for k in ('id','owner','purpose_key')) or type(r.get('enabled')) is not bool: raise ValueError('Invalid inventory entry; id, owner, purpose_key, enabled required')
        if r['id'] in ids: raise ValueError('Duplicate inventory ID')
        ids.add(r['id'])
        # Paused jobs retain ownership; resuming one must not create duplicates.
        occupied.add(r['purpose_key'].strip().casefold())
    lines=[]; conflicts=[]
    for r in reg['routines']:
        if only and r['id'] not in only: continue
        if r['id'] in ids or r['purpose_key'].strip().casefold() in occupied:
            conflicts.append(r['id']); continue
        if not r['schedule']: continue
        cmd=['hermes','-p','pantheon-'+r['owner'],'cron','create',r['schedule'],r['prompt'],'--name',r['id'],'--skill',r['skill'],'--timezone',tz,'--deliver','local','--paused']
        if r.get('catch_up') is False:
            cmd.extend(['--catch-up','off'])
        if 'grace_minutes' in r:
            grace=r['grace_minutes']
            if type(grace) is not int or grace<0: raise ValueError('grace_minutes must be a nonnegative integer')
            cmd.extend(['--grace-minutes',str(grace)])
        lines.append(shlex.join(cmd))
    return lines,conflicts

def main():
    reg=json.loads((ROOT/'registry/routines.json').read_text())
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--inventory',required=True); p.add_argument('--routine',action='append',choices=[x['id'] for x in reg['routines']]); p.add_argument('--timezone')
    a=p.parse_args()
    try: lines,conflicts=plan(reg,json.loads(Path(a.inventory).read_text()),a.routine,a.timezone)
    except (ValueError,OSError,KeyError) as e: p.error(str(e))
    for c in conflicts: print('# BLOCKED: existing ID or reserved equivalent purpose:',c)
    for l in lines: print(l)
    print('# Plan only. Nothing created or activated. Verify all existing schedules, sources, and destination before executing.')
    return 1 if conflicts else 0
if __name__=='__main__': raise SystemExit(main())

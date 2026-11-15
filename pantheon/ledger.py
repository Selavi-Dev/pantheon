"""Local-only reference ledger. No dispatch, authentication, or external side effects."""
import argparse
import hashlib
import json
import os
import sqlite3
import time
from datetime import datetime
from pathlib import Path

FIELDS = {'schema_version','handoff_id','idempotency_key','source_agent','target_agent','entity','project','objective','constraints','acceptance_criteria','evidence','due_at','authorization_required'}


def nonblank(value):
    return isinstance(value, str) and bool(value.strip())


def validate_proposal(p):
    if not isinstance(p, dict) or set(p) != FIELDS or p['schema_version'] != '1.0' or p['authorization_required'] is not True:
        raise ValueError('Invalid proposal fields, version or authorization requirement')
    for key in FIELDS - {'constraints','acceptance_criteria','evidence','due_at','authorization_required'}:
        if not nonblank(p[key]):
            raise ValueError(f'Invalid {key}')
    if p['source_agent'] == p['target_agent']:
        raise ValueError('Self-handoff is forbidden')
    for key in ('constraints','acceptance_criteria','evidence'):
        if not isinstance(p[key], list) or not all(nonblank(x) for x in p[key]) or (key != 'evidence' and not p[key]):
            raise ValueError(f'Invalid {key}')
    if p['due_at'] is not None:
        if not nonblank(p['due_at']):
            raise ValueError('Invalid due_at')
        dt = datetime.fromisoformat(p['due_at'].replace('Z', '+00:00'))
        if dt.tzinfo is None:
            raise ValueError('due_at must be offset-aware')
    return p


def canonical(p):
    return json.dumps(p, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


class Ledger:
    def __init__(self, path):
        if str(path) != ':memory:':
            Path(path).parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            # Pre-create only new databases with private evidence permissions.
            # Existing installations retain their operator-managed permissions.
            try:
                fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            except FileExistsError:
                pass
            else:
                os.close(fd)
        self.conn = sqlite3.connect(path, timeout=15, isolation_level=None)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript('''
        CREATE TABLE IF NOT EXISTS handoffs (
          id TEXT PRIMARY KEY, idem TEXT UNIQUE NOT NULL, payload TEXT NOT NULL,
          digest TEXT NOT NULL, state TEXT NOT NULL, approved_by TEXT,
          expires REAL, claimant TEXT, completion_evidence TEXT, reviewer TEXT,
          verification_evidence TEXT
        );
        CREATE TABLE IF NOT EXISTS events (
          seq INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT NOT NULL,
          event TEXT NOT NULL, actor TEXT NOT NULL, at REAL NOT NULL, details TEXT NOT NULL
        );''')

    def close(self):
        self.conn.close()

    def _event(self, id, action, actor, details=''):
        self.conn.execute('INSERT INTO events(id,event,actor,at,details) VALUES(?,?,?,?,?)', (id,action,actor,time.time(),details))

    def _row(self,id):
        row = self.conn.execute('SELECT * FROM handoffs WHERE id=?',(id,)).fetchone()
        if row is None:
            raise ValueError('Unknown handoff')
        return row

    def show(self,id):
        owns_snapshot = not self.conn.in_transaction
        if owns_snapshot:
            self.conn.execute('BEGIN')
        try:
            row=dict(self._row(id)); row['payload']=json.loads(row['payload'])
            row['events']=[dict(x) for x in self.conn.execute('SELECT * FROM events WHERE id=? ORDER BY seq',(id,))]
            if owns_snapshot:
                self.conn.execute('COMMIT')
            return row
        except BaseException:
            if owns_snapshot and self.conn.in_transaction:
                self.conn.execute('ROLLBACK')
            raise

    def _transaction(self, operation):
        self.conn.execute('BEGIN IMMEDIATE')
        try:
            result=operation()
            self.conn.execute('COMMIT')
            return result
        except BaseException:
            self.conn.execute('ROLLBACK')
            raise

    def propose(self,p):
        validate_proposal(p)
        payload=canonical(p); digest=hashlib.sha256(payload.encode()).hexdigest(); id=p['handoff_id']; idem=p['idempotency_key']
        def op():
            existing=self.conn.execute('SELECT * FROM handoffs WHERE id=? OR idem=?',(id,idem)).fetchall()
            if existing:
                if len(existing)==1 and existing[0]['id']==id and existing[0]['digest']==digest:
                    return self.show(id)
                raise ValueError('Duplicate ID or idempotency key with different proposal')
            self.conn.execute('INSERT INTO handoffs(id,idem,payload,digest,state) VALUES(?,?,?,?,?)',(id,idem,payload,digest,'proposed'))
            self._event(id,'proposed',p['source_agent'],digest)
            return self.show(id)
        return self._transaction(op)

    def approve(self,id,digest,actor,ttl):
        if not nonblank(actor) or type(ttl) is not int or not 1<=ttl<=86400:
            raise ValueError('Actor and TTL of 1–86400 seconds required')
        def op():
            r=self._row(id); p=json.loads(r['payload'])
            if r['state']!='proposed' or r['digest']!=digest:
                raise ValueError('Approval requires proposed state and matching digest')
            if actor in (p['source_agent'],p['target_agent']):
                raise ValueError('Agent self-approval forbidden; use trusted operator')
            self.conn.execute('UPDATE handoffs SET state=?,approved_by=?,expires=? WHERE id=?',('approved',actor,time.time()+ttl,id))
            self._event(id,'approved',actor,digest)
            return self.show(id)
        return self._transaction(op)

    def revoke(self,id,actor):
        def op():
            r=self._row(id)
            if r['state']!='approved' or actor!=r['approved_by']:
                raise ValueError('Only approving operator may revoke an unclaimed approval')
            self.conn.execute('UPDATE handoffs SET state=? WHERE id=?',('revoked',id)); self._event(id,'revoked',actor)
            return self.show(id)
        return self._transaction(op)

    def claim(self,id,actor):
        def op():
            r=self._row(id); p=json.loads(r['payload'])
            if r['state']!='approved' or r['expires']<=time.time() or actor!=p['target_agent']:
                raise ValueError('Claim requires unexpired approval and exact target; one claim only')
            self.conn.execute('UPDATE handoffs SET state=?,claimant=? WHERE id=?',('claimed',actor,id)); self._event(id,'claimed',actor)
            return self.show(id)
        return self._transaction(op)

    def complete(self,id,actor,evidence):
        if not nonblank(evidence): raise ValueError('Completion evidence required')
        def op():
            r=self._row(id)
            if r['state']!='claimed' or r['claimant']!=actor:
                raise ValueError('Only the claimant can record completion')
            self.conn.execute('UPDATE handoffs SET state=?,completion_evidence=? WHERE id=?',('completed_claimed',evidence,id)); self._event(id,'completed_claimed',actor,evidence)
            return self.show(id)
        return self._transaction(op)

    def verify(self,id,actor,evidence):
        if not nonblank(actor) or not nonblank(evidence): raise ValueError('Reviewer and verification evidence required')
        def op():
            r=self._row(id); p=json.loads(r['payload'])
            if r['state']!='completed_claimed' or actor in (r['claimant'],p['source_agent']):
                raise ValueError('Independent reviewer required after claimed completion')
            self.conn.execute('UPDATE handoffs SET state=?,reviewer=?,verification_evidence=? WHERE id=?',('verified',actor,evidence,id)); self._event(id,'verified',actor,evidence)
            return self.show(id)
        return self._transaction(op)


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--db',required=True); sub=p.add_subparsers(dest='action',required=True)
    a=sub.add_parser('propose'); a.add_argument('file')
    for action in ('show','approve','revoke','claim','complete','verify'):
        a=sub.add_parser(action); a.add_argument('id')
        if action!='show': a.add_argument('--actor',required=True)
        if action=='approve': a.add_argument('--digest',required=True); a.add_argument('--ttl',type=int,required=True)
        if action in ('complete','verify'): a.add_argument('--evidence',required=True)
    args=p.parse_args(); l=Ledger(args.db)
    try:
        if args.action=='propose': result=l.propose(json.loads(Path(args.file).read_text()))
        else:
            kw={k:v for k,v in vars(args).items() if k not in ('db','action','id')}
            result=getattr(l,args.action)(args.id,**kw)
        print(json.dumps(result,indent=2))
    except (ValueError,OSError,sqlite3.Error) as e:
        p.exit(1,f'Error: {e}\n')
    finally: l.close()

if __name__=='__main__': main()

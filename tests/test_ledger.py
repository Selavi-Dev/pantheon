import copy,json,tempfile,time,unittest
from pathlib import Path
from pantheon.ledger import Ledger

ROOT=Path(__file__).resolve().parents[1]
class LedgerTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.path=Path(self.tmp.name)/'ledger.sqlite'; self.l=Ledger(self.path); self.p=json.loads((ROOT/'examples/handoff.json').read_text()); self.id=self.p['handoff_id']
    def tearDown(self): self.l.close(); self.tmp.cleanup()
    def approve(self):
        d=self.l.propose(self.p)['digest']; return self.l.approve(self.id,d,'operator',60)
    def test_lifecycle(self):
        self.approve(); self.l.claim(self.id,'grokbot'); self.l.complete(self.id,'grokbot','artifact:example'); r=self.l.verify(self.id,'themis','audit:example'); self.assertEqual(r['state'],'verified'); self.assertEqual(len(r['events']),5)
    def test_exact_replay_and_conflict(self):
        r=self.l.propose(self.p); self.assertEqual(r,self.l.propose(self.p)); p=copy.deepcopy(self.p); p['objective']='different'; self.assertRaises(ValueError,self.l.propose,p); p['handoff_id']='other'; self.assertRaises(ValueError,self.l.propose,p)
    def test_no_unapproved_claim(self):
        self.l.propose(self.p); self.assertRaises(ValueError,self.l.claim,self.id,'grokbot')
    def test_wrong_digest(self):
        self.l.propose(self.p); self.assertRaises(ValueError,self.l.approve,self.id,'wrong','operator',60)
    def test_self_approval(self):
        d=self.l.propose(self.p)['digest']; self.assertRaises(ValueError,self.l.approve,self.id,d,'hephaestus',60)
    def test_expiry(self):
        self.approve(); self.l.conn.execute('UPDATE handoffs SET expires=?',(time.time()-1,)); self.assertRaises(ValueError,self.l.claim,self.id,'grokbot')
    def test_revocation(self):
        self.approve(); self.l.revoke(self.id,'operator'); self.assertRaises(ValueError,self.l.claim,self.id,'grokbot')
    def test_wrong_target_and_duplicate_claim(self):
        self.approve(); self.assertRaises(ValueError,self.l.claim,self.id,'other'); self.l.claim(self.id,'grokbot'); other=Ledger(self.path)
        try: self.assertRaises(ValueError,other.claim,self.id,'grokbot')
        finally: other.close()
    def test_independent_verification_and_evidence(self):
        self.approve(); self.l.claim(self.id,'grokbot'); self.assertRaises(ValueError,self.l.complete,self.id,'grokbot',''); self.l.complete(self.id,'grokbot','artifact:x'); self.assertRaises(ValueError,self.l.verify,self.id,'grokbot','audit:x'); self.assertRaises(ValueError,self.l.verify,self.id,'hephaestus','audit:x'); self.assertRaises(ValueError,self.l.verify,self.id,'themis','')
    def test_invalid_proposal(self):
        self.p['authorization_required']=False; self.assertRaises(ValueError,self.l.propose,self.p)

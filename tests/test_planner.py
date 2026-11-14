import json,shlex,unittest
from pathlib import Path
from scripts.plan_routines import plan
ROOT=Path(__file__).resolve().parents[1]
class PlannerTest(unittest.TestCase):
    def setUp(self): self.reg=json.loads((ROOT/'registry/routines.json').read_text())
    def test_paused_local(self):
        lines,conflicts=plan(self.reg,{'routines':[]}); self.assertEqual(len(lines),21); self.assertFalse(conflicts); self.assertTrue(all('--paused' in x and '--deliver local' in x for x in lines))
    def test_equivalent_purpose(self):
        inv={'routines':[{'id':'G-1','owner':'grokbot','purpose_key':self.reg['routines'][0]['purpose_key'].upper(),'enabled':True}]}; lines,conflicts=plan(self.reg,inv,['H-01']); self.assertEqual(lines,[]); self.assertEqual(conflicts,['H-01'])
    def test_same_id_paused(self):
        inv={'routines':[{'id':'H-01','owner':'hermes','purpose_key':'other','enabled':False}]}; self.assertEqual(plan(self.reg,inv,['H-01'])[1],['H-01'])
    def test_equivalent_paused_purpose_remains_owned(self):
        inv={'routines':[{'id':'G-PAUSED','owner':'grokbot','purpose_key':' EXECUTIVE.MORNING-BRIEF ','enabled':False}]}
        self.assertEqual(plan(self.reg,inv,['H-01']), ([], ['H-01']))
    def test_improvement_jobs_disable_native_catch_up(self):
        lines, conflicts = plan(self.reg, {'routines': []},
            ['pantheon-self-improvement-daily', 'pantheon-self-improvement-weekly'])
        self.assertFalse(conflicts)
        self.assertEqual(len(lines), 2)
        for line in lines:
            command = shlex.split(line)
            self.assertIn('--catch-up', command)
            self.assertEqual(command[command.index('--catch-up') + 1], 'off')
            self.assertIn('--grace-minutes', command)
            self.assertEqual(command[command.index('--grace-minutes') + 1], '0')
    def test_bad_inventory(self): self.assertRaises(ValueError,plan,self.reg,{'routines':[{}]})

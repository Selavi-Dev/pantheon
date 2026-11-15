import copy
import json
from pathlib import Path
import tempfile
import unittest

from pantheon import self_improvement as si

ROOT = Path(__file__).resolve().parents[1]


def fixture(name):
    return json.loads((ROOT / 'examples' / f'self-improvement-{name}.json').read_text(encoding='utf-8'))


class ImprovementTests(unittest.TestCase):
    def setUp(self):
        self.state = {}
        self.p = fixture('proposal')
        self.e = fixture('evaluation')
        self.r = fixture('review')
        self.pid = self.p['id']
        si.add(self.state, self.p)

    def evaluated(self):
        return si.evaluate(self.state, self.pid, self.e)

    def reviewed(self):
        self.evaluated()
        return si.review(self.state, self.pid, self.r)

    def approval(self):
        return {'administrator': 'operator-001', 'candidate_sha256': self.p['candidate_sha256'], 'scope': self.p['scope'], 'decision': 'approve', 'evidence_ref': 'private:approval-record'}

    def test_good_evaluation(self):
        self.assertEqual(self.evaluated()['status'], 'evaluated')
        self.assertEqual(self.state[self.pid]['evaluation']['observed_improvement'], 5)

    def test_duplicate_id(self):
        with self.assertRaises(ValueError):
            si.add(self.state, self.p)

    def test_duplicate_finding(self):
        p = {**self.p, 'id': 'SI-002'}
        with self.assertRaises(ValueError):
            si.add(self.state, p)

    def test_path_traversal_id(self):
        with self.assertRaises(ValueError):
            si.add({}, {**self.p, 'id': '../../evil'})

    def test_wrong_evaluator(self):
        self.e['evaluator'] = 'hephaestus'
        with self.assertRaises(ValueError):
            self.evaluated()

    def test_digest_mismatch(self):
        self.e['candidate_sha256'] = 'b' * 64
        with self.assertRaises(ValueError):
            self.evaluated()

    def test_insufficient_samples(self):
        self.e['sample_count'] = 1
        self.assertEqual(self.evaluated()['status'], 'evaluation_failed')

    def test_regression(self):
        self.e['regressions_pass'] = False
        self.assertEqual(self.evaluated()['status'], 'evaluation_failed')

    def test_guardrail(self):
        self.e['guardrails_pass'] = False
        self.assertEqual(self.evaluated()['status'], 'evaluation_failed')

    def test_string_boolean_rejected(self):
        self.e['guardrails_pass'] = 'false'
        with self.assertRaises(ValueError):
            self.evaluated()

    def test_insufficient_improvement(self):
        self.e['candidate'] = 9
        self.assertEqual(self.evaluated()['status'], 'evaluation_failed')

    def test_grokbot_overlap(self):
        self.r['grokbot_overlap'] = True
        self.assertEqual(self.reviewed()['status'], 'rejected')

    def test_governance_failure(self):
        self.r['governance_pass'] = False
        self.assertEqual(self.reviewed()['status'], 'rejected')

    def test_review_before_evaluation(self):
        with self.assertRaises(ValueError):
            si.review(self.state, self.pid, self.r)

    def test_approval_before_review(self):
        with self.assertRaises(ValueError):
            si.approve(self.state, self.pid, self.approval())

    def test_synthetic_cannot_be_approved(self):
        self.reviewed()
        with self.assertRaisesRegex(ValueError, 'synthetic'):
            si.approve(self.state, self.pid, self.approval())

    def real_review(self):
        # Test-only references, deliberately not represented as production data.
        self.state = {}
        self.p['evidence_refs'] = ['test:observation']
        self.e['comparison_ref'] = 'test:comparison'
        self.r['evidence_ref'] = 'test:review'
        si.add(self.state, self.p)
        self.reviewed()

    def test_approval_record(self):
        self.real_review()
        result = si.approve(self.state, self.pid, self.approval())
        self.assertEqual(result['status'], 'approval_recorded')
        self.assertNotIn('deployed', result)

    def test_agent_cannot_approve(self):
        self.real_review()
        with self.assertRaises(ValueError):
            si.approve(self.state, self.pid, {**self.approval(), 'administrator': 'hermes'})

    def test_scope_mismatch(self):
        self.real_review()
        with self.assertRaises(ValueError):
            si.approve(self.state, self.pid, {**self.approval(), 'scope': 'all permissions'})

    def test_export_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            path = si.export_lesson(self.state, self.pid, Path(temp))
            self.assertIn('not a validated production outcome', path.read_text(encoding='utf-8'))
            with self.assertRaises(FileExistsError):
                si.export_lesson(self.state, self.pid, Path(temp))

    def test_state_roundtrip(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'state.json'
            si.save(path, self.state)
            self.assertEqual(si.load_json(path), self.state)

    def test_higher_metric(self):
        state = {}
        si.add(state, {**self.p, 'direction': 'higher'})
        self.e['baseline'], self.e['candidate'] = 5, 10
        self.assertEqual(si.evaluate(state, self.pid, self.e)['status'], 'evaluated')


if __name__ == '__main__':
    unittest.main()

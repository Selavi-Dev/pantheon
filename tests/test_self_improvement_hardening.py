"""Regression checks for local review-record integrity, not authentication."""
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest

from pantheon import self_improvement as si

ROOT = Path(__file__).resolve().parents[1]


def reviewed_state():
    records = [json.loads((ROOT / 'examples' / f'self-improvement-{kind}.json').read_text())
               for kind in ('proposal', 'evaluation', 'review')]
    proposal, evaluation, review = records
    proposal['evidence_refs'] = ['test:observation']
    evaluation['comparison_ref'] = 'test:comparison'
    review['evidence_ref'] = 'test:review'
    state = {}
    si.add(state, proposal)
    si.evaluate(state, proposal['id'], evaluation)
    si.review(state, proposal['id'], review)
    return state, proposal


class ImprovementHardeningTests(unittest.TestCase):
    def test_unknown_export_leaves_no_empty_note(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            with self.assertRaises(KeyError):
                si.export_lesson({}, 'SI-NOTFOUND', directory)
            self.assertFalse((directory / 'SI-NOTFOUND.md').exists())

    def test_all_agent_profile_aliases_are_rejected_as_administrators(self):
        for agent in sorted(si.AGENTS):
            with self.subTest(agent=agent):
                state, proposal = reviewed_state()
                decision = {'administrator': f' PANTHEON-{agent.upper()} ',
                            'candidate_sha256': proposal['candidate_sha256'],
                            'scope': proposal['scope'], 'decision': 'approve',
                            'evidence_ref': 'test:approval'}
                with self.assertRaises(ValueError):
                    si.approve(state, proposal['id'], decision)

    def test_cli_rejects_forged_reviewed_state_before_recording_approval(self):
        state, proposal = reviewed_state()
        del state[proposal['id']]['evaluation']
        decision = {'administrator': 'operator-001',
                    'candidate_sha256': proposal['candidate_sha256'],
                    'scope': proposal['scope'], 'decision': 'approve',
                    'evidence_ref': 'test:approval'}
        with tempfile.TemporaryDirectory() as temp:
            state_path, decision_path = Path(temp) / 'state.json', Path(temp) / 'decision.json'
            original = json.dumps(state)
            state_path.write_text(original)
            decision_path.write_text(json.dumps(decision))
            with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit) as stopped:
                    si.main(['--state', str(state_path), 'approve', proposal['id'], str(decision_path)])
            self.assertEqual(stopped.exception.code, 2)
            self.assertEqual(state_path.read_text(), original)

    def test_valid_state_remains_valid_when_json_object_keys_are_reordered(self):
        state, proposal = reviewed_state()
        rejected = {'administrator': 'operator-001',
                    'candidate_sha256': proposal['candidate_sha256'],
                    'scope': proposal['scope'], 'decision': 'reject',
                    'evidence_ref': 'test:rejection'}
        si.approve(state, proposal['id'], rejected)
        replacement = copy.deepcopy(proposal)
        replacement['id'] = 'SI-REPLACEMENT'
        si.add(state, replacement)
        reordered = dict(reversed(list(state.items())))
        self.assertEqual(si.validate_state(reordered), reordered)


if __name__ == '__main__':
    unittest.main()

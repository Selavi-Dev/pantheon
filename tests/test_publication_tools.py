"""Regression checks for safe source preparation and complete skill bundles."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PublicationToolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / 'repo'
        shutil.copytree(ROOT, self.repo, ignore=shutil.ignore_patterns('.git', '__pycache__'))

    def run_script(self, name, optimized=False):
        cmd = [sys.executable]
        if optimized:
            cmd.append('-O')
        return subprocess.run(cmd + [str(self.repo / 'scripts' / name)],
                              cwd=self.repo, text=True, capture_output=True)

    def test_sync_copies_skill_support_files(self):
        # A bundled skill must retain the local resources referenced by SKILL.md.
        agents_path = self.repo / 'registry/agents.json'
        agents = json.loads(agents_path.read_text())
        agents['agents'][0]['skills'].append('fixture-resource')
        agents_path.write_text(json.dumps(agents))
        skill = self.repo / 'skills/fixture-resource'
        (skill / 'references').mkdir(parents=True)
        (skill / 'SKILL.md').write_text('Read references/check.md')
        (skill / 'references/check.md').write_text('Retain this evidence checklist.\n')
        result = self.run_script('sync_templates.py')
        self.assertEqual(result.returncode, 0, result.stderr)
        bundled = self.repo / 'profiles/hermes/skills/fixture-resource/references/check.md'
        self.assertTrue(bundled.is_file(), 'support file omitted from installed skill')
        self.assertEqual(bundled.read_text(), 'Retain this evidence checklist.\n')

    def test_validator_rejects_profile_drift_under_optimized_python(self):
        (self.repo / 'profiles/hermes/SOUL.md').write_text('Unreviewed replacement')
        result = self.run_script('validate.py', optimized=True)
        self.assertNotEqual(result.returncode, 0, result.stdout)

    def test_validator_rejects_private_environment_variants(self):
        (self.repo / '.env.production').write_text('EXAMPLE_ONLY=fixture\n')
        result = self.run_script('validate.py', optimized=True)
        self.assertNotEqual(result.returncode, 0, result.stdout)

    def test_validator_accepts_clean_integrated_candidate(self):
        result = self.run_script('validate.py', optimized=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_validator_rejects_missing_support_resource(self):
        (self.repo / 'profiles/hermes/skills/self-improvement/evaluation.md').unlink()
        result = self.run_script('validate.py', optimized=True)
        self.assertNotEqual(result.returncode, 0, result.stdout)


if __name__ == '__main__':
    unittest.main()

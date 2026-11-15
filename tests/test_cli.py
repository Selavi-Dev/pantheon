import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from typer.testing import CliRunner
from pantheon.cli import app
from pantheon import installer as i

class CLITests(unittest.TestCase):
    def setUp(self): self.runner = CliRunner()
    def test_presets(self):
        self.assertEqual(i.select('full'), i.PRESETS['full'])
        self.assertEqual(i.select(agents=' Athena,athena,THEMIS '), ('athena','themis'))
        with self.assertRaises(ValueError): i.select('full', 'athena')
        with self.assertRaises(ValueError): i.select(agents='../secret')
    def test_install_plan_no_side_effects(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'PANTHEON_HOME':tmp}):
            with patch.object(i, 'run_native') as native:
                result = self.runner.invoke(app, ['install','--agents','athena,themis'])
                self.assertEqual(result.exit_code, 0, result.output)
                self.assertIn('Plan only', result.output)
                self.assertEqual(list(Path(tmp).iterdir()), [])
                native.assert_not_called()
    def test_stage_is_immutable(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'PANTHEON_HOME':tmp}):
            dest = i.stage('athena')
            self.assertEqual(i.stage('athena'), dest)
            self.assertEqual(i.tree_bytes(dest), i.tree_bytes(i.RESOURCES/'profiles'/'athena'))
            (dest/'SOUL.md').write_text('local edit')
            with self.assertRaises(RuntimeError): i.stage('athena')
            self.assertEqual((dest/'SOUL.md').read_text(),'local edit')
    def test_native_install_no_force_or_auto_confirm(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'PANTHEON_HOME':tmp}), patch.object(i,'run_native') as native:
            result = self.runner.invoke(app,['install','--agents','athena','--apply','--alias'])
            self.assertEqual(result.exit_code,0,result.output)
            self.assertEqual(native.call_args.args[0], ['profile','install',str(i.source_path('athena')),'--alias'])
            self.assertEqual(native.call_count,3)
    def test_native_failure_propagates(self):
        with patch.object(i,'run_native',side_effect=subprocess.CalledProcessError(2,['hermes'])):
            result=self.runner.invoke(app,['install','--agents','athena','--apply'])
            self.assertEqual(result.exit_code,1,result.output)
    def test_doctor_missing_runtime(self):
        with patch.object(i,'executable',side_effect=RuntimeError('Hermes CLI not found')):
            result=self.runner.invoke(app,['doctor'])
            self.assertEqual(result.exit_code,1,result.output)
            self.assertIn('Hermes CLI not found',result.output)
    def test_init_dry_run(self):
        result=self.runner.invoke(app,['init','--preset','developer'])
        self.assertEqual(result.exit_code,0,result.output)
        self.assertIn('Plan only', result.output)
        self.assertIn('hephaestus', result.output)
    def test_configuration_requires_apply(self):
        with patch.object(i,'run_native') as native:
            result=self.runner.invoke(app,['configure','--agent','hermes'])
            self.assertEqual(result.exit_code,0,result.output)
            native.assert_not_called()
    def test_update_confirmation(self):
        with patch.object(i,'run_native') as native:
            result=self.runner.invoke(app,['update','--agent','hermes','--apply'], input='n\n')
            self.assertNotEqual(result.exit_code,0)
            native.assert_called_once_with(['profile','info','pantheon-hermes'])
    def test_backup_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(i,'run_native') as native:
            path=Path(tmp)/'snapshot.tar.gz'; path.write_text('existing')
            result=self.runner.invoke(app,['backup','--agent','athena','--output',str(path),'--apply'])
            self.assertEqual(result.exit_code,1,result.output)
            native.assert_not_called()
            self.assertEqual(path.read_text(),'existing')
    def test_invalid_selection(self):
        result=self.runner.invoke(app,['install','--agents','../../bad'])
        self.assertEqual(result.exit_code,1,result.output)
    def test_all_resources(self):
        self.assertEqual(len(i.registry('agents')['agents']),8)
        self.assertEqual(len(i.registry('groups')['groups']),7)
        self.assertTrue(all(not x['enabled'] for x in i.registry('routines')['routines']))
        for agent in i.PRESETS['full']:
            self.assertTrue((i.RESOURCES/'profiles'/agent/'distribution.yaml').is_file())

class BundledResourceTests(unittest.TestCase):
    def test_every_profile_bundles_self_improvement(self):
        for agent in i.PRESETS['full']:
            skill = i.RESOURCES/'profiles'/agent/'skills'/'self-improvement'
            self.assertTrue((skill/'SKILL.md').is_file(), agent)
            self.assertEqual(i.tree_bytes(skill), i.tree_bytes(i.RESOURCES/'skills'/'self-improvement'))
    def test_bundled_versions_match_package(self):
        from pantheon import __version__
        for agent in i.PRESETS['full']:
            manifest = (i.RESOURCES/'profiles'/agent/'distribution.yaml').read_text(encoding='utf-8')
            self.assertIn(f'version: {__version__}\n', manifest)

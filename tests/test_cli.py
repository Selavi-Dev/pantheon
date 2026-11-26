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
            (dest/'SOUL.md').write_text('local edit', encoding='utf-8')
            with self.assertRaises(RuntimeError): i.stage('athena')
            self.assertEqual((dest/'SOUL.md').read_text(encoding='utf-8'),'local edit')
    def test_native_install_no_force_or_auto_confirm(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'PANTHEON_HOME':tmp}), patch.object(i,'run_native') as native:
            result = self.runner.invoke(app,['install','--agents','athena','--apply','--alias'])
            self.assertEqual(result.exit_code,0,result.output)
            calls=[c.args[0] for c in native.call_args_list]
            self.assertIn(['profile','install',str(i.source_path('athena')),'--alias'], calls)
            self.assertEqual([c for c in calls if c[:2]==['profile','install'] and c[2:3]!=['--help']], [['profile','install',str(i.source_path('athena')),'--alias']])
            self.assertFalse(any('--force' in c or '--yes' in c or '-y' in c for c in calls))
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
            path=Path(tmp)/'snapshot.tar.gz'; path.write_text('existing', encoding='utf-8')
            result=self.runner.invoke(app,['backup','--agent','athena','--output',str(path),'--apply'])
            self.assertEqual(result.exit_code,1,result.output)
            native.assert_not_called()
            self.assertEqual(path.read_text(encoding='utf-8'),'existing')
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


PROFILE_LIST = """
 Profile          Model                        Gateway      Alias        Distribution
 \u2500\u2500\u2500\u2500\u2500\u2500\u2500    \u2500\u2500\u2500\u2500    \u2500\u2500\u2500\u2500
 \u25c6default         anthropic/claude-opus-4.6    running      \u2014            \u2014
  pantheon-athena \u2014                            stopped      \u2014            pantheon-athena@0.3.0
  pantheon-hermes \u2014                            running      \u2014            pantheon-hermes@0.3.0
"""

class GatewayWarningTests(unittest.TestCase):
    def setUp(self): self.runner = CliRunner()
    def fake(self, output):
        def run(args, capture=False):
            return subprocess.CompletedProcess(args, 0, stdout=output if args == ['profile','list'] else 'hermes 0.23.1', stderr='')
        return run
    def test_parses_running_profiles(self):
        with patch.object(i, 'run_native', side_effect=self.fake(PROFILE_LIST)):
            self.assertEqual(i.running_gateways(), ['default', 'pantheon-hermes'])
    def test_alias_named_running_is_not_a_running_gateway(self):
        out = "  pantheon-athena \u2014                            stopped      running      pantheon-athena@0.3.0\n"
        with patch.object(i, 'run_native', side_effect=self.fake(out)):
            self.assertEqual(i.running_gateways(), [])
    def test_display_name_rows_use_canonical_id(self):
        out = (" \u25c6Profile (default) anthropic/claude-opus-4.6    running      \u2014            \u2014\n"
               "  Chief Of Staff (pantheon-hermes) \u2014           running      \u2014            pantheon-hermes@0.3.0\n"
               "  pantheon-athena \u2014                            stopped      \u2014            pantheon-athena@0.3.0\n")
        with patch.object(i, 'run_native', side_effect=self.fake(out)):
            self.assertEqual(i.running_gateways(), ['default', 'pantheon-hermes'])
    def test_warning_targets_the_default_host(self):
        with patch.object(i, 'run_native', side_effect=self.fake(PROFILE_LIST)):
            result = self.runner.invoke(app, ['doctor'])
            self.assertIn('hermes -p default gateway stop', ' '.join(result.output.split()))
    def test_no_hermes_means_no_warning(self):
        with patch.object(i, 'run_native', side_effect=RuntimeError('Hermes CLI not found')):
            self.assertEqual(i.running_gateways(), [])
    def test_apply_warns_before_and_reports_served_after(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'PANTHEON_HOME': tmp}), \
             patch.object(i, 'run_native', side_effect=self.fake(PROFILE_LIST)):
            result = self.runner.invoke(app, ['install', '--agents', 'hermes,athena', '--apply'])
            self.assertEqual(result.exit_code, 0, result.output)
            out = ' '.join(result.output.split())
            self.assertIn('A Hermes gateway is already running (default, pantheon-hermes)', out)
            self.assertIn('Now served by a running gateway: pantheon-hermes', out)
    def test_quiet_when_nothing_runs(self):
        quiet = PROFILE_LIST.replace('running', 'stopped')
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'PANTHEON_HOME': tmp}), \
             patch.object(i, 'run_native', side_effect=self.fake(quiet)):
            result = self.runner.invoke(app, ['install', '--agents', 'athena', '--apply'])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertNotIn('gateway is already running', result.output)
    def test_doctor_warns(self):
        with patch.object(i, 'run_native', side_effect=self.fake(PROFILE_LIST)):
            result = self.runner.invoke(app, ['doctor'])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn('already running', ' '.join(result.output.split()))


class NativeErrorReportingTests(unittest.TestCase):
    def setUp(self): self.runner = CliRunner()
    def test_doctor_shows_hermes_error_output(self):
        err = subprocess.CalledProcessError(1, ['hermes', 'profile', 'install', '--help'],
                                            output='', stderr='Traceback ...\nModuleNotFoundError: No module named example')
        with patch.object(i, 'run_native', side_effect=err):
            result = self.runner.invoke(app, ['doctor'])
        out = ' '.join(result.output.split())
        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn('`hermes profile install --help` failed with exit code 1', out)
        self.assertIn('No module named example', out)
    def test_silent_failure_says_so(self):
        err = subprocess.CalledProcessError(1, ['hermes'], output='', stderr='')
        with patch.object(i, 'run_native', side_effect=err):
            result = self.runner.invoke(app, ['doctor'])
        self.assertIn('printed nothing', ' '.join(result.output.split()))
    def test_timeout_is_reported(self):
        with patch.object(i, 'run_native', side_effect=subprocess.TimeoutExpired(['hermes'], 30)):
            result = self.runner.invoke(app, ['doctor'])
        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn('did not finish within 30 seconds', ' '.join(result.output.split()))
    def test_timeout_shows_what_hermes_printed(self):
        # subprocess.run hands back a timeout's partial output as bytes, even with text=True.
        err = subprocess.TimeoutExpired(['hermes'], 30, output=b'loading profiles\n',
                                        stderr=b'stalled: waiting for profile store lock\n')
        with patch.object(i, 'run_native', side_effect=err):
            result = self.runner.invoke(app, ['doctor'])
        out = ' '.join(result.output.split())
        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn('did not finish within 30 seconds', out)
        self.assertIn('stalled: waiting for profile store lock', out)
        self.assertIn('loading profiles', out)
        self.assertNotIn("b'", out)
    def test_install_preflight_reports_hermes_output(self):
        err = subprocess.CalledProcessError(2, ['hermes'], output='usage: hermes ...', stderr='')
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'PANTHEON_HOME': tmp}), \
             patch.object(i, 'run_native', side_effect=err):
            result = self.runner.invoke(app, ['install', '--agents', 'athena', '--apply'])
        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn('usage: hermes', result.output)

    def test_stderr_survives_verbose_stdout(self):
        usage = '\n'.join(f'usage line {n}' for n in range(30))
        err = subprocess.CalledProcessError(1, ['hermes'], output=usage, stderr='real reason: profile store locked')
        with patch.object(i, 'run_native', side_effect=err):
            result = self.runner.invoke(app, ['doctor'])
        out = ' '.join(result.output.split())
        self.assertIn('real reason: profile store locked', out)
        self.assertIn('usage line 29', out)
        self.assertNotIn('usage line 0 ', out)

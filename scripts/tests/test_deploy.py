"""Deployment credentials must persist without appearing in commands or output."""
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('deployment', Path(__file__).resolve().parents[1] / 'deploy.py')
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)


class DeploymentTests(unittest.TestCase):
    def test_configure_preserves_key_and_token_on_reuse(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / 'config'
            # Windows ACLs do not implement POSIX modes; Linux CI checks them below.
            permissions = patch.object(Path, 'chmod') if os.name == 'nt' else contextlib.nullcontext()
            with permissions, contextlib.redirect_stdout(io.StringIO()) as output:
                with patch('builtins.input', side_effect=['', '']), patch.object(deploy.getpass, 'getpass', return_value='test-secret-not-real'):
                    deploy.configure(directory)
                original = (directory / 'server.env').read_bytes()
                with patch('builtins.input', side_effect=['', '']), patch.object(deploy.getpass, 'getpass', return_value=''):
                    deploy.configure(directory)
                self.assertEqual((directory / 'llm_api_key').read_text(), 'test-secret-not-real')
                self.assertEqual((directory / 'server.env').read_bytes(), original)
                self.assertNotIn('test-secret-not-real', output.getvalue())
                self.assertNotIn('test-secret-not-real', original.decode())
                if os.name == 'posix':
                    self.assertEqual(directory.stat().st_mode & 0o777, 0o700)
                    self.assertEqual((directory / 'server.env').stat().st_mode & 0o777, 0o600)
                with patch('builtins.input', side_effect=['', '']), patch.object(deploy.getpass, 'getpass', return_value='rotated-test-secret'):
                    deploy.configure(directory)
                self.assertEqual((directory / 'llm_api_key').read_text(), 'rotated-test-secret')

    def test_command_uses_fixed_project_external_config_and_no_inline_key(self):
        directory = Path('/server/private/config')
        command = deploy.deployment_command(directory)
        self.assertIn('shuprophet-studio', command)
        self.assertIn(str(directory / 'server.env'), command)
        self.assertIn(str(deploy.ROOT / 'compose.secrets.yaml'), command)
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'secret-from-shell', 'OPENAI_MODEL': 'stale-model', 'STUDIO_ACCESS_TOKEN': 'stale-token'}):
            environment = deploy.deployment_environment(directory)
        for key in ('OPENAI_API_KEY', 'OPENAI_MODEL', 'STUDIO_ACCESS_TOKEN'):
            self.assertNotIn(key, environment)
        self.assertEqual(environment['SHU_SECRET_DIR'], str(directory))
        self.assertNotIn('secret-from-shell', ' '.join(command))


if __name__ == '__main__':
    unittest.main()

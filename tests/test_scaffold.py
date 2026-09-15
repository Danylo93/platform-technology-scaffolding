import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/create-node-service.py'


class ScaffoldTest(unittest.TestCase):
    def run_generator(self, name, output, *extra):
        return subprocess.run(
            ['python3', str(SCRIPT), name, '--owner', 'Example-Team', '--output', str(output), *extra],
            text=True, capture_output=True,
            env={**os.environ, 'GIT_AUTHOR_NAME': 'Scaffold test',
                 'GIT_AUTHOR_EMAIL': 'test@example.invalid',
                 'GIT_COMMITTER_NAME': 'Scaffold test',
                 'GIT_COMMITTER_EMAIL': 'test@example.invalid'})

    def test_complete_service_and_branches(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'service'
            result = self.run_generator('orders-api', output, '--init-git')
            self.assertEqual(result.returncode, 0, result.stderr)
            for filename in ('Dockerfile', 'package-lock.json', 'src/server.js',
                             'test/server.test.js', '.github/workflows/ci.yml',
                             '.github/workflows/promote.yml', 'README.md'):
                self.assertTrue((output / filename).is_file(), filename)
            self.assertFalse((output / 'openshift').exists())
            for environment, replicas in (('ti', 1), ('hml', 2), ('prod', 3)):
                values = yaml.safe_load((output / f'gitops/environments/{environment}/values.yaml').read_text())
                self.assertEqual(values['replicaCount'], replicas)
                self.assertEqual(values['image']['repository'], 'platform-registry:5000/orders-api')
                self.assertIsInstance(values['image']['tag'], str)
                app = yaml.safe_load((output / f'gitops/argocd/app-{environment}.yaml').read_text())
                self.assertEqual(app['metadata']['name'], f'orders-api-{environment}')
                self.assertEqual(app['metadata']['namespace'], 'argocd')
                self.assertEqual(app['spec']['source']['repoURL'], 'git@github.com:Example-Team/orders-api.git')
            refs = subprocess.check_output(['git', 'branch', '--format=%(refname:short)'], cwd=output, text=True)
            self.assertEqual(set(refs.split()), {'main', 'deployment_files'})
            self.assertEqual(subprocess.check_output(['git', 'status', '--porcelain'], cwd=output), b'')

    def test_existing_directory_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            sentinel = output / 'keep.txt'
            sentinel.write_text('existing user data')
            self.assertNotEqual(self.run_generator('orders-api', output).returncode, 0)
            self.assertEqual(sentinel.read_text(), 'existing user data')
            self.assertEqual(list(output.iterdir()), [sentinel])

    def test_invalid_names_do_not_create_output(self):
        with tempfile.TemporaryDirectory() as directory:
            for name in ('../escape', 'UpperCase', 'bad_name', '-bad', 'a' * 49):
                output = Path(directory) / 'service'
                self.assertNotEqual(self.run_generator(name, output).returncode, 0)
                self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()

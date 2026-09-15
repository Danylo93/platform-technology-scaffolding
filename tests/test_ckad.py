import importlib.util
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('ckad_lab', Path(__file__).resolve().parents[1] / 'ckad/lab.py')
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class CkadSafetyTests(unittest.TestCase):
    def test_existing_unowned_namespace_is_not_modified(self):
        response = subprocess.CompletedProcess([], 0, stdout=json.dumps({'metadata': {'labels': {}}}))
        with patch.object(lab, 'kubectl', return_value=response) as command:
            with self.assertRaisesRegex(RuntimeError, 'nao pertence'):
                lab.start('01')
        self.assertEqual(command.call_count, 1)
        self.assertEqual(command.call_args.args[:2], ('get', 'namespace'))

    def test_old_ready_pod_does_not_hide_failed_rollout(self):
        deployment = {
            'metadata': {'generation': 3}, 'spec': {'replicas': 1},
            'status': {'replicas': 2, 'readyReplicas': 1, 'updatedReplicas': 1,
                       'observedGeneration': 3},
        }
        with patch.object(lab, 'guard'), patch.object(lab, 'get', return_value=deployment):
            with self.assertRaisesRegex(RuntimeError, 'replica atualizada'):
                lab.check()


if __name__ == '__main__':
    unittest.main()

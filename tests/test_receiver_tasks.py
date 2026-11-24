import json
import sys
import subprocess
import tempfile
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from receiver_tasks import validate_request, request_token
from commit_message_policy import keys_for_paths, require_valid_commit_message
from analysis_task_fixture import task_binding


class ReceiverTaskTests(unittest.TestCase):
    def request(self):
        return dict(schema_version=1, request_id=str(uuid.uuid4()), provider='sbertrek',
                    role='AN', target='receiver', delivery='demo', summary='Demo',
                    confirmation='Создать задачу на принимающей стороне')

    def test_request_validation(self):
        request = self.request()
        self.assertEqual(validate_request(request, 'demo'), request)
        for change in [dict(delivery='other'), dict(key='RSCON-1'), dict(request_id='../../bad'),
                       dict(role='BE'), dict(confirmation='')]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_request({**request, **change}, 'demo')

    def test_transport_request_preserves_delta_scope_and_cannot_publish(self):
        request = self.request()
        root = 'quarters/2026-Q4/features/demo/deliveries/demo'
        old = {'delivery-index.json': json.dumps({'schema_version': 1, 'deliveries': {
            'legacy': {'path': 'features/legacy'}}})}
        registry = json.loads(old['delivery-index.json'])
        registry['deliveries']['demo'] = {'path': root, 'quarter': '2026-Q4'}
        files = {'delivery-index.json': json.dumps(registry),
                 root + '/analysis-task-request.json': json.dumps(request)}
        paths = ['delivery-index.json', root + '/requirements.md', root + '/analysis-task-request.json']
        with self.assertRaises(ValueError):
            keys_for_paths(paths, files.get, old.get)
        keys = keys_for_paths(paths, files.get, old.get, allow_receiver_requests=True)
        self.assertEqual(keys, {request_token(request)})
        require_valid_commit_message(request_token(request) + ': Передать требования', keys)
        for title in ['Передать требования', request_token(request)]:
            with self.assertRaises(ValueError):
                require_valid_commit_message(title, keys)
        with self.assertRaises(ValueError):
            keys_for_paths(paths + ['requirements-exchange/demo/manifest.json'], files.get,
                           old.get, allow_receiver_requests=True)
        with self.assertRaises(ValueError):
            keys_for_paths(paths + ['quarters/2026-Q4/gantt/actual-progress.puml'], files.get,
                           old.get, allow_receiver_requests=True)
        files[root + '/analysis-task.json'] = json.dumps(task_binding())
        self.assertEqual(keys_for_paths(paths, files.get, old.get, allow_receiver_requests=True), {'RSCON-123'})

    def test_source_commit_hook_checks_transport_token(self):
        from workspace import install_commit_message_hook
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            def git(*args):
                return subprocess.run(['git', '-C', str(project), *args],
                                      capture_output=True, text=True)
            self.assertEqual(git('init', '-b', 'main').returncode, 0)
            git('config', 'user.name', 'Test')
            git('config', 'user.email', 'test@example.invalid')
            git('commit', '--allow-empty', '-m', 'Initial fixture')
            request = self.request()
            root = 'features/demo'
            (project / root).mkdir(parents=True)
            (project / root / 'analysis-task-request.json').write_text(json.dumps(request))
            (project / root / 'requirements.md').write_text('Requirements')
            (project / 'delivery-index.json').write_text(json.dumps({
                'schema_version': 1, 'deliveries': {
                    'legacy': {'path': 'features/legacy'}, 'demo': {'path': root}}}))
            # The unrelated legacy delivery must not enter the new delta.
            git('add', '--', 'delivery-index.json')
            git('commit', '-m', 'Registry fixture')
            git('add', '--', root + '/analysis-task-request.json', root + '/requirements.md')
            install_commit_message_hook(project, Path(__file__).resolve().parents[1] / "scripts/commit_message_policy.py")
            self.assertNotEqual(git('commit', '-m', 'Missing request token').returncode, 0)
            result = git('commit', '-m', request_token(request) + ': Передать требования')
            self.assertEqual(result.returncode, 0, result.stderr)

#!/usr/bin/env python3
"""Verify the running sample lab without changing desired state."""
import argparse
import json
import socket
import subprocess
import time
import urllib.error
import urllib.request


def kubectl(*args):
    return json.loads(subprocess.check_output(
        ['kubectl', '--context=kind-platform-lab', *args, '-o', 'json'], text=True))


def verify_http(environment):
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        port = listener.getsockname()[1]
    process = subprocess.Popen([
        'kubectl', '--context=kind-platform-lab', '-n', f'platform-{environment}',
        'port-forward', '--address=127.0.0.1', 'svc/platform-sample-application', f'{port}:8080',
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for attempt in range(50):
            if process.poll() is not None:
                raise RuntimeError(f'port-forward exited for {environment}')
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{port}/health', timeout=2) as response:
                    health = json.load(response)
                break
            except (urllib.error.URLError, TimeoutError):
                time.sleep(0.2)
        else:
            raise RuntimeError(f'port-forward readiness timeout for {environment}')
        assert health == {'status': 'UP', 'environment': environment}, health
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/', timeout=5) as response:
            root = json.load(response)
        assert root['app'] == 'platform-sample-application', root
        assert root['environment'] == environment, root
        return {'root': root, 'health': health}
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image-tag', required=True)
    parser.add_argument('--revision', required=True, help='Expected GitOps commit')
    args = parser.parse_args()
    image = f'platform-registry:5000/platform-sample-application:{args.image_tag}'
    image_ids = set()
    result = {}
    for environment, replicas in (('ti', 1), ('hml', 2), ('prod', 3)):
        app = kubectl('-n', 'argocd', 'get', 'application', f'platform-sample-{environment}')
        assert app['status']['sync']['status'] == 'Synced', app['status']['sync']
        assert app['status']['health']['status'] == 'Healthy', app['status']['health']
        assert app['status']['sync']['revision'] == args.revision, app['status']['sync']
        deployment = kubectl('-n', f'platform-{environment}', 'get', 'deployment', 'platform-sample-application')
        assert deployment['spec']['replicas'] == replicas
        assert deployment['status']['readyReplicas'] == replicas
        assert deployment['spec']['template']['spec']['containers'][0]['image'] == image
        pods = kubectl('-n', f'platform-{environment}', 'get', 'pods', '-l', 'app=platform-sample-application')
        active = [pod for pod in pods['items'] if not pod['metadata'].get('deletionTimestamp')]
        assert len(active) == replicas, len(active)
        for pod in active:
            status = pod['status']['containerStatuses'][0]
            assert status['ready'], pod['metadata']['name']
            image_ids.add(status['imageID'])
        result[environment] = {'replicas': replicas, 'image': image, **verify_http(environment)}
    assert len(image_ids) == 1, image_ids
    result['shared_image_id'] = image_ids.pop()
    result['gitops_revision'] = args.revision
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

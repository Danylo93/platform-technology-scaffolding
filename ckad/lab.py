#!/usr/bin/env python3
"""Prepare and verify isolated CKAD practice incidents in the existing Kind lab."""
import argparse
import json
import subprocess
import sys

CONTEXT = 'kind-platform-lab'
NAMESPACE = 'ckad-practice'
OWNER = 'platform-lab-ckad'
LABELS = {'lab': OWNER}
IMAGE = 'platform-registry:5000/platform-sample-application:67e504b8a1bc95e2e67e7d4d35622aad178eb6f9'
CASES = {
    '01': 'A API esta pronta, mas o consumidor nao consegue acessa-la.',
    '02': 'O processo iniciou, mas a aplicacao nao recebe trafego.',
    '03': 'A nova configuracao impede o container de iniciar.',
    '04': 'O rollout ficou bloqueado ao obter o artefato.',
    '05': 'O container inicia e encerra repetidamente.',
    '06': 'A politica de execucao impede a inicializacao.',
}


def kubectl(*args, payload=None, capture=True):
    return subprocess.run(
        ['kubectl', '--context', CONTEXT, '--namespace', NAMESPACE, *args],
        input=json.dumps(payload) if payload is not None else None,
        text=True, capture_output=capture, check=True, timeout=100)


def get(kind, name):
    return json.loads(kubectl('get', kind, name, '-o', 'json').stdout)


def guard():
    result = kubectl('get', 'namespace', NAMESPACE, '--ignore-not-found', '-o', 'json')
    if result.stdout.strip():
        existing = json.loads(result.stdout)
        if existing['metadata'].get('labels', {}).get('lab') != OWNER:
            raise RuntimeError('Namespace existente nao pertence a estes exercicios; nenhuma alteracao realizada.')


def resource(kind, name, **extra):
    return {'apiVersion': 'v1', 'kind': kind,
            'metadata': {'name': name, 'namespace': NAMESPACE, 'labels': LABELS.copy()}, **extra}


def manifests(case):
    settings = resource('ConfigMap', 'api-settings', data={'APP_ENV': 'ckad'})
    container = {
        'name': 'api', 'image': IMAGE, 'imagePullPolicy': 'Always',
        'ports': [{'name': 'http', 'containerPort': 8080}],
        'env': [{'name': 'APP_ENV', 'valueFrom': {'configMapKeyRef': {'name': 'api-settings', 'key': 'APP_ENV'}}}],
        'resources': {'requests': {'cpu': '25m', 'memory': '32Mi'},
                      'limits': {'cpu': '250m', 'memory': '96Mi'}},
        'securityContext': {'runAsNonRoot': True, 'runAsUser': 1000,
                            'readOnlyRootFilesystem': True, 'allowPrivilegeEscalation': False,
                            'capabilities': {'drop': ['ALL']}},
        'readinessProbe': {'httpGet': {'path': '/health', 'port': 8080}, 'periodSeconds': 2},
        'livenessProbe': {'httpGet': {'path': '/health', 'port': 8080}, 'initialDelaySeconds': 5},
    }
    deployment = resource('Deployment', 'ckad-api', spec={
        'replicas': 1, 'selector': {'matchLabels': {'app': 'ckad-api'}},
        'template': {'metadata': {'labels': {**LABELS, 'app': 'ckad-api'},
                                  'annotations': {'practice-case': case}},
                     'spec': {'automountServiceAccountToken': False, 'terminationGracePeriodSeconds': 2,
                              'securityContext': {'seccompProfile': {'type': 'RuntimeDefault'}},
                              'containers': [container]}}})
    deployment['apiVersion'] = 'apps/v1'
    service = resource('Service', 'ckad-api', spec={
        'type': 'ClusterIP', 'selector': {'app': 'ckad-api'},
        'ports': [{'name': 'http', 'port': 8080, 'targetPort': 8080}]})
    client = resource('Pod', 'ckad-client', spec={
        'automountServiceAccountToken': False, 'terminationGracePeriodSeconds': 2,
        'containers': [{'name': 'client', 'image': IMAGE,
                        'command': ['node', '-e', 'setInterval(() => {}, 60000)'],
                        'resources': {'requests': {'cpu': '10m', 'memory': '24Mi'},
                                      'limits': {'cpu': '100m', 'memory': '96Mi'}},
                        'securityContext': {'runAsNonRoot': True, 'runAsUser': 1000,
                                            'allowPrivilegeEscalation': False,
                                            'capabilities': {'drop': ['ALL']}}}]})
    # Fault definitions are trainer material; student briefs are in EXERCICIOS.md.
    if case == '01':
        service['spec']['selector'] = {'app': 'ckad-api-v2'}
    elif case == '02':
        container['readinessProbe']['httpGet']['port'] = 8081
    elif case == '03':
        container['env'][0]['valueFrom']['configMapKeyRef']['key'] = 'ENVIRONMENT'
    elif case == '04':
        container['image'] = IMAGE.rsplit(':', 1)[0] + ':ckad-missing-artifact'
    elif case == '05':
        container['command'] = ['node', 'src/missing-server.js']
    elif case == '06':
        container['securityContext']['runAsUser'] = 0
    return [settings, deployment, service, client]


def start(case):
    guard()
    namespace = {'apiVersion': 'v1', 'kind': 'Namespace',
                 'metadata': {'name': NAMESPACE, 'labels': LABELS.copy()}}
    kubectl('apply', '-f', '-', payload=namespace)
    quota = resource('ResourceQuota', 'practice-budget', spec={'hard': {
        'pods': '6', 'requests.cpu': '500m', 'requests.memory': '256Mi',
        'limits.cpu': '2', 'limits.memory': '512Mi'}})
    kubectl('apply', '-f', '-', payload=quota)
    kubectl('apply', '-f', '-', payload={'apiVersion': 'v1', 'kind': 'List', 'items': manifests(case)})
    kubectl('wait', '--for=condition=Ready', 'pod/ckad-client', '--timeout=90s')
    if case in ('baseline', '01'):
        kubectl('rollout', 'status', 'deployment/ckad-api', '--timeout=90s')
    print(f'Contexto: {CONTEXT}; namespace: {NAMESPACE}')
    print('Baseline saudavel aplicada.' if case == 'baseline' else f'Incidente {case}: {CASES[case]}')
    print('Use status para observar. Use check depois de corrigir.')


def check():
    guard()
    deployment = get('deployment', 'ckad-api')
    spec, status = deployment['spec'], deployment.get('status', {})
    if (spec['replicas'] != 1 or status.get('readyReplicas') != 1
            or status.get('updatedReplicas') != 1
            or status.get('replicas') != 1
            or status.get('observedGeneration', 0) < deployment['metadata']['generation']):
        raise RuntimeError('Deployment precisa ter uma replica atualizada e Ready.')
    pods = json.loads(kubectl('get', 'pods', '-l', 'app=ckad-api', '-o', 'json').stdout)['items']
    active = [pod for pod in pods if not pod['metadata'].get('deletionTimestamp')]
    if len(active) != 1 or not all(item.get('ready') for item in active[0].get('status', {}).get('containerStatuses', [])):
        raise RuntimeError('Aguarde o Pod atual ficar Ready e a versao anterior sair do rollout.')
    if not active[0].get('status', {}).get('containerStatuses'):
        raise RuntimeError('O container atual ainda nao iniciou.')
    container = spec['template']['spec']['containers'][0]
    if container['image'] != IMAGE:
        raise RuntimeError('Mantenha a imagem versionada original; nao substitua por nginx ou latest.')
    if not container.get('readinessProbe') or not container.get('livenessProbe'):
        raise RuntimeError('As probes precisam continuar habilitadas.')
    for name in ('readinessProbe', 'livenessProbe'):
        probe = container[name].get('httpGet', {})
        if probe.get('path') != '/health' or probe.get('port') not in (8080, 'http'):
            raise RuntimeError('As probes devem verificar /health na porta HTTP da aplicacao.')
    env = next((item for item in container.get('env', []) if item['name'] == 'APP_ENV'), {})
    if env.get('valueFrom', {}).get('configMapKeyRef', {}).get('name') != 'api-settings':
        raise RuntimeError('APP_ENV deve continuar vindo do ConfigMap api-settings.')
    security = container.get('securityContext', {})
    if not security.get('runAsNonRoot') or security.get('runAsUser') == 0:
        raise RuntimeError('A aplicacao deve continuar executando sem root.')
    if security.get('allowPrivilegeEscalation') is not False or security.get('privileged'):
        raise RuntimeError('Preserve as restricoes de privilegios do container.')
    capabilities = security.get('capabilities', {})
    if capabilities.get('add') or 'ALL' not in capabilities.get('drop', []):
        raise RuntimeError('Preserve o descarte de capabilities e nao adicione privilegios.')
    if get('service', 'ckad-api')['spec']['type'] != 'ClusterIP':
        raise RuntimeError('O Service deve continuar sendo ClusterIP.')
    script = """Promise.all(['/','/health'].map(async path => {
      const response = await fetch('http://ckad-api:8080' + path, {signal: AbortSignal.timeout(15000)});
      if (!response.ok) throw Error('HTTP ' + response.status);
      const data = await response.json();
      if (data.environment !== 'ckad') throw Error('Ambiente incorreto');
      if (path === '/health' && data.status !== 'UP') throw Error('Health incorreto');
      if (path === '/' && data.app !== 'platform-sample-application') throw Error('Aplicacao incorreta');
    })).then(() => console.log('HTTP / e /health OK via Service DNS')).catch(() => {
      console.error('Falha no acesso HTTP pelo Service ou no contrato da resposta'); process.exit(1);
    });"""
    result = kubectl('exec', 'ckad-client', '--', 'node', '-e', script)
    print(result.stdout.strip())
    print('PASSOU: Deployment, Service, seguranca e resposta da API validados.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['start', 'reset', 'status', 'check'])
    parser.add_argument('case', nargs='?', choices=list(CASES))
    args = parser.parse_args()
    try:
        if args.action == 'start':
            if not args.case:
                parser.error('start exige um numero entre 01 e 06')
            start(args.case)
        elif args.action == 'reset':
            start('baseline')
        elif args.action == 'status':
            kubectl('get', 'deployment,pods,service', capture=False)
        else:
            check()
    except subprocess.CalledProcessError as error:
        print((error.stderr or error.stdout or str(error)).strip(), file=sys.stderr)
        sys.exit(1)
    except (RuntimeError, subprocess.TimeoutExpired) as error:
        print(f'AINDA NAO PASSOU: {error}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

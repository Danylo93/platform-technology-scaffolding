# Platform Technology Scaffolding

A lightweight Node 22 Golden Path for Docker, Kind, Distribution registry:3,
GitHub Actions and Argo CD. No Backstage, CRC, Harbor or GitLab server is needed.

## Generate a service

```bash
python3 scripts/create-node-service.py orders-api --owner Danylo93 --output ../orders-api --init-git
```

The output directory must not exist. Names are validated before writing files.
`--init-git` creates an initial commit, main and deployment_files branches and an
SSH origin; it does not create or push a GitHub repository. Without this option,
the command only renders files. Git author configuration is needed for commits.

## Included contract

- Node source, package/lockfile, HTTP tests, Dockerfile and health endpoint.
- Helm Deployment/Service, non-root runtime, resource limits and health probes.
- Separate TI/HML/PROD values (1/2/3 replicas) and Argo Applications.
- Main CI consuming pinned reusable workflows from platform-pipeline-templates.
- Manual HML/PROD promotion using the same immutable Git SHA image tag.
- README with runner, registry, GitOps bootstrap and access commands.

```text
Developer -> generator -> application repository (main)
  -> shared CI -> localhost:5000 -> deployment_files
  -> Argo CD -> Kind (TI -> HML -> PROD)
```

The Docker publishing address is localhost:5000. Pods pull through
platform-registry:5000 on the Kind network. New GitOps values use an explicit
all-zero bootstrap tag until the first build/promotion replaces it.
Each service uses its own Application/Deployment/Service names, while namespaces
platform-ti, platform-hml and platform-prod are shared.

Configure a repository runner with the platform-lab label. The runner needs
Docker, Git, curl, Python 3/PyYAML, Helm and kubectl with kind-platform-lab access.
setup-node provides Node 22. For private repositories, configure Argo repository
access outside Git. Existing SSH keys and credentials are never generated or copied.

## Local Argo CD URL

The optional user service exposes Argo only on 127.0.0.1:8443 and reconnects
automatically when its pod or the cluster restarts. To install it:

```bash
mkdir -p ~/.config/systemd/user
cp scripts/platform-argocd-local.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now platform-argocd-local.service
sudo python3 scripts/configure-argocd-host.py
```

Open https://argocd.platform.test:8443. The hosts helper preserves existing
entries and backs up /etc/hosts before adding the name. Argo keeps its existing
login and self-signed TLS certificate, so the browser may show a certificate
warning. lab-control.sh also starts/stops this service when installed.

## Verification

After registering the existing runner in ~/actions-runner, its user service can
be installed without changing system services:

```bash
mkdir -p ~/.config/systemd/user
cp scripts/platform-lab-runner.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now platform-lab-runner.service
loginctl enable-linger "$USER"
```

The service enables run.sh's signal trap so stopping systemd also stops the
runner listener cleanly. lab-control.sh refuses to stop while a job is active.

```bash
python3 -m unittest discover -s tests -v
```

After deployment, verify all environments and temporary port-forwards without
changing desired state (use the actual image tag and deployment_files commit):

```bash
python3 scripts/verify-lab.py --image-tag IMAGE_SHA --revision GITOPS_SHA
```

The verification checks Argo revision/health, replica counts, the same image
digest across environments, and both HTTP endpoints. It closes all port-forwards.

The lab also verifies a rendered service with npm ci/test/audit, Docker build,
HTTP requests, Helm lint/template and Kubernetes server dry-run in all environments.
The existing skeleton/openshift files remain reference material and are excluded
from generated services. GitLab templates remain in the pipeline repository as
corporate reference; GitHub Actions is the lab execution path.

# Platform Technology Scaffolding

Laboratório local e gratuito de Platform Engineering.

Este repositório representa a camada de **scaffolding/Golden Path**. Ele define como uma nova aplicação deve nascer antes de consumir os templates de pipeline e ser reconciliada pelo Argo CD no OpenShift Local.

## Fluxo do lab

`Scaffolding -> App (master) -> Pipeline Template -> Harbor -> GitOps (deployment_files) -> Argo CD -> OpenShift Local`

## Stack alvo

- Git: GitHub agora; depois pode ser espelhado em GitLab CE/Gitea local
- CI: GitLab CI Runner
- Build: Podman/Buildah
- Registry: Harbor (`harbor.local/platform-lab`)
- CD: Argo CD / OpenShift GitOps
- Runtime: OpenShift Local / CRC
- Ambientes: namespaces `platform-ti`, `platform-hml`, `platform-prod`
- Packaging: Helm

## Estrutura

- `templates/node-api/`: Golden Path inicial para API Node.js
- `templates/node-api/skeleton/`: arquivos que formam uma nova aplicação
- `templates/node-api/template.yaml`: contrato da tecnologia, branches, registry e ambientes

> Lab educacional, sem URLs, segredos ou configurações internas de empresa.

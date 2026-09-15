# CKAD: pratica no seu Platform Lab

O primeiro incidente fica em ckad-practice. TI/HML/PROD e Argo continuam intactos.
Usamos a imagem Node real do projeto, o registry existente e o contexto
kind-platform-lab. Nenhum novo cluster ou ferramenta pesada e necessario.

## Comece aqui

```bash
cd ~/platform-lab/platform-technology-scaffolding/ckad
python3 lab.py status
```

Leia EXERCICIOS.md e investigue o incidente 01. Nao abra lab.py ou DICAS.md
antes da primeira tentativa: eles contem detalhes que revelam as falhas.

```bash
python3 lab.py check
```

O verificador acessa a API pelo DNS do Service de dentro de outro Pod, verifica
as respostas, a imagem original, as probes e a execucao sem root. Nao basta
fazer port-forward diretamente para o Deployment.

## Modo de estudo

1. Leia o objetivo e coloque um cronometro.
2. Observe recursos, eventos e logs antes de editar.
3. Escreva uma hipotese com a evidencia que a sustenta.
4. Faca a menor correcao que resolva a causa.
5. Rode o verificador e explique por que a correcao funcionou.

Traga a saida dos comandos e sua hipotese para nossa conversa. Primeiro
discutimos o raciocinio; depois a solucao. Dicas graduais ficam em DICAS.md.

## Gerenciar os cenarios

```bash
python3 lab.py start 01   # escolha 01 ate 06; substitui o cenario atual
python3 lab.py status
python3 lab.py check
python3 lab.py reset      # restaura os recursos-base saudaveis
```

start/reset restauram a quota e sobrescrevem o estado dos quatro recursos de treino nomeados
ckad-api (Deployment/Service), api-settings e ckad-client. Nao execute durante
uma tentativa que queira preservar. Outros recursos criados nos desafios
manuais nao sao apagados. O script fixa contexto/namespace e recusa namespaces
existentes sem o marcador de propriedade. Ele nao altera o contexto padrao.

O namespace tem quota: ate 6 pods, requests totais de 500m CPU/256Mi e limits
totais de 2 CPUs/512Mi. O baseline usa dois pods pequenos. Apenas um incidente
fica ativo por vez. Estes recursos nao sao gerenciados pelo Argo, para suas
correcoes com kubectl persistirem durante o treino.

## Relacao com a CKAD

| Dominio oficial | Peso | Pratica aqui |
| --- | --- | --- |
| Application Design and Build | 20% | Imagem Node, initContainer, volumes e Job |
| Application Deployment | 20% | Rollout, imagem invalida e rollback |
| Application Observability and Maintenance | 15% | Probes, logs, eventos e diagnostico |
| Application Environment, Configuration and Security | 25% | ConfigMap, Secret, recursos, identidade e RBAC |
| Services and Networking | 20% | Service, DNS, EndpointSlices e politica de rede |

Fonte: https://www.cncf.io/training/certification/ckad/ (consultada em 2026-09-15).
O cluster local e Kubernetes 1.37. Confira a versao vigente do exame antes de
agenda-lo; este material e pratica autoral, nao uma reproducao de questoes da prova.

Argo, GitHub Actions e scaffolding contextualizam o trabalho, mas aqui o foco
e desenvolver/configurar/operar aplicacoes Kubernetes. Administracao de etcd,
instalacao de control plane e upgrade de cluster ficam fora desta trilha.

## Material anterior

Encontramos ~/k8s-labs, mas labs/, manifests/ e helm/ estavam vazios. Os temas
foram reaproveitados dos LABS.md presentes no workspace: deploy, readiness,
pull de imagens, rollout, limites e troubleshooting. Nenhum script antigo de
criacao de cluster foi executado. O material anterior permanece onde estava.

## Limites de cobertura

Os incidentes 01-06 sao executaveis com verificador automatico. Os desafios
07-12 sao tarefas de construcao com criterios de aceite para revisarmos juntos.
NetworkPolicy exige um CNI que aplique as regras; o kindnet deste lab nao serve
como prova de isolamento. Nao instalamos outro CNI no cluster funcionando.
Ingress requer um controller; escrever o YAML sozinho nao comprova roteamento.

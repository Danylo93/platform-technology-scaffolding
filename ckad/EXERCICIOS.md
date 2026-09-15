# Desafios CKAD

Contexto: kind-platform-lab. Namespace: ckad-practice.
Os incidentes 01-06 usam ckad-api (Deployment/Service), api-settings e ckad-client.
Mantenha uma replica, a imagem Node versionada, probes e execucao sem root.
Nao mude recursos de platform-ti, platform-hml, platform-prod ou argocd.

## 01. Chamado: API indisponivel (10 minutos)

**Por que praticar:** Um deploy aplicado pelo Argo e um Pod Ready nao garantem acesso pelo Service. Este desafio treina localizar a interrupcao entre consumidor, Service e Pod.

**Por onde comecar:** Observe o estado dos Pods, depois os destinos do Service. Registre em qual etapa o caminho deixa de ter evidencia de funcionamento.

[Dicas graduais deste desafio](DICAS.md#01). Tente primeiro; abra uma dica por vez.

Ja esta preparado. Os pods aparentam estar saudaveis, mas o consumidor nao
consegue usar http://ckad-api:8080/health. Descubra a causa e recupere o acesso.
Nao mude o codigo, a imagem, os labels do Pod ou o tipo ClusterIP do Service.

Investigue primeiro:

```bash
kubectl --context kind-platform-lab -n ckad-practice get deploy,pods,svc
kubectl --context kind-platform-lab -n ckad-practice get endpointslices
```

Aceite: lab.py check passa e voce explica a relacao entre Service e seus destinos.
Registre a evidencia encontrada antes de modificar qualquer campo.

## 02. Chamado: processo vivo, rollout incompleto (12 minutos)

**Por que praticar:** Readiness controla a entrada de trafego; liveness pode reiniciar um container. Confundir as duas pode deixar uma entrega indisponivel mesmo com o processo vivo.

**Por onde comecar:** Use get pods e describe pod no Pod novo. Leia Conditions e Events antes de comparar as probes com a aplicacao.

[Dicas graduais deste desafio](DICAS.md#02). Tente primeiro; abra uma dica por vez.

Prepare com python3 lab.py start 02. A API inicia, mas nao entra em servico.
Nao remova probes e nao altere a porta real da aplicacao. Explique por que
Running e Ready podem divergir. Aceite: uma replica pronta e check passando.

## 03. Chamado: configuracao nova bloqueou a API (12 minutos)

**Por que praticar:** A imagem pode estar correta, mas uma dependencia de configuracao impedir a criacao do container. Nessa fase, logs da aplicacao podem nem existir.

**Por onde comecar:** Leia Events no describe do Pod novo. Identifique o objeto e a chave citados e consulte o ConfigMap, sem substituir a referencia por um valor fixo.

[Dicas graduais deste desafio](DICAS.md#03). Tente primeiro; abra uma dica por vez.

Prepare com python3 lab.py start 03. Nao ha resposta HTTP nem logs uteis do
processo novo. Corrija a referencia de configuracao mantendo APP_ENV vindo de
api-settings e o valor final ckad. Aceite: rollout completo e check passando.

## 04. Chamado: entrega travada (10 minutos)

**Por que praticar:** A pipeline publicar uma imagem e o cluster conseguir baixa-la sao etapas diferentes. Identificar a fase da falha evita depurar codigo que nem executou.

**Por onde comecar:** Observe a imagem declarada no Pod e a mensagem completa dos eventos de pull. Diferencie artefato inexistente de problemas de acesso ao registry.

[Dicas graduais deste desafio](DICAS.md#04). Tente primeiro; abra uma dica por vez.

Prepare com python3 lab.py start 04. O novo Pod nao consegue obter seu artefato.
Encontre uma tag existente no registry e restaure a imagem Node original:
67e504b8a1bc95e2e67e7d4d35622aad178eb6f9. Nao use latest, nginx ou rebuild.
Aceite: check passa; explique a diferenca entre falha de pull e falha do processo.

## 05. Chamado: processo reinicia (12 minutos)

**Por que praticar:** CrashLoopBackOff descreve o intervalo entre novas tentativas, nao a causa original. O motivo esta no processo que terminou.

**Por onde comecar:** Consulte logs --previous do Pod afetado e Last State no describe. Compare comando, argumentos e codigo de saida antes de alterar o Deployment.

[Dicas graduais deste desafio](DICAS.md#05). Tente primeiro; abra uma dica por vez.

Prepare com python3 lab.py start 05. Use logs atuais/anteriores e o estado da
ultima terminacao. Preserve imagem e configuracao. Aceite: check passa e o
contador de reinicios do novo Pod permanece estavel por pelo menos 30 segundos.

## 06. Chamado: restricao de execucao (12 minutos)

**Por que praticar:** Configuracoes de seguranca precisam ser compativeis com o usuario do processo. Desativar a protecao pode esconder o erro sem atender ao requisito.

**Por onde comecar:** Leia os eventos do Pod e os securityContext do Pod e do container. Descubra qual restricao impede a inicializacao.

[Dicas graduais deste desafio](DICAS.md#06). Tente primeiro; abra uma dica por vez.

Prepare com python3 lab.py start 06. A imagem esta disponivel, mas nao inicia.
Mantenha runAsNonRoot=true, allowPrivilegeEscalation=false e nenhuma capability
adicional. Aceite: processo sem root, rollout saudavel e check passando.

## Desafios de construcao: 07-12

Comece cada um com python3 lab.py reset. Estes desafios sao revisados pelos
criterios abaixo; o check generico nao valida todos os novos objetos.
Salve seus YAMLs em uma pasta de respostas fora dos arquivos do instrutor.

### 07. Configuracao e identidade (20 minutos)

**Por que praticar:** Configuracao, dados sensiveis e identidade possuem responsabilidades distintas. RBAC limita o que a identidade da aplicacao pode fazer na API.

**Por onde comecar:** Desenhe os objetos e suas referencias antes do YAML. Confira campos com kubectl explain e teste permissoes assumindo a ServiceAccount correta.

[Dicas graduais deste desafio](DICAS.md#07). Tente primeiro; abra uma dica por vez.
Crie ConfigMap app-options e Secret demo-credentials com apenas dados ficticios.
Configure um Pod consumer-demo com envFrom do ConfigMap e uma chave do Secret
via valueFrom. Crie ServiceAccount reader-demo, Role que permita get/list de
ConfigMaps somente neste namespace e RoleBinding correspondente.
Aceite: Pod pronto; auth can-i como reader-demo permite listar ConfigMaps e
nega listar Secrets. Nao conceda cluster-admin. Considere a quota ao definir recursos.

### 08. Recursos e disponibilidade (15 minutos)

**Por que praticar:** Requests influenciam agendamento, limits restringem consumo e quota limita o namespace. Um rollout precisa de capacidade para Pods extras.

**Por onde comecar:** Consulte a quota e some os recursos de todos os Pods, incluindo o cliente e o Pod adicional permitido por maxSurge.

[Dicas graduais deste desafio](DICAS.md#08). Tente primeiro; abra uma dica por vez.
No Deployment de treino, defina requests=50m/48Mi e limits=250m/96Mi. Escale para
duas replicas, respeitando a quota. Configure RollingUpdate com maxUnavailable=0
e maxSurge=1. Aceite: duas replicas prontas e um rollout sem perder todos os backends.
Depois restaure o baseline de uma replica. Explique request, limit e quota.

### 09. InitContainer e volume compartilhado (20 minutos)

**Por que praticar:** Inicializacao sequencial permite preparar dados antes do processo principal. emptyDir compartilha arquivos entre containers do mesmo Pod, nao entre Pods diferentes.

**Por onde comecar:** Planeje um volume e seus mounts nos dois containers. Confira como o init termina e como o principal comprova que leu o arquivo.

[Dicas graduais deste desafio](DICAS.md#09). Tente primeiro; abra uma dica por vez.
Crie um Pod volume-demo. Um initContainer deve escrever um arquivo ready.txt em
um emptyDir; o container principal deve le-lo e continuar executando. Use a
imagem Node existente, sem baixar ferramentas. Aceite: init termina com sucesso,
arquivo pode ser lido no container principal e ambos usam o mesmo volume.
Explique o que acontece com esse arquivo se o Pod for substituido.

### 10. Job e CronJob (20 minutos)

**Por que praticar:** Tarefas finitas precisam expressar sucesso ou falha por codigo de saida. Agendamento, concorrencia e limpeza sao responsabilidades adicionais.

**Por onde comecar:** Primeiro valide um Job isolado. Depois coloque o template no CronJob e teste uma execucao manual mantendo a agenda suspensa.

[Dicas graduais deste desafio](DICAS.md#10). Tente primeiro; abra uma dica por vez.
Crie um Job que execute uma chamada HTTP a /health e termine com erro se falhar.
Crie um CronJob com agenda */5 * * * *, concurrencyPolicy=Forbid e suspend=true.
Dispare um Job manual a partir do CronJob. Defina recursos, backoffLimit e
ttlSecondsAfterFinished para limitar residuos. Aceite: Jobs Complete com sucesso;
o CronJob nao cria execucoes automaticas enquanto suspenso.

### 11. Rollout e rollback (20 minutos)

**Por que praticar:** O Deployment recria Pods a partir do template desejado. Apagar um Pod nao desfaz uma alteracao errada nesse template.

**Por onde comecar:** Registre rollout history e a imagem saudavel antes da falha. Observe ReplicaSets e disponibilidade durante a tentativa de atualizacao.

[Dicas graduais deste desafio](DICAS.md#11). Tente primeiro; abra uma dica por vez.
Com duas replicas saudaveis, salve a revisao atual do Deployment. Introduza uma
imagem inexistente somente no treino, observe o rollout e recupere a revisao
anterior com rollback. Aceite: imagem original, duas replicas Ready e resposta
pelo Service. Explique por que apagar um Pod nao corrige um template errado.

### 12. Rede e exposicao (20 minutos; YAML e revisao)

**Por que praticar:** NetworkPolicy descreve acesso de rede e Ingress descreve roteamento HTTP. A existencia do recurso na API nao prova que ha um componente executando essas regras.

**Por onde comecar:** Separe destino, origem e porta na politica; depois host, caminho e Service no Ingress. Use kubectl explain e dry-run=server para conferir os campos.

[Dicas graduais deste desafio](DICAS.md#12). Tente primeiro; abra uma dica por vez.
Escreva uma NetworkPolicy para permitir entrada em ckad-api:8080 somente dos
pods com label role=client. Escreva um Ingress para api.ckad.test apontando para
ckad-api:8080, com pathType=Prefix. Valide os manifests com dry-run=server.
Aceite aqui: sintaxe e seletores corretos, e explicacao dos componentes faltantes.
Bloqueio de rede e roteamento HTTP NAO estao comprovados sem CNI/controller
compativeis. Nao instale componentes nem altere o CNI deste cluster para esta tarefa.

## Como vamos corrigir juntos

Envie: incidente, sintoma, comando usado, evidencia, hipotese e correcao proposta.
Depois da tentativa, rode check. Vamos pontuar diagnostico, mudanca minima,
validacao funcional e capacidade de explicar o mecanismo, nao so velocidade.

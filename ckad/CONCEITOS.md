# Conceitos para entender antes de decorar comandos

## 1. Pod, ReplicaSet e Deployment

Pod e a unidade em que containers executam. Containers do mesmo Pod compartilham
rede e podem compartilhar volumes. O Pod pode ser substituido e mudar de IP.
ReplicaSet mantem a quantidade desejada de pods. Deployment controla ReplicaSets
e a transicao entre versoes. Alterar o template do Deployment provoca rollout;
alterar somente replicas normalmente escala o ReplicaSet atual.

No projeto: a imagem vem da CI; o Deployment define como executa-la.
Pergunta: apagar um Pod de um Deployment equivale a parar a aplicacao?

## 2. Estado desejado e observado

spec descreve o que voce quer; status mostra o que os controllers observaram.
Um apply bem-sucedido comprova que a API aceitou o objeto, nao que a aplicacao
ficou saudavel. Observe generation, rollout, Ready e resposta HTTP.

No seu GitOps, Argo compara Git com os recursos. Em ckad-practice nao ha uma
Application Argo: voce pode corrigir o recurso diretamente. Isso separa o
selfHeal do Argo da reposicao de pods feita pelo controller do Kubernetes.

## 3. Service, labels e EndpointSlice

Um Service fornece um endereco estavel. O selector encontra os pods pelos
labels; os EndpointSlices representam os destinos. port e a porta do Service;
targetPort aponta para a porta do backend. containerPort nao abre uma porta
sozinho: o processo precisa estar escutando nela.

No mesmo namespace, ckad-api resolve o Service; o nome completo e
ckad-api.ckad-practice.svc.cluster.local. Pod Ready e acesso pelo Service sao
verificacoes diferentes. Fonte: https://kubernetes.io/docs/concepts/services-networking/service/

## 4. Running nao significa Ready

Running e uma fase do Pod; Ready indica se ele esta pronto para receber trafego.
Readiness controla sua elegibilidade como backend. Liveness pode reiniciar o
container quando uma falha persistente e detectada. Startup protege uma
inicializacao lenta antes de readiness/liveness comecarem a atuar.

Uma readiness quebrada pode deixar o processo vivo e fora dos destinos prontos.
Remover a probe pode esconder o erro. Fonte: https://kubernetes.io/docs/concepts/workloads/pods/probes/

## 5. ConfigMap e Secret

ConfigMap guarda configuracao nao sigilosa. Secret destina-se a dados sensiveis;
base64 e codificacao, nao criptografia. Um nome de objeto correto com uma chave
incorreta ainda pode impedir a inicializacao. Variaveis de ambiente normalmente
exigem recriar o Pod para incorporar uma mudanca no objeto de origem.

Use somente valores ficticios nos exercicios. Nao traga tokens reais do GitHub
ou do Argo. Fonte: https://kubernetes.io/docs/concepts/configuration/secret/

## 6. Requests, limits e quota

Requests influenciam o agendamento e a reserva de capacidade. Limits restringem
o consumo: CPU pode sofrer throttling; memoria excedida pode resultar em OOMKilled.
ResourceQuota limita o consumo agregado do namespace. Um Pod Pending por falta
de capacidade e diferente de uma criacao rejeitada por quota.

No treino, consulte a quota antes de adicionar um container. 100m equivale a
0,1 CPU. Mi mede memoria; nao confunda 128Mi com 128m.

## 7. Imagem e comando

ImagePullBackOff aponta para falha ao obter a imagem; nao prova bug no codigo.
CrashLoopBackOff indica espera crescente entre reinicios. Investigue logs,
inclusive --previous, e a ultima terminacao do container. command substitui
o ENTRYPOINT da imagem; args substitui seu CMD.

A aplicacao usa node src/server.js. O node Kind acessa platform-registry:5000;
localhost dentro dele nao aponta para o Ubuntu host.

## 8. SecurityContext, ServiceAccount e RBAC

SecurityContext governa aspectos do processo, como UID e escalacao de privilegios.
ServiceAccount representa a identidade do workload perante a API. Role define
permissoes dentro de um namespace; RoleBinding associa essas permissoes a sujeitos.
Executar como root no container nao concede automaticamente permissao na API.

No baseline usamos UID 1000, runAsNonRoot e nenhum token de API montado.
Nao resolva uma falha de UID tornando o container privilegiado.

## 9. Volumes e initContainers

emptyDir acompanha a vida do Pod, nao apenas a de um processo. Reiniciar o
container nao e o mesmo que substituir o Pod. PVC solicita armazenamento que
pode sobreviver a substituicao do Pod. Um initContainer comum termina antes
dos containers principais; se ele falhar, o principal pode nunca iniciar.

## 10. Job e CronJob

Deployment espera um processo duradouro. Job representa trabalho que termina;
codigo de saida e retentativas importam. CronJob agenda Jobs. concurrencyPolicy
Forbid evita execucoes simultaneas daquele CronJob; suspend impede novos Jobs,
mas nao encerra os que ja estao rodando.

## 11. NetworkPolicy e Ingress

NetworkPolicy seleciona pods e declara trafego permitido, aplicado por um CNI
compativel. Regras ingress/egress e acesso a DNS precisam ser considerados.
Um objeto aceito pela API sem enforcement nao comprova bloqueio.
Fonte: https://kubernetes.io/docs/concepts/services-networking/network-policies/

Ingress descreve roteamento HTTP(S) e depende de um controller. Port-forward
e uma ferramenta de acesso/debug e nao substitui um teste de Service DNS ou Ingress.

## 12. Metodo de diagnostico

Observe -> formule uma hipotese -> teste -> corrija -> valide o comportamento.
Use get para visao geral, describe para eventos/configuracao, logs para o processo
e exec para testar a comunicacao. Nao reinicie tudo como primeira tentativa.
Na CKAD, pratique editar YAML com rapidez, mas sempre confirme contexto/namespace.

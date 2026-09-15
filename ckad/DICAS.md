# Dicas graduais: abra somente depois de tentar

Use a visualizacao Markdown para expandir uma dica por vez. No arquivo-fonte,
as dicas ficam visiveis. A terceira e mais direta; tente as anteriores primeiro.
Volte aos [enunciados](EXERCICIOS.md) para conferir os criterios de aceite.

## 01
<details>
<summary>Dica 1</summary>

Um Service pode existir sem destinos utilizaveis.

</details>

<details>
<summary>Dica 2</summary>

Compare seus selectors com os labels dos pods e os EndpointSlices.

</details>

<details>
<summary>Dica 3 (mais direta)</summary>

Corrija a selecao do Service; o backend original usa app=ckad-api.

</details>


## 02
<details>
<summary>Dica 1</summary>

Consulte os eventos e diferencie readiness de liveness.

</details>

<details>
<summary>Dica 2</summary>

Compare a porta da probe com a porta onde o processo realmente escuta.

</details>

<details>
<summary>Dica 3 (mais direta)</summary>

A readiness deve consultar /health na porta 8080.

</details>


## 03
<details>
<summary>Dica 1</summary>

O erro acontece antes do processo Node iniciar.

</details>

<details>
<summary>Dica 2</summary>

Leia a mensagem sobre o objeto/chave de configuracao.

</details>

<details>
<summary>Dica 3 (mais direta)</summary>

api-settings possui a chave APP_ENV; preserve valueFrom na referencia.

</details>


## 04
<details>
<summary>Dica 1</summary>

Observe image e os eventos de pull.

</details>

<details>
<summary>Dica 2</summary>

Consulte /v2/platform-sample-application/tags/list no registry local.

</details>

<details>
<summary>Dica 3 (mais direta)</summary>

Reponha o SHA documentado, usando platform-registry:5000 dentro do cluster.

</details>


## 05
<details>
<summary>Dica 1</summary>

Consulte logs --previous quando houver reinicio.

</details>

<details>
<summary>Dica 2</summary>

Compare command/args com o Dockerfile original.

</details>

<details>
<summary>Dica 3 (mais direta)</summary>

Remova o override invalido ou use node src/server.js.

</details>


## 06
<details>
<summary>Dica 1</summary>

Leia os eventos e o securityContext.

</details>

<details>
<summary>Dica 2</summary>

Compare o UID solicitado com runAsNonRoot.

</details>

<details>
<summary>Dica 3 (mais direta)</summary>

Use UID 1000 preservando as demais restricoes.

</details>


## 07

<details>
<summary>Dica 1</summary>

Separe configuracao, identidade e permissoes.

</details>

<details>
<summary>Dica 2</summary>

Confira serviceAccountName e os subjects do RoleBinding.

</details>

<details>
<summary>Dica 3 (mais direta)</summary>

Teste auth can-i usando --as=system:serviceaccount:ckad-practice:reader-demo, com contexto e namespace explicitos.

</details>

## 08

<details>
<summary>Dica 1</summary>

Inclua o Pod extra do rollout na conta.

</details>

<details>
<summary>Dica 2</summary>

Confira describe resourcequota e eventos do ReplicaSet.

</details>

<details>
<summary>Dica 3 (mais direta)</summary>

Some recursos de tres Pods da API durante maxSurge=1, mais cliente e outros Pods existentes.

</details>

## 09

<details>
<summary>Dica 1</summary>

Use um volume com mounts nos dois containers.

</details>

<details>
<summary>Dica 2</summary>

O modulo fs do Node permite escrever e ler o arquivo sem ferramentas extras.

</details>

<details>
<summary>Dica 3 (mais direta)</summary>

Garanta permissao de escrita no mount. emptyDir dura enquanto o Pod existe, nao sobrevive a sua substituicao.

</details>

## 10

<details>
<summary>Dica 1</summary>

Uma falha HTTP precisa produzir codigo de saida diferente de zero.

</details>

<details>
<summary>Dica 2</summary>

O Job precisa de restartPolicy Never ou OnFailure; backoffLimit e TTL ficam no spec do Job.

</details>

<details>
<summary>Dica 3 (mais direta)</summary>

Use create job NOME --from=cronjob/NOME com contexto e namespace explicitos. suspend bloqueia disparos agendados, nao Jobs manuais.

</details>

## 11

<details>
<summary>Dica 1</summary>

Salve a revisao saudavel antes de alterar a imagem.

</details>

<details>
<summary>Dica 2</summary>

Compare os ReplicaSets antigo e novo; disponibilidade antiga nao prova sucesso da nova versao.

</details>

<details>
<summary>Dica 3 (mais direta)</summary>

Use rollout undo com --to-revision e valide imagem, replicas e acesso pelo Service. Fixe contexto e namespace.

</details>

## 12

<details>
<summary>Dica 1</summary>

Separe os Pods protegidos das origens permitidas.

</details>

<details>
<summary>Dica 2</summary>

podSelector em ingress.from sem namespaceSelector seleciona origens no mesmo namespace.

</details>

<details>
<summary>Dica 3 (mais direta)</summary>

Confira backend.service no Ingress. dry-run=server nao comprova aplicacao de politica, DNS ou roteamento HTTP.

</details>

Uma correcao que remove probes ou desativa seguranca pode esconder o sintoma,
mas nao cumpre o objetivo. O reset e uma saida de emergencia, nao uma resposta
para o exercicio: explique a causa e a evidencia encontrada.

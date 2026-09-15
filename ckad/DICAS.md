# Dicas graduais: abra somente depois de tentar

## 01
1. Um Service pode existir sem destinos utilizaveis.
2. Compare seus selectors com os labels dos pods e os EndpointSlices.
3. Corrija a selecao do Service; o backend original usa app=ckad-api.

## 02
1. Consulte os eventos e diferencie readiness de liveness.
2. Compare a porta da probe com a porta onde o processo realmente escuta.
3. A readiness deve consultar /health na porta 8080.

## 03
1. O erro acontece antes do processo Node iniciar.
2. Leia a mensagem sobre o objeto/chave de configuracao.
3. api-settings possui a chave APP_ENV; preserve valueFrom na referencia.

## 04
1. Observe image e os eventos de pull.
2. Consulte /v2/platform-sample-application/tags/list no registry local.
3. Reponha o SHA documentado, usando platform-registry:5000 dentro do cluster.

## 05
1. Consulte logs --previous quando houver reinicio.
2. Compare command/args com o Dockerfile original.
3. Remova o override invalido ou use node src/server.js.

## 06
1. Leia os eventos e o securityContext.
2. Compare o UID solicitado com runAsNonRoot.
3. Use UID 1000 preservando as demais restricoes.

Uma correcao que remove probes ou desativa seguranca pode esconder o sintoma,
mas nao cumpre o objetivo. O reset e uma saida de emergencia, nao uma resposta
para o exercicio: explique a causa e a evidencia encontrada.

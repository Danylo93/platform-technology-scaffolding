#!/usr/bin/env bash
set -euo pipefail

action=${1:-status}
cluster=platform-lab
registry=platform-registry
runner=platform-lab-runner.service
context=kind-platform-lab

case "$action" in
  start)
    docker info >/dev/null
    mapfile -t nodes < <(docker ps -a --filter "label=io.x-k8s.kind.cluster=$cluster" --format '{{.Names}}')
    if ((${#nodes[@]} == 0)); then
      echo 'Existing platform-lab cluster not found; nothing was created.' >&2
      exit 1
    fi
    docker start "$registry" "${nodes[@]}"
    ready=false
    for attempt in {1..30}; do
      if kubectl --context "$context" wait --for=condition=Ready nodes --all --timeout=5s 2>/dev/null; then
        ready=true
        break
      fi
      sleep 2
    done
    "$ready" || { echo 'Cluster did not become Ready' >&2; exit 1; }
    curl --fail --silent --show-error http://localhost:5000/v2/
    systemctl --user start "$runner"
    ;;
  stop)
    if pgrep -f '[/]Runner.Worker' >/dev/null; then
      echo 'An Actions job is running. Wait for it to finish before stopping the lab.' >&2
      exit 1
    fi
    systemctl --user stop "$runner"
    mapfile -t nodes < <(docker ps -a --filter "label=io.x-k8s.kind.cluster=$cluster" --format '{{.Names}}')
    if ((${#nodes[@]})); then
      docker stop --timeout 30 "${nodes[@]}"
    fi
    docker stop "$registry"
    ;;
  status)
    docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
    systemctl --user is-active "$runner"
    kubectl --context "$context" get nodes
    kubectl --context "$context" get pods -A
    kubectl --context "$context" get applications -n argocd
    ;;
  *)
    echo 'Usage: bash scripts/lab-control.sh {start|stop|status}' >&2
    exit 2
    ;;
esac

#!/usr/bin/env bash
# retry.sh - repete um comando com backoff exponencial ate ter sucesso.
# O comando de espera e injetavel via RETRY_SLEEP (padrao: sleep); recebe os
# segundos como unico argumento (util em testes: RETRY_SLEEP=echo).
# Saida: 0 sucesso | codigo do ultimo erro do comando apos esgotar tentativas | 2 uso incorreto
set -euo pipefail

uso() {
  cat <<'USO'
Uso: retry.sh [-n TENTATIVAS] [-d ATRASO] [-f FATOR] [-m MAX] CMD [ARGS...]
  -n  numero maximo de tentativas (padrao 5)
  -d  atraso inicial em segundos (padrao 1)
  -f  fator multiplicador do atraso (padrao 2)
  -m  atraso maximo em segundos (padrao 60)
Ambiente: RETRY_SLEEP (comando de espera, padrao "sleep")
Saida: 0 sucesso, codigo do comando se esgotar tentativas, 2 uso incorreto.
USO
}

tentativas=5
atraso=1
fator=2
maximo=60
if [[ ${1-} == --help ]]; then uso; exit 0; fi
while getopts ":n:d:f:m:h" opt; do
  case "$opt" in
    n) tentativas=$OPTARG ;;
    d) atraso=$OPTARG ;;
    f) fator=$OPTARG ;;
    m) maximo=$OPTARG ;;
    h) uso; exit 0 ;;
    :) echo "retry.sh: -$OPTARG exige valor" >&2; exit 2 ;;
    *) echo "retry.sh: opcao invalida -$OPTARG" >&2; exit 2 ;;
  esac
done
shift $((OPTIND - 1))
if [[ ${1-} == --help ]]; then uso; exit 0; fi
if (( $# == 0 )); then uso >&2; exit 2; fi
for v in "$tentativas" "$atraso" "$fator" "$maximo"; do
  [[ $v =~ ^[0-9]+$ ]] || { echo "retry.sh: valores numericos devem ser inteiros >= 0" >&2; exit 2; }
done
if (( tentativas < 1 )); then echo "retry.sh: TENTATIVAS deve ser >= 1" >&2; exit 2; fi

espera=${RETRY_SLEEP:-sleep}
rc=0
for ((i = 1; i <= tentativas; i++)); do
  rc=0
  "$@" || rc=$?
  if (( rc == 0 )); then exit 0; fi
  if (( i == tentativas )); then break; fi
  if (( atraso > maximo )); then atraso=$maximo; fi
  echo "retry.sh: tentativa $i/$tentativas falhou (codigo $rc); aguardando ${atraso}s" >&2
  # shellcheck disable=SC2086
  $espera "$atraso"
  atraso=$(( atraso * fator ))
done
echo "retry.sh: esgotadas $tentativas tentativas" >&2
exit "$rc"

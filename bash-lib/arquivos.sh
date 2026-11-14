#!/usr/bin/env bash
# arquivos.sh - tempdir seguro com trap e lock exclusivo com flock.
# Funcoes (para `source`): arq_criar_tempdir (define ARQ_TMPDIR e instala trap EXIT),
#                          arq_limpar, arq_com_lock ARQUIVO CMD...
# CLI:
#   tmprun CMD...        executa CMD com ARQ_TMPDIR exportado; remove o diretorio ao final
#   lock ARQUIVO CMD...  executa CMD segurando flock em ARQUIVO (nao bloqueia)
# Saida: codigo do comando | 75 lock ocupado | 2 uso incorreto | 1 falha ao criar tempdir
set -euo pipefail

ARQ_TMPDIR=""

arq_uso() {
  cat <<'USO'
Uso: arquivos.sh tmprun CMD [ARGS...]
     arquivos.sh lock ARQUIVO CMD [ARGS...]
  tmprun  cria um diretorio temporario (modo 700), exporta ARQ_TMPDIR,
          roda o comando e remove o diretorio ao sair (trap EXIT).
  lock    obtem flock exclusivo nao bloqueante em ARQUIVO e roda o comando.
Saida: codigo do comando; 75 se o lock estiver ocupado; 2 uso incorreto.
USO
}

# Remove o tempdir (idempotente). Usado pelo trap.
arq_limpar() {
  if [[ -n $ARQ_TMPDIR && -d $ARQ_TMPDIR ]]; then rm -rf -- "$ARQ_TMPDIR"; fi
  ARQ_TMPDIR=""
}

# Cria o tempdir e registra a limpeza em EXIT/INT/TERM.
arq_criar_tempdir() {
  ARQ_TMPDIR=$(mktemp -d "${TMPDIR:-/tmp}/arq.XXXXXXXX") || return 1
  chmod 700 "$ARQ_TMPDIR"
  trap arq_limpar EXIT
  trap 'exit 130' INT
  trap 'exit 143' TERM
  export ARQ_TMPDIR
}

# arq_com_lock ARQUIVO CMD... : 75 se outro processo ja segura o lock.
arq_com_lock() {
  (( $# >= 2 )) || return 2
  local arq="$1"
  shift
  (
    flock -n 9 || exit 75
    "$@"
  ) 9>"$arq"
}

arq_main() {
  case "${1-}" in
    -h | --help) arq_uso; return 0 ;;
    "") arq_uso >&2; return 2 ;;
  esac
  local sub="$1"
  shift
  local rc=0
  case "$sub" in
    tmprun)
      (( $# >= 1 )) || { echo "arquivos.sh: falta o comando" >&2; return 2; }
      arq_criar_tempdir || { echo "arquivos.sh: falha ao criar tempdir" >&2; return 1; }
      "$@" || rc=$?
      return "$rc"
      ;;
    lock)
      (( $# >= 2 )) || { echo "arquivos.sh: uso: lock ARQUIVO CMD..." >&2; return 2; }
      arq_com_lock "$@" || rc=$?
      if (( rc == 75 )); then echo "arquivos.sh: lock ocupado" >&2; fi
      return "$rc"
      ;;
    *) echo "arquivos.sh: subcomando desconhecido '$sub'" >&2; return 2 ;;
  esac
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then arq_main "$@"; fi

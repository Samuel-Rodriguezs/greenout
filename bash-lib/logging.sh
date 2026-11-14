#!/usr/bin/env bash
# logging.sh - biblioteca de log com niveis e cores desligaveis.
# Variaveis: LOG_LEVEL (debug|info|warn|error, padrao info)
#            LOG_COLOR (1 forca cor, 0 desliga; padrao: cor so se stderr for terminal)
#            NO_COLOR  (se definida, desliga cor)
# Mensagens vao para stderr no formato "[NIVEL] mensagem".
# Saida: 0 ok | 2 uso incorreto / nivel invalido
set -euo pipefail

log_uso() {
  cat <<'USO'
Uso: logging.sh <nivel> MENSAGEM...
  nivel: debug | info | warn | error
Ambiente: LOG_LEVEL, LOG_COLOR=0|1, NO_COLOR
Mensagens abaixo de LOG_LEVEL sao descartadas (saida 0).
Saida: 0 ok, 2 uso incorreto.
USO
}

log_nivel_num() {
  case "${1,,}" in
    debug) echo 0 ;; info) echo 1 ;; warn) echo 2 ;; error) echo 3 ;;
    *) return 1 ;;
  esac
}

log_usar_cor() {
  [[ -z ${NO_COLOR+x} ]] || return 1
  case "${LOG_COLOR-}" in
    1) return 0 ;;
    0) return 1 ;;
  esac
  [[ -t 2 ]]
}

# log_msg NIVEL MENSAGEM...
log_msg() {
  local nivel="${1,,}"
  shift
  local num atual cfg="${LOG_LEVEL:-info}"
  num=$(log_nivel_num "$nivel") || { echo "logging: nivel invalido '$nivel'" >&2; return 2; }
  atual=$(log_nivel_num "$cfg") || { echo "logging: LOG_LEVEL invalido '$cfg'" >&2; return 2; }
  if (( num < atual )); then return 0; fi
  local cor="" reset="" rotulo="${nivel^^}"
  if log_usar_cor; then
    reset=$'\033[0m'
    case "$nivel" in
      debug) cor=$'\033[36m' ;; info) cor=$'\033[32m' ;;
      warn) cor=$'\033[33m' ;; error) cor=$'\033[31m' ;;
    esac
  fi
  printf '%s[%s]%s %s\n' "$cor" "$rotulo" "$reset" "$*" >&2
}

log_debug() { log_msg debug "$@"; }
log_info() { log_msg info "$@"; }
log_warn() { log_msg warn "$@"; }
log_error() { log_msg error "$@"; }

log_main() {
  case "${1-}" in
    -h | --help) log_uso; return 0 ;;
    "") log_uso >&2; return 2 ;;
  esac
  (( $# >= 2 )) || { echo "logging.sh: falta a mensagem" >&2; return 2; }
  log_msg "$@"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then log_main "$@"; fi

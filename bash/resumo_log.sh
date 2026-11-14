#!/usr/bin/env bash
# Resume um arquivo de log contando linhas ERROR, WARN e INFO.
set -euo pipefail

uso() {
    cat <<'EOF'
Uso: resumo_log.sh [-h|--help] ARQUIVO_LOG

Conta as linhas de ARQUIVO_LOG que contem os niveis ERROR, WARN e INFO
(como palavras inteiras) e imprime:
  ERROR: N
  WARN: N
  INFO: N
EOF
}

if [[ $# -eq 1 && ( "$1" == "-h" || "$1" == "--help" ) ]]; then
    uso
    exit 0
fi

if [[ $# -ne 1 ]]; then
    uso >&2
    exit 2
fi

log=$1
if [[ ! -f "$log" ]]; then
    echo "Erro: arquivo nao encontrado: $log" >&2
    exit 1
fi

# grep -c sai com 1 quando nao ha correspondencias; "|| true" evita abortar.
for nivel in ERROR WARN INFO; do
    total=$(grep -cw -- "$nivel" "$log" || true)
    echo "$nivel: $total"
done

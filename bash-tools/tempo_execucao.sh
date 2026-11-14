#!/usr/bin/env bash
# Executa um comando e informa o tempo de execução e o código de saída.
# Uso: tempo_execucao.sh <comando> [args...]
# Saída: código do comando executado; 1 uso inválido; 127 comando não encontrado.
set -euo pipefail

uso() {
  cat <<'USO'
Uso: tempo_execucao.sh <comando> [args...]
Roda o comando e imprime em stderr: "tempo: X.XXX s (saida=N)".
Retorna o mesmo código de saída do comando.
USO
}

case "${1:-}" in
  -h|--help) uso; exit 0 ;;
  "") echo "erro: informe o comando" >&2; uso >&2; exit 1 ;;
esac
if ! command -v "$1" >/dev/null 2>&1; then
  echo "erro: comando não encontrado: $1" >&2; exit 127
fi

inicio="$(date +%s%N)"
codigo=0
"$@" || codigo=$?
fim="$(date +%s%N)"

ms=$(( (fim - inicio) / 1000000 ))
printf 'tempo: %d.%03d s (saida=%d)\n' $((ms / 1000)) $((ms % 1000)) "$codigo" >&2
exit "$codigo"

#!/usr/bin/env bash
# Gera a tabela de multiplicação de um número.
# Uso: tabuada.sh <numero> [ate]   (padrão: ate=10)
# Saída: 0 ok, 1 uso/entrada inválida.
set -euo pipefail

uso() {
  cat <<'USO'
Uso: tabuada.sh <numero> [ate]
Imprime "N x i = R" para i de 1 até <ate> (padrão 10, máximo 1000).
USO
}

case "${1:-}" in
  -h|--help) uso; exit 0 ;;
  "") echo "erro: informe o número" >&2; uso >&2; exit 1 ;;
esac
n="$1"; ate="${2:-10}"
if ! [[ "$n" =~ ^-?[0-9]+$ && "$ate" =~ ^[0-9]+$ ]]; then
  echo "erro: valores devem ser inteiros" >&2; exit 1
fi
if (( ate < 1 || ate > 1000 )); then
  echo "erro: 'ate' deve estar entre 1 e 1000" >&2; exit 1
fi

for (( i = 1; i <= ate; i++ )); do
  echo "$n x $i = $(( n * i ))"
done

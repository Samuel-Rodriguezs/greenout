#!/usr/bin/env bash
# Rotaciona um arquivo de log: log -> log.1 -> log.2 ... descartando o mais antigo.
# Uso: rotacao_logs.sh <arquivo> [max_copias]   (padrão: 3)
# Saída: 0 ok, 1 uso, 2 arquivo inexistente.
set -euo pipefail

uso() {
  cat <<'USO'
Uso: rotacao_logs.sh <arquivo> [max_copias]
Renomeia arquivo.N para arquivo.N+1, move o log atual para .1 e cria um novo vazio.
USO
}

case "${1:-}" in
  -h|--help) uso; exit 0 ;;
  "") echo "erro: informe o arquivo" >&2; uso >&2; exit 1 ;;
esac
arq="$1"
max="${2:-3}"
if ! [[ "$max" =~ ^[1-9][0-9]*$ ]]; then
  echo "erro: max_copias deve ser inteiro positivo" >&2; exit 1
fi
if [[ ! -f "$arq" ]]; then
  echo "erro: arquivo inexistente: $arq" >&2; exit 2
fi

rm -f -- "$arq.$max"
for (( i = max - 1; i >= 1; i-- )); do
  if [[ -f "$arq.$i" ]]; then
    mv -- "$arq.$i" "$arq.$((i + 1))"
  fi
done
mv -- "$arq" "$arq.1"
: > "$arq"
echo "rotacionado: $arq (máx. $max cópias)"

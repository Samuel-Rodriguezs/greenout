#!/usr/bin/env bash
# Gera senhas aleatórias usando /dev/urandom.
# Uso: gerar_senha.sh [-n tamanho] [-c quantidade] [-s]
# Saída: 0 ok, 1 uso inválido.
set -euo pipefail

uso() {
  cat <<'USO'
Uso: gerar_senha.sh [-n tamanho] [-c quantidade] [-s]
  -n   tamanho da senha (padrão 16, mínimo 4, máximo 256)
  -c   quantidade de senhas (padrão 1)
  -s   inclui símbolos
USO
}

tam=16; qtd=1; simb=0
while (( $# > 0 )); do
  case "$1" in
    -h|--help) uso; exit 0 ;;
    -n|-c)
      if (( $# < 2 )); then echo "erro: falta valor para $1" >&2; exit 1; fi
      if [[ "$1" == "-n" ]]; then tam="$2"; else qtd="$2"; fi
      shift 2 ;;
    -s) simb=1; shift ;;
    *) echo "erro: argumento inválido: $1" >&2; uso >&2; exit 1 ;;
  esac
done
for v in "$tam" "$qtd"; do
  if ! [[ "$v" =~ ^[0-9]+$ ]]; then
    echo "erro: valores numéricos inválidos" >&2; exit 1
  fi
done
if (( tam < 4 || tam > 256 || qtd < 1 )); then
  echo "erro: tamanho deve estar entre 4 e 256 e quantidade >= 1" >&2; exit 1
fi

conjunto='A-Za-z0-9'
if (( simb )); then conjunto='A-Za-z0-9!@#$%^&*()_+='; fi
for (( i = 0; i < qtd; i++ )); do
  # head fecha o pipe cedo; || true evita falha por SIGPIPE com pipefail
  senha="$(LC_ALL=C tr -dc "$conjunto" < /dev/urandom | head -c "$tam" || true)"
  echo "$senha"
done

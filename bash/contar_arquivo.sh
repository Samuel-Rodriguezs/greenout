#!/usr/bin/env bash
# Conta linhas e palavras de um arquivo.
set -euo pipefail

uso() {
    cat <<'EOF'
Uso: contar_arquivo.sh [-h|--help] ARQUIVO

Imprime o numero de linhas e de palavras do ARQUIVO:
  linhas: N
  palavras: M
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

arquivo=$1
if [[ ! -f "$arquivo" ]]; then
    echo "Erro: arquivo nao encontrado: $arquivo" >&2
    exit 1
fi

linhas=$(wc -l < "$arquivo")
palavras=$(wc -w < "$arquivo")
# Ultima linha sem '\n' final tambem conta como linha.
if [[ -s "$arquivo" && -n "$(tail -c 1 "$arquivo")" ]]; then
    linhas=$((linhas + 1))
fi

echo "linhas: $((linhas + 0))"
echo "palavras: $((palavras + 0))"

#!/usr/bin/env bash
# FizzBuzz de 1 ate N.
set -euo pipefail

uso() {
    cat <<'EOF'
Uso: fizzbuzz.sh [-h|--help] N

Imprime, uma por linha, a sequencia FizzBuzz de 1 ate N (N >= 0):
multiplos de 3 -> Fizz, de 5 -> Buzz, de ambos -> FizzBuzz.
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

if [[ ! "$1" =~ ^[0-9]+$ ]]; then
    echo "Erro: N deve ser um inteiro nao negativo: $1" >&2
    exit 2
fi

n=$((10#$1))
for ((i = 1; i <= n; i++)); do
    saida=""
    if ((i % 3 == 0)); then saida+="Fizz"; fi
    if ((i % 5 == 0)); then saida+="Buzz"; fi
    echo "${saida:-$i}"
done

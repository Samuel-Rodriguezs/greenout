#!/usr/bin/env bash
# Lista os N maiores arquivos de um diretorio (recursivo).
set -euo pipefail

uso() {
    cat <<'EOF'
Uso: maiores_arquivos.sh [-h|--help] [-n N] DIRETORIO

Lista, do maior para o menor, os N maiores arquivos regulares de DIRETORIO
(recursivamente), no formato "<bytes> <caminho>". Padrao: N=5.
EOF
}

n=5
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help) uso; exit 0 ;;
        -n)
            if [[ $# -lt 2 || ! "$2" =~ ^[0-9]+$ || "$2" -lt 1 ]]; then
                echo "Erro: -n exige um inteiro positivo" >&2
                exit 2
            fi
            n=$2
            shift 2
            ;;
        --) shift; break ;;
        -*) echo "Erro: opcao desconhecida: $1" >&2; uso >&2; exit 2 ;;
        *) break ;;
    esac
done

if [[ $# -ne 1 ]]; then
    uso >&2
    exit 2
fi

dir=$1
if [[ ! -d "$dir" ]]; then
    echo "Erro: diretorio nao encontrado: $dir" >&2
    exit 1
fi

# Ordena por tamanho (desc) e depois por caminho, para saida deterministica.
find "$dir" -type f -printf '%s %p\n' | sort -k1,1nr -k2 | head -n "$n"

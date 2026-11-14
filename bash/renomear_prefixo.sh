#!/usr/bin/env bash
# Renomeia os arquivos de um diretorio acrescentando um prefixo.
set -euo pipefail

uso() {
    cat <<'EOF'
Uso: renomear_prefixo.sh [-h|--help] [--dry-run] PREFIXO DIRETORIO

Renomeia cada arquivo regular de DIRETORIO (nao recursivo) para
PREFIXO<nome>. Com --dry-run apenas mostra o que seria feito.
Saida: "<antigo> -> <novo>" por arquivo. Nao sobrescreve arquivos existentes.
EOF
}

dry=0
args=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help) uso; exit 0 ;;
        --dry-run) dry=1; shift ;;
        --) shift; args+=("$@"); break ;;
        -*) echo "Erro: opcao desconhecida: $1" >&2; uso >&2; exit 2 ;;
        *) args+=("$1"); shift ;;
    esac
done

if [[ ${#args[@]} -ne 2 ]]; then
    uso >&2
    exit 2
fi

prefixo=${args[0]}
dir=${args[1]}

if [[ -z "$prefixo" || "$prefixo" == */* ]]; then
    echo "Erro: prefixo invalido" >&2
    exit 2
fi
if [[ ! -d "$dir" ]]; then
    echo "Erro: diretorio nao encontrado: $dir" >&2
    exit 1
fi

# Coleta antes de renomear para nao reprocessar arquivos ja renomeados.
arquivos=()
while IFS= read -r -d '' f; do
    arquivos+=("$f")
done < <(find "$dir" -maxdepth 1 -type f -print0 | sort -z)

for f in "${arquivos[@]}"; do
    nome=$(basename -- "$f")
    novo="$dir/$prefixo$nome"
    if [[ -e "$novo" ]]; then
        echo "Erro: destino ja existe: $novo" >&2
        exit 1
    fi
    echo "$nome -> $prefixo$nome"
    if [[ $dry -eq 0 ]]; then
        mv -- "$f" "$novo"
    fi
done

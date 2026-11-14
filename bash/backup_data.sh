#!/usr/bin/env bash
# Copia um arquivo para um diretorio de destino acrescentando a data ao nome.
set -euo pipefail

uso() {
    cat <<'EOF'
Uso: backup_data.sh [-h|--help] ARQUIVO DESTINO

Copia ARQUIVO para o diretorio DESTINO (criado se nao existir) com o nome
<base>_AAAA-MM-DD<ext>. A data pode ser fixada com a variavel BACKUP_DATA
(formato AAAA-MM-DD); por padrao e a data de hoje. Se o backup ja existir,
ele e sobrescrito.
EOF
}

if [[ $# -eq 1 && ( "$1" == "-h" || "$1" == "--help" ) ]]; then
    uso
    exit 0
fi

if [[ $# -ne 2 ]]; then
    uso >&2
    exit 2
fi

origem=$1
destino=$2

if [[ ! -f "$origem" ]]; then
    echo "Erro: arquivo nao encontrado: $origem" >&2
    exit 1
fi

data=${BACKUP_DATA:-$(date +%Y-%m-%d)}
if [[ ! "$data" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    echo "Erro: BACKUP_DATA invalida: $data" >&2
    exit 1
fi

nome=$(basename -- "$origem")
if [[ "$nome" == *.* && "${nome%.*}" != "" ]]; then
    base=${nome%.*}
    ext=.${nome##*.}
else
    base=$nome
    ext=""
fi

mkdir -p -- "$destino"
alvo="$destino/${base}_${data}${ext}"
cp -- "$origem" "$alvo"
echo "$alvo"

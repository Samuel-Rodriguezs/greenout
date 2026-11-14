#!/usr/bin/env bash
# Conversor de temperatura entre Celsius, Fahrenheit e Kelvin.
set -euo pipefail

uso() {
    cat <<'EOF'
Uso: temperatura.sh [-h|--help] VALOR DE PARA

Converte VALOR da escala DE para a escala PARA.
Escalas: C (Celsius), F (Fahrenheit), K (Kelvin).
Resultado com duas casas decimais. Exemplo: temperatura.sh 100 C F -> 212.00
EOF
}

if [[ $# -eq 1 && ( "$1" == "-h" || "$1" == "--help" ) ]]; then
    uso
    exit 0
fi

if [[ $# -ne 3 ]]; then
    uso >&2
    exit 2
fi

valor=$1
de=${2^^}
para=${3^^}

if [[ ! "$valor" =~ ^-?([0-9]+(\.[0-9]*)?|\.[0-9]+)$ ]]; then
    echo "Erro: valor invalido: $valor" >&2
    exit 2
fi
for escala in "$de" "$para"; do
    if [[ "$escala" != "C" && "$escala" != "F" && "$escala" != "K" ]]; then
        echo "Erro: escala invalida: $escala (use C, F ou K)" >&2
        exit 2
    fi
done

# Passa por Celsius como escala intermediaria.
resultado=$(awk -v v="$valor" -v de="$de" -v para="$para" 'BEGIN {
    if (de == "C") c = v
    else if (de == "F") c = (v - 32) * 5 / 9
    else c = v - 273.15

    if (para == "C") r = c
    else if (para == "F") r = c * 9 / 5 + 32
    else r = c + 273.15

    if (r > -0.005 && r < 0.005) r = 0
    printf "%.2f", r
}')

if [[ "$de" == "K" && "$(awk -v v="$valor" 'BEGIN { print (v < 0) }')" == "1" ]]; then
    echo "Erro: Kelvin nao pode ser negativo" >&2
    exit 2
fi

echo "$resultado"

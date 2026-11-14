#!/usr/bin/env bash
# Gera um .gitignore para um tipo de projeto.
# Uso: gerar_gitignore.sh <python|node|java|go|bash> [arquivo]
# Saída: 0 ok, 1 uso, 2 tipo desconhecido.
set -euo pipefail

uso() {
  cat <<'USO'
Uso: gerar_gitignore.sh <tipo> [arquivo]
Tipos: python, node, java, go, bash
Sem arquivo, escreve na saída padrão.
USO
}

case "${1:-}" in
  -h|--help) uso; exit 0 ;;
  "") echo "erro: informe o tipo" >&2; uso >&2; exit 1 ;;
esac
tipo="$1"
destino="${2:-}"

gerar() {
  case "$tipo" in
    python) printf '%s\n' '__pycache__/' '*.pyc' '.venv/' 'venv/' '*.egg-info/' 'dist/' 'build/' '.pytest_cache/' ;;
    node)   printf '%s\n' 'node_modules/' 'npm-debug.log*' 'dist/' '.env' 'coverage/' ;;
    java)   printf '%s\n' '*.class' '*.jar' 'target/' '.gradle/' 'build/' '.idea/' ;;
    go)     printf '%s\n' '*.exe' '*.test' '*.out' 'vendor/' 'bin/' ;;
    bash)   printf '%s\n' '*.log' '*.tmp' '*.swp' '.env' ;;
    *) echo "erro: tipo desconhecido: $tipo" >&2; return 2 ;;
  esac
}

if [[ -n "$destino" ]]; then
  conteudo="$(gerar)" || exit 2
  printf '%s\n' "$conteudo" > "$destino"
  echo "gerado: $destino"
else
  gerar || exit 2
fi

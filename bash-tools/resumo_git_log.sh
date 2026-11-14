#!/usr/bin/env bash
# Resume o histórico git: número de commits por autor.
# Uso: resumo_git_log.sh [repositorio]   (padrão: diretório atual)
# Saída: 0 ok, 2 não é repositório git, 3 repositório sem commits.
set -euo pipefail

uso() {
  cat <<'USO'
Uso: resumo_git_log.sh [repositorio]
Imprime "<commits><TAB><autor>" em ordem decrescente e o total.
USO
}

case "${1:-}" in
  -h|--help) uso; exit 0 ;;
esac
repo="${1:-.}"
if ! git -C "$repo" rev-parse --git-dir >/dev/null 2>&1; then
  echo "erro: não é um repositório git: $repo" >&2; exit 2
fi
if ! git -C "$repo" rev-parse --verify HEAD >/dev/null 2>&1; then
  echo "erro: repositório sem commits" >&2; exit 3
fi

git -C "$repo" log --format='%an' \
  | sort | uniq -c | sort -k1,1nr -k2 \
  | awk '{n=$1; $1=""; sub(/^ /,""); printf "%d\t%s\n", n, $0}'
printf 'total\t%s\n' "$(git -C "$repo" rev-list --count HEAD)"

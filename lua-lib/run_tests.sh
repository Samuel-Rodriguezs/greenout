#!/usr/bin/env bash
# Executa todos os testes test_*.lua deste diretório.
cd "$(dirname "$0")" || exit 1
LUA=$(command -v lua || command -v lua5.4 || command -v luajit) || { echo "lua não encontrado"; exit 1; }
export LUA_PATH="$PWD/?.lua;;"
falhas=0
for t in test_*.lua; do
  [ -e "$t" ] || continue
  printf '%s: ' "$t"
  "$LUA" "$t" || { echo "FALHOU: $t"; falhas=$((falhas+1)); }
done
[ "$falhas" -eq 0 ] && echo "Todos os testes passaram" || { echo "$falhas teste(s) falharam"; exit 1; }

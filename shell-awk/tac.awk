# tac.awk - imprime as linhas em ordem inversa (equivalente ao tac).
# Uso: awk -f tac.awk arquivo
{ linhas[NR] = $0 }
END { for (i = NR; i >= 1; i--) print linhas[i] }

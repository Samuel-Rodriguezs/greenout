# dedup.awk - remove linhas duplicadas preservando a ordem da primeira ocorrencia.
# Uso: awk -f dedup.awk arquivo
#      awk -F, -v col=1 -f dedup.awk arquivo   (duplicata definida so pela coluna col)
BEGIN { if (col == "") col = 0 }
!vistos[$col]++

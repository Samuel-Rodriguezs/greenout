# limpar_comentarios.sed - remove comentarios '#' e linhas vazias.
# Uso: sed -f limpar_comentarios.sed script.sh
# Remove comentarios de linha inteira e finais (" # texto"), depois as linhas em branco.
# Atencao: um '#' dentro de strings tambem e tratado como comentario.
s/[[:space:]]*#.*$//
/^[[:space:]]*$/d

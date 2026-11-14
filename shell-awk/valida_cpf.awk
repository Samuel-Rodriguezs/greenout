# valida_cpf.awk - valida o FORMATO de CPFs (nnn.nnn.nnn-nn ou 11 digitos).
# Uso: awk -f valida_cpf.awk cpfs.txt
# Saida: "<cpf><TAB>VALIDO|INVALIDO". Nao calcula digitos verificadores, mas rejeita
# sequencias de digitos todos iguais (111.111.111-11). Linhas vazias sao ignoradas.
NF == 0 { next }
{
    cpf = $0
    gsub(/^[[:space:]]+|[[:space:]]+$/, "", cpf)
    ok = (cpf ~ /^[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}$/ || cpf ~ /^[0-9]{11}$/)
    if (ok) {
        d = cpf; gsub(/[^0-9]/, "", d)
        if (d ~ /^(0+|1+|2+|3+|4+|5+|6+|7+|8+|9+)$/) ok = 0
    }
    print $0 "\t" (ok ? "VALIDO" : "INVALIDO")
}

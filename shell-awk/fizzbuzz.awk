# fizzbuzz.awk - FizzBuzz de 1 ate n.
# Uso: awk -v n=15 -f fizzbuzz.awk </dev/null     (n padrao 100; ignora a entrada)
# n deve ser inteiro >= 0, senao erro em stderr e status 1.
BEGIN {
    if (n == "") n = 100
    if (n !~ /^[0-9]+$/) { print "erro: n invalido: " n > "/dev/stderr"; exit 1 }
    for (i = 1; i <= n; i++) {
        s = ""
        if (i % 3 == 0) s = "Fizz"
        if (i % 5 == 0) s = s "Buzz"
        print (s == "" ? i : s)
    }
}

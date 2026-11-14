local p = require("palindromo")
assert(p.eh_palindromo("arara"))
assert(p.eh_palindromo("A man, a plan, a canal: Panama"))
assert(p.eh_palindromo("Socorram me subi no onibus em Marrocos"))
assert(not p.eh_palindromo("lua"))
assert(p.eh_palindromo(""))        -- vazio
assert(p.eh_palindromo("x"))       -- um caractere
assert(p.eh_palindromo(" ,. "))    -- só pontuação
assert(not p.eh_palindromo("ab"))
assert(p.normalizar("A-b C!") == "abc")
print("ok")

local trie = require("trie")
local t = trie.nova()
assert(t:inserir("casa") and t:inserir("casaco") and t:inserir("caso") and t:inserir("cama"))
assert(not t:inserir("casa"))                -- duplicada
assert(t:tamanho() == 4)
assert(t:contem("casa") and t:contem("casaco"))
assert(not t:contem("cas") and not t:contem("casas") and not t:contem(""))
assert(t:tem_prefixo("cas") and t:tem_prefixo("") and not t:tem_prefixo("x"))
assert(table.concat(t:autocompletar("cas"), ",") == "casa,casaco,caso")
assert(table.concat(t:autocompletar("ca", 2), ",") == "cama,casa")
assert(#t:autocompletar("zzz") == 0)
assert(#t:autocompletar("") == 4)

-- remoção: casa continua existindo como prefixo de casaco
assert(t:remover("casa") and not t:contem("casa") and t:contem("casaco"))
assert(not t:remover("casa") and not t:remover("inexistente") and not t:remover("ca"))
assert(t:tamanho() == 3)
-- poda de ramos vazios
assert(t:remover("casaco"))
assert(not t:tem_prefixo("casa") and t:tem_prefixo("cas"))
assert(t:remover("caso") and not t:tem_prefixo("cas") and t:tem_prefixo("cama"))

-- palavra vazia e UTF-8
local u = trie.nova()
assert(u:inserir("") and u:contem("") and u:tamanho() == 1)
u:inserir("ação"); u:inserir("açúcar")
assert(table.concat(u:autocompletar("aç"), ",") == "ação,açúcar")
assert(u:contem("ação") and not u:contem("aca"))
assert(not pcall(u.inserir, u, 42))
print("ok")

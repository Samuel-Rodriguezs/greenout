local lru = require("lru")
local c = lru.novo(2)
assert(c:obter("a") == nil and c:tamanho() == 0)
assert(c:colocar("a", 1) == nil)
c:colocar("b", 2)
assert(table.concat(c:chaves(), ",") == "b,a")
assert(c:obter("a") == 1)                       -- a vira a mais recente
assert(table.concat(c:chaves(), ",") == "a,b")
local k, v = c:colocar("c", 3)                  -- expulsa b
assert(k == "b" and v == 2)
assert(c:obter("b") == nil and c:obter("c") == 3 and c:obter("a") == 1)
-- atualizar não expulsa
assert(c:colocar("a", 10) == nil and c:tamanho() == 2 and c:obter("a") == 10)
-- espiar não muda a ordem
local antes = table.concat(c:chaves(), ",")
assert(c:espiar("c") == 3 and table.concat(c:chaves(), ",") == antes)
-- remover
assert(c:remover("a") and not c:remover("a") and c:tamanho() == 1)
-- valores falsos são válidos
c:colocar("f", false)
assert(c:obter("f") == false and c:tamanho() == 2)

-- capacidade 1
local u = lru.novo(1)
u:colocar(1, "x")
local ek = u:colocar(2, "y")
assert(ek == 1 and u:obter(1) == nil and u:obter(2) == "y")

-- carga: nunca excede capacidade e guarda os mais recentes
local g = lru.novo(100)
for i = 1, 1000 do g:colocar(i, i * 2) end
assert(g:tamanho() == 100 and g:obter(1000) == 2000 and g:obter(900) == nil and g:obter(901) == 1802)
assert(#g:chaves() == 100)

assert(not pcall(lru.novo, 0))
assert(not pcall(lru.novo, 1.5))
assert(not pcall(c.colocar, c, nil, 1))
print("ok")

local Conjunto = require("conjunto")

local a = Conjunto.novo { 1, 2, 3, 3, 2 }
assert(a:tamanho() == 3 and #a == 3)            -- duplicatas ignoradas
assert(a:contem(2) and not a:contem(9) and not a:contem(nil))
assert(a:remover(2) and not a:remover(2) and not a:remover(nil) and #a == 2)
assert(Conjunto.novo():tamanho() == 0)

local x, y = Conjunto.novo { 1, 2, 3 }, Conjunto.novo { 3, 4 }
assert(tostring(x + y) == "{1, 2, 3, 4}")
assert(tostring(x * y) == "{3}")
assert(tostring(x - y) == "{1, 2}")
assert(tostring(x:diferenca_simetrica(y)) == "{1, 2, 4}")
assert(x:uniao(y) == y:uniao(x))
assert(x == Conjunto.novo { 3, 2, 1 })
assert(x ~= y)
assert(Conjunto.novo { 1 } <= x and Conjunto.novo { 1 } < x and not (x < x) and x <= x)
assert(not (y <= x))
assert(x:disjunto(Conjunto.novo { 7 }) and not x:disjunto(y))
assert(Conjunto.novo():subconjunto_de(x))        -- vazio é subconjunto de tudo

-- operações não mutam os operandos
assert(#x == 3 and #y == 2)

-- strings e tipos mistos
local s = Conjunto.novo { "b", "a" }
assert(tostring(s) == "{a, b}")
local misto = Conjunto.novo { 1, "a", true }
assert(#misto:itens() == 3)  -- não quebra ao ordenar tipos mistos

-- valores inválidos
assert(not pcall(a.adicionar, a, nil))
assert(not pcall(a.adicionar, a, 0 / 0))
assert(tostring(Conjunto.novo()) == "{}")
print("ok")

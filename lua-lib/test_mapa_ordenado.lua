local Mapa = require("mapa_ordenado")

local m = Mapa.novo()
assert(#m == 0 and m:primeira() == nil and m:ultima() == nil)
m:definir("z", 1):definir("a", 2):definir("m", 3)
assert(#m == 3 and m:obter("a") == 2 and m:obter("x") == nil)
assert(table.concat(m:chaves(), "") == "zam")          -- ordem de inserção
assert(table.concat(m:valores(), "") == "123")

m:definir("z", 10)                                       -- atualizar mantém posição
assert(table.concat(m:chaves(), "") == "zam" and m:obter("z") == 10 and #m == 3)

m:remover("a")
assert(table.concat(m:chaves(), "") == "zm" and not m:tem("a") and #m == 2)
m:remover("inexistente"); m:remover(nil)
assert(#m == 2)
m:definir("a", 5)                                        -- reinserida vai ao fim
assert(table.concat(m:chaves(), "") == "zma" and m:ultima() == "a" and m:primeira() == "z")

-- definir nil remove
m:definir("m", nil)
assert(not m:tem("m") and table.concat(m:chaves(), "") == "za")

-- iteração em ordem
local ks = {}
for k, v in m:pares() do ks[#ks + 1] = k .. "=" .. v end
assert(table.concat(ks, ",") == "z=10,a=5")

-- remover durante a iteração
local m2 = Mapa.novo { { 1, "a" }, { 2, "b" }, { 3, "c" } }
local vistos = 0
for k in m2:pares() do vistos = vistos + 1; m2:remover(3) end
assert(vistos == 2 and #m2 == 2)

-- valores false e chaves não-string
local m3 = Mapa.novo()
m3:definir(true, false):definir(1.5, "x")
assert(m3:tem(true) and m3:obter(true) == false and m3:obter(1.5) == "x")

-- chaves inválidas
assert(not pcall(m.definir, m, nil, 1))
assert(not pcall(m.definir, m, 0 / 0, 1))

-- chaves() devolve cópia
local c = m:chaves(); c[1] = "q"
assert(m:primeira() == "z")
print("ok")

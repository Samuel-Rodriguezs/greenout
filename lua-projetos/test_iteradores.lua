local it = require("iteradores")
local function junta(l) return table.concat(l, ",") end
assert(junta(it.lista(it.faixa(1, 5))) == "1,2,3,4,5")
assert(junta(it.lista(it.faixa(10, 1, -3))) == "10,7,4,1")
assert(#it.lista(it.faixa(5, 1)) == 0)           -- faixa vazia
assert(junta(it.lista(it.faixa(3, 3))) == "3")
assert(not pcall(it.faixa, 1, 5, 0))

-- infinito + pegar (preguiça)
assert(junta(it.lista(it.pegar(it.fibonacci(), 10))) == "0,1,1,2,3,5,8,13,21,34")
assert(#it.lista(it.pegar(it.fibonacci(), 0)) == 0)
assert(#it.lista(it.pegar(it.faixa(1, 3), 10)) == 3)   -- pedir mais que existe

-- composição
local pares_ao_quadrado = it.mapear(it.filtrar(it.faixa(1, 10), function(x) return x % 2 == 0 end),
  function(x) return x * x end)
assert(junta(it.lista(pares_ao_quadrado)) == "4,16,36,64,100")
assert(junta(it.lista(it.pegar(it.filtrar(it.fibonacci(), function(x) return x % 2 == 0 end), 4))) == "0,2,8,34")

-- zip para no menor
local z = it.lista(it.zip(it.faixa(1, 5), it.pegar(it.fibonacci(), 3)))
assert(#z == 3 and z[3][1] == 3 and z[3][2] == 1)
assert(#it.lista(it.zip(it.faixa(1, 0), it.faixa(1, 3))) == 0)

-- árvore em pré-ordem
local arv = { valor = 1, filhos = { { valor = 2, filhos = { { valor = 3 } } }, { valor = 4 } } }
assert(junta(it.lista(it.arvore(arv))) == "1,2,3,4")
assert(#it.lista(it.arvore(nil)) == 0)

-- permutações
local ps = it.lista(it.permutacoes({ 1, 2, 3 }))
assert(#ps == 6)
local vistos = {}
for _, p in ipairs(ps) do vistos[junta(p)] = true end
local n = 0
for _ in pairs(vistos) do n = n + 1 end
assert(n == 6)                                   -- todas distintas
assert(#it.lista(it.permutacoes({})) == 1)       -- uma permutação vazia
assert(#it.lista(it.permutacoes({ 7 })) == 1)
local lista_orig = { 1, 2, 3 }
it.lista(it.permutacoes(lista_orig))
assert(junta(lista_orig) == "1,2,3")             -- não altera a entrada

-- gerador personalizado com argumentos extras
local g = it.gerador(function(emitir, a, b) emitir(a); emitir(b) end, "x", "y")
assert(g() == "x" and g() == "y")
print("ok")

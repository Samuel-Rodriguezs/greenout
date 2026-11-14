local Prng = require("prng")

-- valores conhecidos da recorrência
local g = Prng.novo(0)
assert(g:proximo() == 1013904223)
assert(g:proximo() == (1664525 * 1013904223 + 1013904223) & 0xFFFFFFFF)
assert(Prng.novo(1):proximo() == 1015568748)

-- determinismo
local a, b = Prng.novo(42), Prng.novo(42)
for _ = 1, 100 do assert(a:proximo() == b:proximo()) end
assert(Prng.novo(1):proximo() ~= Prng.novo(2):proximo())

-- semente negativa, float inteiro e inválida
assert(Prng.novo(-1):proximo() >= 0)
assert(Prng.novo(5.0):proximo() == Prng.novo(5):proximo())
assert(not pcall(Prng.novo, 1.5) and not pcall(Prng.novo, "x"))
assert(Prng.novo():proximo() >= 0)         -- semente padrão (os.time)

-- real em [0,1)
local r = Prng.novo(7)
for _ = 1, 1000 do local x = r:real(); assert(x >= 0 and x < 1) end

-- inteiro dentro do intervalo, cobrindo todos os valores
local gi = Prng.novo(123)
local vistos = {}
for _ = 1, 500 do
  local v = gi:inteiro(1, 6)
  assert(v >= 1 and v <= 6)
  vistos[v] = true
end
for i = 1, 6 do assert(vistos[i], "faltou " .. i) end
assert(gi:inteiro(5, 5) == 5)
for _ = 1, 50 do local v = gi:inteiro(-3, -1); assert(v >= -3 and v <= -1) end
for _ = 1, 50 do local v = gi:inteiro(3); assert(v >= 1 and v <= 3) end
assert(not pcall(gi.inteiro, gi, 5, 1) and not pcall(gi.inteiro, gi, 1.5, 3))

-- distribuição razoável (média perto do centro)
local soma = 0
for _ = 1, 5000 do soma = soma + gi:real() end
assert(math.abs(soma / 5000 - 0.5) < 0.03)

-- escolher / embaralhar
local e = Prng.novo(9)
assert(e:escolher({}) == nil and e:escolher({ "só" }) == "só")
local lista = { 1, 2, 3, 4, 5, 6, 7, 8 }
local emb = Prng.novo(9):embaralhar({ table.unpack(lista) })
table.sort(emb)
assert(table.concat(emb, ",") == table.concat(lista, ","))      -- mesma multiconjunto
local e1 = Prng.novo(5):embaralhar({ 1, 2, 3, 4, 5, 6, 7, 8 })
local e2 = Prng.novo(5):embaralhar({ 1, 2, 3, 4, 5, 6, 7, 8 })
assert(table.concat(e1) == table.concat(e2))                    -- determinístico
assert(#Prng.novo(1):embaralhar({}) == 0)

-- salvar/restaurar estado
local s = Prng.novo(11)
s:proximo()
local est = s:estado()
local x1 = s:proximo()
s:restaurar(est)
assert(s:proximo() == x1)
assert(type(s:booleano()) == "boolean")
print("ok")

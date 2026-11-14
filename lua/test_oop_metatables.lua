local m = require("oop_metatables")
local a = m.Animal.novo("Gato", "miau")
assert(a:falar() == "Gato faz miau")
assert(tostring(a) == "Animal(Gato)")
assert(m.Animal.novo("X"):falar() == "X faz ...")
local c = m.Cachorro.novo("Rex")
assert(c:falar() == "Rex faz au")          -- herdado
assert(c:buscar() == "Rex busca a bola")
assert(tostring(c) == "Cachorro(Rex)")
assert(a.buscar == nil)                     -- não vaza para a base
local V = m.Vetor
local s = V.novo(1, 2) + V.novo(3, 4)
assert(s == V.novo(4, 6))
assert(s ~= V.novo(4, 7))
assert(V.novo(1, 1) < V.novo(2, 2))
assert(not (V.novo(2, 2) < V.novo(1, 1)))
assert(tostring(s) == "(4, 6)")
print("ok")

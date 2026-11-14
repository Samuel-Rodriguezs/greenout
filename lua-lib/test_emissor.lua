local Emissor = require("emissor")

local e = Emissor.novo()
assert(e:emitir("nada") == 0)               -- sem ouvintes

local log = {}
local f1 = e:ligar("msg", function(x, y) log[#log + 1] = "f1:" .. x .. y end)
e:ligar("msg", function(x) log[#log + 1] = "f2:" .. x end)
assert(e:emitir("msg", "a", "b") == 2)
assert(table.concat(log, ",") == "f1:ab,f2:a")   -- ordem de registro

-- uma_vez
local n = 0
e:uma_vez("ping", function() n = n + 1 end)
assert(e:emitir("ping") == 1 and e:emitir("ping") == 0 and n == 1)

-- desligar específico, inexistente e total
assert(e:desligar("msg", f1) == 1 and e:desligar("msg", f1) == 0)
assert(e:contar("msg") == 1)
assert(e:desligar("msg") == 1 and e:contar("msg") == 0 and e:desligar("zzz") == 0)

-- mesmo ouvinte registrado duas vezes: remove um por vez
local c = 0
local g = function() c = c + 1 end
e:ligar("x", g); e:ligar("x", g)
e:desligar("x", g)
e:emitir("x")
assert(c == 1)

-- ouvinte que se remove durante o disparo não afeta os demais
local ordem = {}
local h
h = e:ligar("y", function() ordem[#ordem + 1] = 1; e:desligar("y", h) end)
e:ligar("y", function() ordem[#ordem + 1] = 2 end)
assert(e:emitir("y") == 2 and e:emitir("y") == 1)
assert(table.concat(ordem, "") == "122")

-- ouvinte que registra outro durante o disparo: só vale no próximo
local z = 0
e:uma_vez("w", function() e:ligar("w", function() z = z + 1 end) end)
e:emitir("w")
assert(z == 0)
e:emitir("w")
assert(z == 1)

-- eventos não-string e erros
e:ligar(42, function() end)
assert(e:emitir(42) == 1)
assert(not pcall(e.ligar, e, "a", "nao-funcao"))
assert(not pcall(e.ligar, e, nil, function() end))
local eventos = e:eventos()
assert(#eventos >= 1)

-- erro em ouvinte propaga
e:ligar("boom", function() error("falhou") end)
assert(not pcall(e.emitir, e, "boom"))
print("ok")

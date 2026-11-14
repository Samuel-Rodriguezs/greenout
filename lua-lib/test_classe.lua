local classe = require("classe")

local Animal = classe.nova(nil, "Animal")
function Animal:init(nome) self.nome = nome end
function Animal:falar() return self.nome .. " faz um som" end
function Animal:tipo() return "animal" end

local Cao = classe.nova(Animal, "Cao")
function Cao:init(nome, raca)
  classe.super(Cao, "init", self, nome)
  self.raca = raca
end
function Cao:falar() return self.nome .. " late" end

local Filhote = classe.nova(Cao, "Filhote")

local a = Animal("gato")
local c = Cao("rex", "vira-lata")
local f = Filhote("bolt", "poodle")

assert(a:falar() == "gato faz um som")
assert(c:falar() == "rex late" and c.raca == "vira-lata")
assert(c:tipo() == "animal")                            -- herdado
assert(f:falar() == "bolt late" and f.raca == "poodle") -- 3 níveis

assert(classe.instancia_de(f, Animal) and classe.instancia_de(f, Cao) and classe.instancia_de(f, Filhote))
assert(not classe.instancia_de(a, Cao))
assert(not classe.instancia_de(nil, Animal) and not classe.instancia_de(5, Animal))
assert(not classe.instancia_de({}, Animal))

-- super inexistente
assert(not pcall(classe.super, Animal, "init", a))
assert(not pcall(classe.super, Cao, "naoexiste", c))

-- classe sem init
local Vazio = classe.nova()
assert(type(Vazio()) == "table")

-- operadores herdados
local P = classe.nova(nil, "P")
function P:init(x) self.x = x end
P.__add = function(x, y) return P(x.x + y.x) end
P.__eq = function(x, y) return x.x == y.x end
local Q = classe.nova(P, "Q")
assert((Q(1) + Q(2)).x == 3)
assert(Q(2) == Q(2))
assert(tostring(a) == "instancia de Animal")

-- instâncias são independentes
c.nome = "outro"
assert(Cao("x").nome == "x")
print("ok")

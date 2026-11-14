-- OOP com metatables: herança, __tostring, __eq, __add e __lt.
local M = {}

local Animal = {}
Animal.__index = Animal
function Animal.novo(nome, som)
  return setmetatable({ nome = nome, som = som or "..." }, Animal)
end
function Animal:falar() return self.nome .. " faz " .. self.som end
Animal.__tostring = function(a) return "Animal(" .. a.nome .. ")" end

local Cachorro = setmetatable({}, { __index = Animal })
Cachorro.__index = Cachorro
Cachorro.__tostring = function(c) return "Cachorro(" .. c.nome .. ")" end
function Cachorro.novo(nome)
  local c = Animal.novo(nome, "au")
  return setmetatable(c, Cachorro)
end
function Cachorro:buscar() return self.nome .. " busca a bola" end

local Vetor = {}
Vetor.__index = Vetor
Vetor.__add = function(a, b) return Vetor.novo(a.x + b.x, a.y + b.y) end
Vetor.__eq = function(a, b) return a.x == b.x and a.y == b.y end
Vetor.__lt = function(a, b) return a:norma2() < b:norma2() end
Vetor.__tostring = function(v) return "(" .. v.x .. ", " .. v.y .. ")" end
function Vetor.novo(x, y) return setmetatable({ x = x, y = y }, Vetor) end
function Vetor:norma2() return self.x * self.x + self.y * self.y end

M.Animal, M.Cachorro, M.Vetor = Animal, Cachorro, Vetor
return M

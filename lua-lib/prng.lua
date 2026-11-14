-- Gerador pseudoaleatório determinístico (LCG de 32 bits, parâmetros do Numerical Recipes).
--   x' = (1664525 * x + 1013904223) mod 2^32
-- Mesma semente => mesma sequência, em qualquer máquina. Não use para criptografia.
local Prng = {}
Prng.__index = Prng

local MASCARA = 0xFFFFFFFF

function Prng.novo(semente)
  if semente == nil then semente = os.time() end
  if math.type(semente) ~= "integer" then
    if type(semente) == "number" and semente == math.floor(semente) then
      semente = math.tointeger(semente)
    end
    if math.type(semente) ~= "integer" then error("semente deve ser inteira", 2) end
  end
  return setmetatable({ _x = semente & MASCARA }, Prng)
end

-- Próximo inteiro de 32 bits (0 .. 2^32-1).
function Prng:proximo()
  self._x = (1664525 * self._x + 1013904223) & MASCARA
  return self._x
end

-- Real em [0, 1).
function Prng:real()
  return self:proximo() / 4294967296
end

-- Inteiro em [min, max] (inclusive). Com um argumento: [1, min].
function Prng:inteiro(min, max)
  if max == nil then min, max = 1, min end
  if math.type(min) ~= "integer" or math.type(max) ~= "integer" then
    error("limites devem ser inteiros", 2)
  end
  if min > max then error("intervalo vazio", 2) end
  return min + math.floor(self:real() * (max - min + 1))
end

function Prng:booleano() return self:real() < 0.5 end

function Prng:escolher(lista)
  if #lista == 0 then return nil end
  return lista[self:inteiro(1, #lista)]
end

-- Embaralha a lista in-place (Fisher-Yates) e a devolve.
function Prng:embaralhar(lista)
  for i = #lista, 2, -1 do
    local j = self:inteiro(1, i)
    lista[i], lista[j] = lista[j], lista[i]
  end
  return lista
end

-- Estado atual (para salvar/restaurar a sequência).
function Prng:estado() return self._x end
function Prng:restaurar(x) self._x = x & MASCARA end

return Prng

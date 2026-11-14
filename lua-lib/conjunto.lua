-- Conjunto (Set) com operações de álgebra de conjuntos e operadores sobrecarregados.
local Conjunto = {}
Conjunto.__index = Conjunto

-- Marcador interno para representar nil/NaN não é suportado: erro explícito.
local function validar(v)
  if v == nil or v ~= v then error("valor invalido para conjunto (nil ou NaN)", 3) end
end

function Conjunto.novo(itens)
  local s = setmetatable({ _d = {}, _n = 0 }, Conjunto)
  for _, v in ipairs(itens or {}) do s:adicionar(v) end
  return s
end

function Conjunto:adicionar(v)
  validar(v)
  if not self._d[v] then self._d[v] = true; self._n = self._n + 1 end
  return self
end

function Conjunto:remover(v)
  if v ~= nil and self._d[v] then self._d[v] = nil; self._n = self._n - 1; return true end
  return false
end

function Conjunto:contem(v) return v ~= nil and self._d[v] == true end
function Conjunto:tamanho() return self._n end
Conjunto.__len = Conjunto.tamanho

-- Lista de elementos; ordenada quando todos são comparáveis entre si.
function Conjunto:itens()
  local r = {}
  for v in pairs(self._d) do r[#r + 1] = v end
  pcall(table.sort, r)
  return r
end

function Conjunto:uniao(o)
  local r = Conjunto.novo(self:itens())
  for v in pairs(o._d) do r:adicionar(v) end
  return r
end

function Conjunto:intersecao(o)
  local r = Conjunto.novo()
  for v in pairs(self._d) do if o._d[v] then r:adicionar(v) end end
  return r
end

function Conjunto:diferenca(o)
  local r = Conjunto.novo()
  for v in pairs(self._d) do if not o._d[v] then r:adicionar(v) end end
  return r
end

function Conjunto:diferenca_simetrica(o)
  return self:diferenca(o):uniao(o:diferenca(self))
end

function Conjunto:subconjunto_de(o)
  for v in pairs(self._d) do if not o._d[v] then return false end end
  return true
end

function Conjunto:disjunto(o) return self:intersecao(o):tamanho() == 0 end

Conjunto.__add = Conjunto.uniao
Conjunto.__mul = Conjunto.intersecao
Conjunto.__sub = Conjunto.diferenca
Conjunto.__le = Conjunto.subconjunto_de
Conjunto.__lt = function(a, b) return a._n < b._n and a:subconjunto_de(b) end
Conjunto.__eq = function(a, b) return a._n == b._n and a:subconjunto_de(b) end
Conjunto.__tostring = function(s)
  local p = {}
  for i, v in ipairs(s:itens()) do p[i] = tostring(v) end
  return "{" .. table.concat(p, ", ") .. "}"
end

return Conjunto

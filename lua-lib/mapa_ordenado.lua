-- Mapa que preserva a ordem de inserção das chaves.
local Mapa = {}
Mapa.__index = Mapa

function Mapa.novo(pares)
  local m = setmetatable({ _v = {}, _ordem = {}, _pos = {}, _n = 0 }, Mapa)
  for _, p in ipairs(pares or {}) do m:definir(p[1], p[2]) end
  return m
end

local function validar(k)
  if k == nil or k ~= k then error("chave invalida (nil ou NaN)", 3) end
end

-- Definir uma chave existente mantém a posição original.
function Mapa:definir(k, v)
  validar(k)
  if v == nil then return self:remover(k) end
  if self._pos[k] == nil then
    self._n = self._n + 1
    self._ordem[self._n] = k
    self._pos[k] = self._n
  end
  self._v[k] = v
  return self
end

function Mapa:obter(k) return self._v[k] end
function Mapa:tem(k) return k ~= nil and self._pos[k] ~= nil end
function Mapa:tamanho() return self._n end
Mapa.__len = Mapa.tamanho

function Mapa:remover(k)
  local i = k ~= nil and self._pos[k] or nil
  if not i then return self end
  table.remove(self._ordem, i)
  self._pos[k], self._v[k] = nil, nil
  self._n = self._n - 1
  for j = i, self._n do self._pos[self._ordem[j]] = j end
  return self
end

function Mapa:chaves()
  return { table.unpack(self._ordem, 1, self._n) }
end

function Mapa:valores()
  local r = {}
  for i = 1, self._n do r[i] = self._v[self._ordem[i]] end
  return r
end

-- Iterador: for k, v in mapa:pares() do ... end (tolera remoção da chave atual).
function Mapa:pares()
  local ks = self:chaves()
  local i = 0
  return function()
    while true do
      i = i + 1
      local k = ks[i]
      if k == nil then return nil end
      if self._pos[k] then return k, self._v[k] end
    end
  end
end

-- Primeira/última chave (nil se vazio).
function Mapa:primeira() return self._ordem[1] end
function Mapa:ultima() return self._ordem[self._n] end

return Mapa

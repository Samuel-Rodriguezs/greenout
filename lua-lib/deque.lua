-- Deque (fila de duas pontas) com operações O(1); serve também como fila simples.
local Deque = {}
Deque.__index = Deque

function Deque.novo()
  return setmetatable({ _d = {}, _i = 1, _f = 0 }, Deque)
end

function Deque:tamanho() return self._f - self._i + 1 end
Deque.__len = Deque.tamanho
function Deque:vazia() return self._f < self._i end

function Deque:empurrar_fim(v)
  self._f = self._f + 1
  self._d[self._f] = v
  return self
end

function Deque:empurrar_inicio(v)
  self._i = self._i - 1
  self._d[self._i] = v
  return self
end

-- Remoções retornam nil quando a deque está vazia.
function Deque:remover_inicio()
  if self:vazia() then return nil end
  local v = self._d[self._i]
  self._d[self._i] = nil
  self._i = self._i + 1
  return v
end

function Deque:remover_fim()
  if self:vazia() then return nil end
  local v = self._d[self._f]
  self._d[self._f] = nil
  self._f = self._f - 1
  return v
end

function Deque:espiar_inicio() return self._d[self._i] end
function Deque:espiar_fim() return self._d[self._f] end

-- Acesso por posição relativa (1 = início); fora do intervalo devolve nil.
function Deque:obter(n)
  if n < 1 or n > self:tamanho() then return nil end
  return self._d[self._i + n - 1]
end

-- Aliases de fila.
Deque.enfileirar = Deque.empurrar_fim
Deque.desenfileirar = Deque.remover_inicio

function Deque:itens()
  local i = self._i - 1
  return function()
    i = i + 1
    if i <= self._f then return i - self._i + 1, self._d[i] end
  end
end

function Deque:limpar()
  self._d, self._i, self._f = {}, 1, 0
end

return Deque

-- Pilha (LIFO) com capacidade opcional.
local Pilha = {}
Pilha.__index = Pilha

-- `capacidade` nil = ilimitada.
function Pilha.nova(capacidade)
  if capacidade ~= nil and (math.type(capacidade) ~= "integer" or capacidade < 1) then
    error("capacidade deve ser inteiro >= 1", 2)
  end
  return setmetatable({ _d = {}, _n = 0, _cap = capacidade }, Pilha)
end

function Pilha:tamanho() return self._n end
Pilha.__len = Pilha.tamanho
function Pilha:vazia() return self._n == 0 end
function Pilha:cheia() return self._cap ~= nil and self._n >= self._cap end

-- Retorna true; ou nil, "pilha cheia" se atingiu a capacidade.
function Pilha:empilhar(v)
  if self:cheia() then return nil, "pilha cheia" end
  self._n = self._n + 1
  self._d[self._n] = v
  return true
end

-- Retorna o valor; ou nil, "pilha vazia".
function Pilha:desempilhar()
  if self._n == 0 then return nil, "pilha vazia" end
  local v = self._d[self._n]
  self._d[self._n] = nil
  self._n = self._n - 1
  return v
end

function Pilha:topo()
  if self._n == 0 then return nil, "pilha vazia" end
  return self._d[self._n]
end

-- Lista do topo para a base (cópia).
function Pilha:para_lista()
  local r = {}
  for i = self._n, 1, -1 do r[#r + 1] = self._d[i] end
  return r
end

-- Verifica parênteses balanceados usando a pilha (exemplo de uso prático).
function Pilha.balanceado(texto)
  local pares = { [")"] = "(", ["]"] = "[", ["}"] = "{" }
  local p = Pilha.nova()
  for c in texto:gmatch(".") do
    if c == "(" or c == "[" or c == "{" then
      p:empilhar(c)
    elseif pares[c] then
      if p:desempilhar() ~= pares[c] then return false end
    end
  end
  return p:vazia()
end

return Pilha

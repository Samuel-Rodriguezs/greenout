-- Pilha (LIFO) e fila (FIFO) implementadas com tabelas.
local M = {}

local Pilha = {}
Pilha.__index = Pilha
function M.nova_pilha() return setmetatable({ itens = {}, n = 0 }, Pilha) end
function Pilha:empilhar(v) self.n = self.n + 1; self.itens[self.n] = v end
function Pilha:desempilhar()
  if self.n == 0 then return nil, "pilha vazia" end
  local v = self.itens[self.n]
  self.itens[self.n] = nil
  self.n = self.n - 1
  return v
end
function Pilha:topo() return self.itens[self.n] end
function Pilha:tamanho() return self.n end
function Pilha:vazia() return self.n == 0 end

-- Fila com dois índices (inicio/fim) para operações O(1).
local Fila = {}
Fila.__index = Fila
function M.nova_fila() return setmetatable({ itens = {}, inicio = 1, fim = 0 }, Fila) end
function Fila:enfileirar(v) self.fim = self.fim + 1; self.itens[self.fim] = v end
function Fila:desenfileirar()
  if self.inicio > self.fim then return nil, "fila vazia" end
  local v = self.itens[self.inicio]
  self.itens[self.inicio] = nil
  self.inicio = self.inicio + 1
  return v
end
function Fila:tamanho() return self.fim - self.inicio + 1 end
function Fila:vazia() return self:tamanho() == 0 end

return M

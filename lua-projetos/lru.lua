-- Cache LRU: tabela hash + lista duplamente encadeada (O(1) em tudo).
local M = {}
M.__index = M

function M.novo(capacidade)
  assert(math.type(capacidade) == "integer" and capacidade >= 1, "capacidade inválida")
  local cabeca, cauda = {}, {}
  cabeca.prox, cauda.ant = cauda, cabeca
  return setmetatable({ cap = capacidade, n = 0, mapa = {}, cabeca = cabeca, cauda = cauda }, M)
end

local function desligar(no)
  no.ant.prox, no.prox.ant = no.prox, no.ant
end

local function ligar_frente(self, no)
  local c = self.cabeca
  no.ant, no.prox = c, c.prox
  c.prox.ant = no
  c.prox = no
end

function M:obter(chave)
  local no = self.mapa[chave]
  if not no then return nil end
  desligar(no)
  ligar_frente(self, no)
  return no.valor
end

-- Consulta sem alterar a ordem de uso.
function M:espiar(chave)
  local no = self.mapa[chave]
  return no and no.valor
end

-- Insere/atualiza; devolve (chave, valor) removidos por falta de espaço, se houver.
function M:colocar(chave, valor)
  assert(chave ~= nil, "chave nula")
  local no = self.mapa[chave]
  if no then
    no.valor = valor
    desligar(no)
    ligar_frente(self, no)
    return nil
  end
  local ev_k, ev_v
  if self.n >= self.cap then
    local velho = self.cauda.ant
    desligar(velho)
    self.mapa[velho.chave] = nil
    self.n = self.n - 1
    ev_k, ev_v = velho.chave, velho.valor
  end
  no = { chave = chave, valor = valor }
  ligar_frente(self, no)
  self.mapa[chave] = no
  self.n = self.n + 1
  return ev_k, ev_v
end

function M:remover(chave)
  local no = self.mapa[chave]
  if not no then return false end
  desligar(no)
  self.mapa[chave] = nil
  self.n = self.n - 1
  return true
end

function M:tamanho() return self.n end

-- Chaves da mais recente para a menos recente.
function M:chaves()
  local r, no = {}, self.cabeca.prox
  while no ~= self.cauda do
    r[#r + 1] = no.chave
    no = no.prox
  end
  return r
end

return M

-- Trie (árvore de prefixos) com inserção, busca, remoção e autocompletar.
-- Opera sobre caracteres UTF-8.
local M = {}
M.__index = M

function M.nova()
  return setmetatable({ raiz = { filhos = {}, fim = false }, n = 0 }, M)
end

local function caracteres(s)
  local r = {}
  for _, cp in utf8.codes(s) do r[#r + 1] = utf8.char(cp) end
  return r
end

function M:inserir(palavra)
  assert(type(palavra) == "string", "palavra deve ser string")
  local no = self.raiz
  for _, c in ipairs(caracteres(palavra)) do
    no.filhos[c] = no.filhos[c] or { filhos = {}, fim = false }
    no = no.filhos[c]
  end
  if no.fim then return false end
  no.fim = true
  self.n = self.n + 1
  return true
end

local function achar(self, s)
  local no = self.raiz
  for _, c in ipairs(caracteres(s)) do
    no = no.filhos[c]
    if not no then return nil end
  end
  return no
end

function M:contem(palavra)
  local no = achar(self, palavra)
  return no ~= nil and no.fim
end

function M:tem_prefixo(prefixo)
  return achar(self, prefixo) ~= nil
end

-- Todas as palavras com o prefixo, em ordem alfabética (por bytes).
function M:autocompletar(prefixo, limite)
  local no = achar(self, prefixo)
  local r = {}
  if not no then return r end
  local function descer(n, acc)
    if limite and #r >= limite then return end
    if n.fim then r[#r + 1] = acc end
    local cs = {}
    for c in pairs(n.filhos) do cs[#cs + 1] = c end
    table.sort(cs)
    for _, c in ipairs(cs) do descer(n.filhos[c], acc .. c) end
  end
  descer(no, prefixo)
  return r
end

-- Remove a palavra e poda ramos que ficaram vazios.
function M:remover(palavra)
  local cs = caracteres(palavra)
  local caminho, no = { self.raiz }, self.raiz
  for _, c in ipairs(cs) do
    no = no.filhos[c]
    if not no then return false end
    caminho[#caminho + 1] = no
  end
  if not no.fim then return false end
  no.fim = false
  self.n = self.n - 1
  for i = #cs, 1, -1 do
    local n = caminho[i + 1]
    if n.fim or next(n.filhos) then break end
    caminho[i].filhos[cs[i]] = nil
  end
  return true
end

function M:tamanho() return self.n end

return M

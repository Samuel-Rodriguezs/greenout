-- Heap binário (fila de prioridade). Por padrão é heap de mínimo;
-- aceita função de comparação personalizada: menor(a, b) => a sai antes de b.
local M = {}
M.__index = M

function M.novo(menor)
  return setmetatable({ itens = {}, menor = menor or function(a, b) return a < b end }, M)
end

function M:tamanho() return #self.itens end
function M:vazio() return #self.itens == 0 end
function M:topo() return self.itens[1] end

function M:inserir(v)
  assert(v ~= nil, "valor nulo")
  local h = self.itens
  h[#h + 1] = v
  local i = #h
  while i > 1 do
    local p = i // 2
    if self.menor(h[i], h[p]) then
      h[i], h[p] = h[p], h[i]
      i = p
    else
      break
    end
  end
end

function M:remover()
  local h = self.itens
  local n = #h
  if n == 0 then return nil end
  local topo = h[1]
  h[1] = h[n]
  h[n] = nil
  n = n - 1
  local i = 1
  while true do
    local e, d, m = 2 * i, 2 * i + 1, i
    if e <= n and self.menor(h[e], h[m]) then m = e end
    if d <= n and self.menor(h[d], h[m]) then m = d end
    if m == i then break end
    h[i], h[m] = h[m], h[i]
    i = m
  end
  return topo
end

-- Heap sort: devolve nova lista ordenada pela mesma relação.
function M.ordenar(lista, menor)
  local h = M.novo(menor)
  for _, v in ipairs(lista) do h:inserir(v) end
  local r = {}
  while not h:vazio() do r[#r + 1] = h:remover() end
  return r
end

return M

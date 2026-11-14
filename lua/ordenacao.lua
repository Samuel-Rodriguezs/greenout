-- Algoritmos de ordenação próprios (não alteram a tabela original).
local M = {}

local function menor_padrao(a, b) return a < b end

function M.insercao(t, menor)
  menor = menor or menor_padrao
  local r = { table.unpack(t) }
  for i = 2, #r do
    local chave, j = r[i], i - 1
    while j >= 1 and menor(chave, r[j]) do r[j + 1] = r[j]; j = j - 1 end
    r[j + 1] = chave
  end
  return r
end

-- Merge sort estável.
function M.merge_sort(t, menor)
  menor = menor or menor_padrao
  if #t <= 1 then return { table.unpack(t) } end
  local meio = #t // 2
  local esq = M.merge_sort({ table.unpack(t, 1, meio) }, menor)
  local dir = M.merge_sort({ table.unpack(t, meio + 1) }, menor)
  local r, i, j = {}, 1, 1
  while i <= #esq and j <= #dir do
    if menor(dir[j], esq[i]) then r[#r + 1] = dir[j]; j = j + 1
    else r[#r + 1] = esq[i]; i = i + 1 end
  end
  while i <= #esq do r[#r + 1] = esq[i]; i = i + 1 end
  while j <= #dir do r[#r + 1] = dir[j]; j = j + 1 end
  return r
end

return M

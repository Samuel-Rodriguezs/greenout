-- Contador de palavras usando gmatch (ignora maiúsculas e pontuação).
local M = {}

-- Retorna tabela palavra -> ocorrências.
function M.contar(texto)
  local freq = {}
  for palavra in texto:lower():gmatch("[%w']+") do
    freq[palavra] = (freq[palavra] or 0) + 1
  end
  return freq
end

-- Retorna lista {palavra, n} ordenada por n desc e depois alfabética.
function M.ranking(texto)
  local lista = {}
  for p, n in pairs(M.contar(texto)) do lista[#lista + 1] = { p, n } end
  table.sort(lista, function(a, b)
    if a[2] ~= b[2] then return a[2] > b[2] end
    return a[1] < b[1]
  end)
  return lista
end

return M

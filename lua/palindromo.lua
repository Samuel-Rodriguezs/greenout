-- Verificação de palíndromos ignorando maiúsculas, espaços e pontuação (ASCII).
local M = {}

function M.normalizar(s)
  return (s:lower():gsub("[^%w]", ""))
end

function M.eh_palindromo(s)
  local t = M.normalizar(s)
  local i, j = 1, #t
  while i < j do
    if t:sub(i, i) ~= t:sub(j, j) then return false end
    i, j = i + 1, j - 1
  end
  return true
end

return M

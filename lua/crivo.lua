-- Crivo de Eratóstenes.
local M = {}

-- Retorna a lista de primos <= n.
function M.crivo(n)
  local primos = {}
  if n < 2 then return primos end
  local composto = {}
  for i = 2, n do
    if not composto[i] then
      primos[#primos + 1] = i
      for j = i * i, n, i do composto[j] = true end
    end
  end
  return primos
end

return M

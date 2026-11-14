-- Busca binária em tabela ordenada (índices a partir de 1).
local M = {}

-- Retorna o índice do alvo ou nil.
function M.buscar(t, alvo)
  local lo, hi = 1, #t
  while lo <= hi do
    local meio = (lo + hi) // 2
    if t[meio] == alvo then return meio
    elseif t[meio] < alvo then lo = meio + 1
    else hi = meio - 1 end
  end
  return nil
end

-- Primeiro índice cujo valor é >= alvo (#t + 1 se nenhum).
function M.limite_inferior(t, alvo)
  local lo, hi = 1, #t + 1
  while lo < hi do
    local meio = (lo + hi) // 2
    if t[meio] < alvo then lo = meio + 1 else hi = meio end
  end
  return lo
end

return M

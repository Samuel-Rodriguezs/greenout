-- Memoização de funções, com suporte a múltiplos argumentos, retornos nil,
-- múltiplos valores, TTL opcional e estatísticas de acertos.
local M = {}

-- opcoes.ttl = segundos de validade (usa opcoes.relogio ou os.time)
-- opcoes.chave = função(...) -> chave personalizada
function M.memoizar(fn, opcoes)
  assert(type(fn) == "function", "fn deve ser função")
  opcoes = opcoes or {}
  local relogio = opcoes.relogio or os.time
  local cache = {}
  local stats = { acertos = 0, falhas = 0 }

  local function chave(...)
    if opcoes.chave then return opcoes.chave(...) end
    local n = select("#", ...)
    local partes = { n }
    for i = 1, n do
      local v = select(i, ...)
      partes[#partes + 1] = type(v) .. ":" .. tostring(v)
    end
    return table.concat(partes, "|")
  end

  local function chamar(...)
    local k = chave(...)
    local e = cache[k]
    if e and (not opcoes.ttl or relogio() - e.t < opcoes.ttl) then
      stats.acertos = stats.acertos + 1
      return table.unpack(e.v, 1, e.v.n)
    end
    stats.falhas = stats.falhas + 1
    local v = table.pack(fn(...))
    cache[k] = { v = v, t = opcoes.ttl and relogio() or 0 }
    return table.unpack(v, 1, v.n)
  end

  local function limpar() cache = {}; stats.acertos, stats.falhas = 0, 0 end
  local function estatisticas() return stats.acertos, stats.falhas end
  return chamar, limpar, estatisticas
end

-- Fibonacci recursivo memoizado (demonstração clássica).
function M.fibonacci()
  local fib
  fib = M.memoizar(function(n)
    if n < 2 then return n end
    return fib(n - 1) + fib(n - 2)
  end)
  return fib
end

return M

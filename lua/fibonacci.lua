-- Fibonacci com memoização (cache) e versão iterativa para comparação.
local M = {}

local cache = { [0] = 0, [1] = 1 }

function M.fib(n)
  assert(math.type(n) == "integer" and n >= 0, "n deve ser inteiro não negativo")
  local v = cache[n]
  if v then return v end
  v = M.fib(n - 1) + M.fib(n - 2)
  cache[n] = v
  return v
end

function M.fib_iterativo(n)
  assert(math.type(n) == "integer" and n >= 0, "n deve ser inteiro não negativo")
  local a, b = 0, 1
  for _ = 1, n do a, b = b, a + b end
  return a
end

return M

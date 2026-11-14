-- Closures e iteradores.
local M = {}

-- Contador com estado privado.
function M.contador(inicio, passo)
  passo = passo or 1
  local n = (inicio or 0) - passo
  return function() n = n + passo; return n end
end

-- Iterador de intervalo [de, ate] com passo.
function M.intervalo(de, ate, passo)
  passo = passo or 1
  assert(passo ~= 0, "passo não pode ser zero")
  local i = de - passo
  return function()
    i = i + passo
    if (passo > 0 and i <= ate) or (passo < 0 and i >= ate) then return i end
  end
end

-- Iterador de Fibonacci infinito.
function M.fibonacci()
  local a, b = 0, 1
  return function() local r = a; a, b = b, a + b; return r end
end

-- Pega os n primeiros valores de um iterador.
function M.primeiros(iter, n)
  local r = {}
  for _ = 1, n do
    local v = iter()
    if v == nil then break end
    r[#r + 1] = v
  end
  return r
end

-- Compõe funções: compor(f, g)(x) == f(g(x)).
function M.compor(f, g) return function(...) return f(g(...)) end end

return M

local M = require("memo_fraco")

local chamadas = 0
local f, ctl = M.memoizar(function(x)
  chamadas = chamadas + 1
  if type(x) == "table" then return #x end
  return tostring(x) .. "!"
end)

-- primitivos
assert(f(1) == "1!" and f(1) == "1!" and chamadas == 1)
assert(f("a") == "a!" and chamadas == 2)
assert(f(true) == "true!" and f(true) == "true!" and chamadas == 3)

-- nil memorizado
assert(f(nil) == "nil!" and f(nil) == "nil!" and chamadas == 4)

-- NaN nunca é cacheado
local n = 0 / 0
f(n); f(n)
assert(chamadas == 6)

-- objetos: cacheados enquanto vivos
local t = { 1, 2, 3 }
assert(f(t) == 3 and f(t) == 3 and chamadas == 7)
local fracas, fortes = ctl.contar()
assert(fracas == 1 and fortes == 3 + 1)  -- 1, "a", true, nil

-- chave-objeto sem outras referências é coletada
do
  local efemero = { 1 }
  f(efemero)
  assert(select(1, ctl.contar()) == 2)
end
collectgarbage(); collectgarbage()
fracas = ctl.contar()
assert(fracas == 1)  -- só `t` sobrevive

-- múltiplos retornos
local multi = M.memoizar(function(x) return x, x * 2, nil end)
local a, b, c = multi(2)
assert(a == 2 and b == 4 and c == nil and select("#", multi(2)) == 3)

-- limpar
ctl.limpar()
local a2, b2 = ctl.contar()
assert(a2 == 0 and b2 == 0)
f(1)
assert(chamadas == 9)  -- 7 + efêmero + recálculo após limpar

-- tabela de valores fracos
local tv = M.tabela_valores_fracos()
tv.x = { "obj" }
tv.y = "string-permanece"
collectgarbage(); collectgarbage()
assert(tv.x == nil and tv.y == "string-permanece")
print("ok")

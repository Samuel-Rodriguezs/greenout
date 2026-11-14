local m = require("memoize")
local chamadas = 0
local f, limpar, stats = m.memoizar(function(a, b) chamadas = chamadas + 1; return a + (b or 0) end)
assert(f(1, 2) == 3 and f(1, 2) == 3 and chamadas == 1)
assert(f(2, 1) == 3 and chamadas == 2)
local ac, fa = stats()
assert(ac == 1 and fa == 2)
-- chaves distinguem tipos e quantidade de argumentos
assert(f(1) == 1 and chamadas == 3)
local g = m.memoizar(function(x) chamadas = chamadas + 1; return type(x) end)
assert(g(1) == "number" and g("1") == "string")
-- nil como retorno e múltiplos retornos são cacheados
local c2 = 0
local h = m.memoizar(function() c2 = c2 + 1; return nil, 2, nil end)
local a, b, c = h(); local d, e, ff = h()
assert(c2 == 1 and a == nil and b == 2 and c == nil and e == 2 and select("#", h()) == 3)
-- sem argumentos
local c3 = 0
local z = m.memoizar(function() c3 = c3 + 1 return c3 end)
assert(z() == 1 and z() == 1)
-- limpar
limpar()
f(1, 2)
assert(chamadas == 6)                -- recalculou após limpar
local ac2, fa2 = stats()
assert(ac2 == 0 and fa2 == 1)

-- TTL com relógio falso
local t = 100
local c4 = 0
local ttl = m.memoizar(function() c4 = c4 + 1; return c4 end, { ttl = 10, relogio = function() return t end })
assert(ttl() == 1); t = 109; assert(ttl() == 1)
t = 110; assert(ttl() == 2)           -- expirou
assert(ttl() == 2)

-- chave personalizada: ignora o segundo argumento
local c5 = 0
local k = m.memoizar(function(x) c5 = c5 + 1; return x end, { chave = function(x) return x end })
k(1, "a"); k(1, "b")
assert(c5 == 1)

-- erro da função não é cacheado
local tent = 0
local inst = m.memoizar(function() tent = tent + 1; if tent == 1 then error("ops") end; return "ok" end)
assert(not pcall(inst))
assert(inst() == "ok" and inst() == "ok" and tent == 2)

-- fibonacci memoizado é rápido e correto
local fib = m.fibonacci()
assert(fib(0) == 0 and fib(1) == 1 and fib(10) == 55)
assert(fib(80) == 23416728348467685)
assert(not pcall(m.memoizar, 42))
print("ok")

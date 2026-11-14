local T = require("tabelas")

-- cópia profunda
local o = { a = 1, b = { c = { 2, 3 } } }
local c = T.copia_profunda(o)
assert(c ~= o and c.b ~= o.b and c.b.c ~= o.b.c)
assert(T.igual_profundo(o, c))
c.b.c[1] = 99
assert(o.b.c[1] == 2)
assert(T.copia_profunda(5) == 5 and T.copia_profunda(nil) == nil)
-- ciclos
local ci = { nome = "x" }
ci.self = ci
local cc = T.copia_profunda(ci)
assert(cc.self == cc and cc ~= ci)
-- metatabela preservada
local mt = { __index = { z = 7 } }
assert(T.copia_profunda(setmetatable({}, mt)).z == 7)

-- mesclar
local m = T.mesclar({ a = 1, b = { x = 1, y = 2 }, l = { 1, 2, 3 } }, { b = { y = 3, z = 4 }, c = 5, l = { 9 } })
assert(m.a == 1 and m.b.x == 1 and m.b.y == 3 and m.b.z == 4 and m.c == 5)
assert(#m.l == 1 and m.l[1] == 9)
local orig = { b = { x = 1 } }
T.mesclar(orig, { b = { x = 2 } })
assert(orig.b.x == 1) -- sem mutação
assert(T.igual_profundo(T.mesclar({}, {}), {}))

-- chaves / valores
local ch = T.chaves({ b = 1, a = 2, [1] = 3, [2] = 4 })
assert(ch[1] == 1 and ch[2] == 2 and ch[3] == "a" and ch[4] == "b")
local va = T.valores({ b = "B", a = "A" })
assert(va[1] == "A" and va[2] == "B")
assert(#T.chaves({}) == 0 and T.tamanho({}) == 0 and T.tamanho({ 1, 2, x = 1 }) == 3)

-- ordenar_por (estável, sem mutar)
local gente = { { n = "a", i = 30 }, { n = "b", i = 20 }, { n = "c", i = 30 }, { n = "d", i = 10 } }
local ord = T.ordenar_por(gente, "i")
assert(ord[1].n == "d" and ord[2].n == "b" and ord[3].n == "a" and ord[4].n == "c")
local dec = T.ordenar_por(gente, "i", true)
assert(dec[1].n == "a" and dec[2].n == "c" and dec[4].n == "d")
assert(gente[1].n == "a")
assert(#T.ordenar_por({}, "i") == 0)

-- igual_profundo
assert(T.igual_profundo({ 1, { 2 } }, { 1, { 2 } }))
assert(not T.igual_profundo({ 1 }, { 1, 2 }))
assert(not T.igual_profundo({ a = 1 }, { a = 2 }))
assert(not T.igual_profundo({ a = 1 }, { b = 1 }))
assert(not T.igual_profundo({}, 1))

assert(T.inverter({ a = 1 })[1] == "a")
assert(T.contem({ 1, 2 }, 2) and not T.contem({}, 1))
print("ok")

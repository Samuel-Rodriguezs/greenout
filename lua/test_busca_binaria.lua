local b = require("busca_binaria")
local t = { 1, 3, 5, 7, 9, 11 }
for i, v in ipairs(t) do assert(b.buscar(t, v) == i) end
assert(b.buscar(t, 0) == nil and b.buscar(t, 4) == nil and b.buscar(t, 12) == nil)
assert(b.buscar({}, 1) == nil)
assert(b.buscar({ 5 }, 5) == 1 and b.buscar({ 5 }, 4) == nil)
assert(b.limite_inferior(t, 0) == 1)
assert(b.limite_inferior(t, 5) == 3)
assert(b.limite_inferior(t, 6) == 4)
assert(b.limite_inferior(t, 100) == 7)
assert(b.limite_inferior({}, 1) == 1)
assert(b.limite_inferior({ 1, 2, 2, 2, 3 }, 2) == 2)
print("ok")

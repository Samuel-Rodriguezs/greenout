local c = require("closures")
local a, b = c.contador(), c.contador(10, 5)
assert(a() == 0 and a() == 1 and a() == 2)
assert(b() == 10 and b() == 15)       -- estados independentes
assert(a() == 3)
local r = {}
for i in c.intervalo(1, 5) do r[#r + 1] = i end
assert(table.concat(r, ",") == "1,2,3,4,5")
r = {}
for i in c.intervalo(10, 0, -5) do r[#r + 1] = i end
assert(table.concat(r, ",") == "10,5,0")
for _ in c.intervalo(5, 1) do error("não deve iterar") end
assert(not pcall(c.intervalo, 1, 2, 0))
assert(table.concat(c.primeiros(c.fibonacci(), 10), ",") == "0,1,1,2,3,5,8,13,21,34")
assert(#c.primeiros(c.intervalo(1, 3), 10) == 3)
assert(#c.primeiros(c.fibonacci(), 0) == 0)
local f = c.compor(function(x) return x * 2 end, function(x) return x + 1 end)
assert(f(3) == 8)
print("ok")

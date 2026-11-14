local F = require("funcional")

local function igual(a, b)
  if #a ~= #b then return false end
  for i = 1, #a do if a[i] ~= b[i] then return false end end
  return true
end

assert(igual(F.mapear({ 1, 2, 3 }, function(x) return x * 2 end), { 2, 4, 6 }))
assert(igual(F.mapear({}, function(x) return x end), {}))
assert(igual(F.mapear({ "a", "b" }, function(_, i) return i end), { 1, 2 }))
assert(igual(F.filtrar({ 1, 2, 3, 4 }, function(x) return x % 2 == 0 end), { 2, 4 }))
assert(igual(F.filtrar({ 1, 3 }, function(x) return x % 2 == 0 end), {}))

assert(F.reduzir({ 1, 2, 3, 4 }, function(a, b) return a + b end) == 10)
assert(F.reduzir({}, function(a, b) return a + b end, 7) == 7)
assert(F.reduzir({ 5 }, function(a, b) return a + b end) == 5)
assert(not pcall(F.reduzir, {}, function(a, b) return a + b end))

local mais1 = function(x) return x + 1 end
local dobro = function(x) return x * 2 end
assert(F.compor(mais1, dobro)(5) == 11)   -- mais1(dobro(5))
assert(F.encadear(mais1, dobro)(5) == 12) -- dobro(mais1(5))
assert(F.compor()(9, 8) == 9)
local a, b = F.compor(function(x, y) return y, x end)(1, 2)
assert(a == 2 and b == 1)

local soma3 = F.curry(function(a, b, c) return a + b + c end)
assert(soma3(1)(2)(3) == 6)
assert(soma3(1, 2)(3) == 6)
assert(soma3(1)(2, 3) == 6)
assert(soma3(1, 2, 3) == 6)
local var = F.curry(function(...) return select("#", ...) end, 2)
assert(var(1)(2) == 2)

assert(F.parcial(function(a, b, c) return a .. b .. c end, "x", "y")("z") == "xyz")
assert(F.parcial(function(...) return select("#", ...) end)() == 0)

assert(igual(F.intervalo(1, 5), { 1, 2, 3, 4, 5 }))
assert(igual(F.intervalo(5, 1, -2), { 5, 3, 1 }))
assert(igual(F.intervalo(3, 1), {}))
assert(not pcall(F.intervalo, 1, 3, 0))

local z = F.zip({ 1, 2, 3 }, { "a", "b" })
assert(#z == 2 and z[2][1] == 2 and z[2][2] == "b")
assert(F.algum({ 1, 2 }, function(x) return x > 1 end) and not F.algum({}, function() return true end))
assert(F.todos({}, function() return false end) and not F.todos({ 1, 0 }, function(x) return x > 0 end))
assert(igual(F.achatar({ 1, { 2, { 3, { 4 } } }, 5 }), { 1, 2, 3, 4, 5 }))
print("ok")

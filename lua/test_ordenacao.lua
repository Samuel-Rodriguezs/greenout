local o = require("ordenacao")
local function igual(a, b)
  if #a ~= #b then return false end
  for i = 1, #a do if a[i] ~= b[i] then return false end end
  return true
end
for _, alg in ipairs({ o.insercao, o.merge_sort }) do
  assert(igual(alg({}), {}))
  assert(igual(alg({ 1 }), { 1 }))
  assert(igual(alg({ 3, 1, 2 }), { 1, 2, 3 }))
  assert(igual(alg({ 1, 2, 3 }), { 1, 2, 3 }))
  assert(igual(alg({ 3, 2, 1 }), { 1, 2, 3 }))
  assert(igual(alg({ 2, 2, 1, 1, 3 }), { 1, 1, 2, 2, 3 }))
  assert(igual(alg({ 3, 1, 2 }, function(a, b) return a > b end), { 3, 2, 1 }))
  assert(igual(alg({ "b", "a", "c" }), { "a", "b", "c" }))
  local original = { 5, 4, 3 }
  alg(original)
  assert(igual(original, { 5, 4, 3 }))
  math.randomseed(42)
  local g = {}
  for i = 1, 200 do g[i] = math.random(1, 50) end
  local esperado = { table.unpack(g) }
  table.sort(esperado)
  assert(igual(alg(g), esperado))
end
-- estabilidade do merge sort
local itens = { { k = 1, id = "a" }, { k = 0, id = "b" }, { k = 1, id = "c" }, { k = 0, id = "d" } }
local r = o.merge_sort(itens, function(a, b) return a.k < b.k end)
assert(r[1].id == "b" and r[2].id == "d" and r[3].id == "a" and r[4].id == "c")
print("ok")

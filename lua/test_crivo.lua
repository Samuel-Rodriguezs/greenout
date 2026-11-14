local c = require("crivo")
local function igual(a, b)
  if #a ~= #b then return false end
  for i = 1, #a do if a[i] ~= b[i] then return false end end
  return true
end
assert(#c.crivo(0) == 0 and #c.crivo(1) == 0 and #c.crivo(-5) == 0)
assert(igual(c.crivo(2), {2}))
assert(igual(c.crivo(30), {2,3,5,7,11,13,17,19,23,29}))
assert(igual(c.crivo(29), {2,3,5,7,11,13,17,19,23,29}))
assert(#c.crivo(100) == 25)
assert(#c.crivo(10000) == 1229)
print("ok")

local uuid = require("uuid")
local Prng = require("prng")

-- formato e bits de versão/variante
local u = uuid.gerar(1)
assert(#u == 36 and uuid.valido(u))
assert(u:sub(15, 15) == "4")
assert(("89ab"):find(u:sub(20, 20), 1, true))
assert(u:sub(9, 9) == "-" and u:sub(14, 14) == "-" and u:sub(19, 19) == "-" and u:sub(24, 24) == "-")
assert(u == u:lower())

-- determinismo por semente
assert(uuid.gerar(42) == uuid.gerar(42))
assert(uuid.gerar(42) ~= uuid.gerar(43))

-- gerador compartilhado produz sequência de UUIDs distintos
local g = Prng.novo(7)
local vistos = {}
for _ = 1, 500 do
  local x = uuid.gerar(g)
  assert(uuid.valido(x) and not vistos[x])
  vistos[x] = true
end
-- mesma sequência com mesma semente
local g1, g2 = Prng.novo(7), Prng.novo(7)
for _ = 1, 10 do assert(uuid.gerar(g1) == uuid.gerar(g2)) end

-- sem semente
assert(uuid.valido(uuid.gerar()))

-- validação
assert(not uuid.valido("") and not uuid.valido(nil) and not uuid.valido(12))
assert(not uuid.valido(uuid.NULO))                                   -- não é v4
assert(not uuid.valido("123e4567-e89b-12d3-a456-426614174000"))      -- v1
assert(not uuid.valido("123e4567-e89b-42d3-c456-426614174000"))      -- variante errada
assert(uuid.valido("123E4567-E89B-42D3-A456-426614174000"))          -- maiúsculas
assert(not uuid.valido("123e4567e89b42d3a456426614174000"))          -- sem hífens
assert(not uuid.valido("123e4567-e89b-42d3-a456-42661417400g"))
print("ok")

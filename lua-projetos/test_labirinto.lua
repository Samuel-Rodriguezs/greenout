local l = require("labirinto")
-- determinismo por seed
local a = l.gerar(8, 6, 42)
local b = l.gerar(8, 6, 42)
local c = l.gerar(8, 6, 43)
assert(l.desenhar(a) == l.desenhar(b))
assert(l.desenhar(a) ~= l.desenhar(c))

-- labirinto perfeito: passagens = células - 1 e todas alcançáveis
local function passagens(lab)
  local n = 0
  for y = 1, lab.altura do
    for x = 1, lab.largura do
      if not lab.celulas[y][x].L then n = n + 1 end
      if not lab.celulas[y][x].S then n = n + 1 end
    end
  end
  return n
end
for seed = 1, 10 do
  local lab = l.gerar(7, 5, seed)
  assert(passagens(lab) == 7 * 5 - 1)
  for y = 1, 5 do
    for x = 1, 7 do
      assert(l.resolver(lab, 1, 1, x, y), "célula inalcançável")
    end
  end
end

-- solver: caminho válido, passo a passo sem atravessar paredes
local lab = l.gerar(10, 10, 7)
local cam = l.resolver(lab)
assert(cam[1].x == 1 and cam[1].y == 1)
assert(cam[#cam].x == 10 and cam[#cam].y == 10)
local lado = { ["0,-1"] = "N", ["1,0"] = "L", ["0,1"] = "S", ["-1,0"] = "O" }
for i = 2, #cam do
  local d = lado[(cam[i].x - cam[i-1].x) .. "," .. (cam[i].y - cam[i-1].y)]
  assert(d and not lab.celulas[cam[i-1].y][cam[i-1].x][d], "passo através de parede")
end

-- bordas
local um = l.gerar(1, 1, 1)
local cm = l.resolver(um)
assert(#cm == 1)
local fino = l.gerar(5, 1, 3)
assert(#l.resolver(fino) == 5)
local r, e = l.resolver(lab, 0, 0, 1, 1)
assert(r == nil and e == "fora do labirinto")
assert(not pcall(l.gerar, 0, 5, 1))
-- origem = destino
assert(#l.resolver(lab, 3, 3, 3, 3) == 1)
-- labirinto sem caminho (todas as paredes fechadas)
local fechado = { largura = 2, altura = 1, celulas = { { { N=true,S=true,L=true,O=true }, { N=true,S=true,L=true,O=true } } } }
r, e = l.resolver(fechado)
assert(r == nil and e == "sem caminho")
-- desenho com caminho contém marcas
local d = l.desenhar(lab, cam)
local _, marcas = d:gsub("%*", "")
assert(marcas == #cam)
print("ok")

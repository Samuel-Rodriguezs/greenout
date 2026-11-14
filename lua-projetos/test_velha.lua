local v = require("velha")
local t = v.novo()
assert(#t == 9 and v.vencedor(t) == nil)
assert(#v.jogadas(t) == 9)
assert(v.jogar(t, 1, "X"))
local ok, e = v.jogar(t, 1, "O")
assert(not ok and e == "posição ocupada")
ok, e = v.jogar(t, 10, "O"); assert(not ok and e == "posição inválida")
ok, e = v.jogar(t, 0, "O"); assert(not ok)
ok, e = v.jogar(t, 1.5, "O"); assert(not ok)

-- vitórias detectadas
local g = {"X","X","X"," "," "," "," "," "," "}
assert(v.vencedor(g) == "X")
g = {"O"," "," ","O"," "," ","O"," "," "}
assert(v.vencedor(g) == "O")
g = {"X","O","X","X","O","O","O","X","X"}
assert(v.vencedor(g) == "empate")
assert(v.melhor_jogada(g, "X") == nil)

-- completa vitória imediata
g = {"X","X"," ","O","O"," "," "," "," "}
assert(v.melhor_jogada(g, "X") == 3)
-- bloqueia derrota imediata
g = {"O","O"," ","X"," "," ","X"," "," "}
assert(v.melhor_jogada(g, "X") == 3)

-- IA contra IA sempre empata
local b = v.novo()
local vez = "X"
while not v.vencedor(b) do
  local p = v.melhor_jogada(b, vez)
  assert(v.jogar(b, p, vez))
  vez = vez == "X" and "O" or "X"
end
assert(v.vencedor(b) == "empate")

-- IA (O) nunca perde, qualquer que seja a abertura de X e jogando X ingenuamente
for inicio = 1, 9 do
  local bb = v.novo()
  v.jogar(bb, inicio, "X")
  local vz = "O"
  while not v.vencedor(bb) do
    local p
    if vz == "O" then p = v.melhor_jogada(bb, "O")
    else p = v.jogadas(bb)[1] end
    v.jogar(bb, p, vz)
    vz = vz == "X" and "O" or "X"
  end
  assert(v.vencedor(bb) ~= "X")
end
print("ok")

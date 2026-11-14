-- Jogo da velha com IA minimax (com poda alfa-beta).
-- Tabuleiro: tabela de 9 posições com "X", "O" ou " ".
local M = {}

local LINHAS = {
  {1,2,3},{4,5,6},{7,8,9},{1,4,7},{2,5,8},{3,6,9},{1,5,9},{3,5,7},
}

function M.novo()
  local t = {}
  for i = 1, 9 do t[i] = " " end
  return t
end

-- Retorna "X", "O", "empate" ou nil (jogo em andamento).
function M.vencedor(t)
  for _, l in ipairs(LINHAS) do
    local a = t[l[1]]
    if a ~= " " and a == t[l[2]] and a == t[l[3]] then return a end
  end
  for i = 1, 9 do if t[i] == " " then return nil end end
  return "empate"
end

function M.jogadas(t)
  local r = {}
  for i = 1, 9 do if t[i] == " " then r[#r + 1] = i end end
  return r
end

local function outro(j) return j == "X" and "O" or "X" end

-- Pontuação do ponto de vista de `eu`: +10 vitória, -10 derrota, 0 empate.
-- A profundidade entra na conta para preferir vitórias rápidas.
local function minimax(t, vez, eu, prof, alfa, beta)
  local v = M.vencedor(t)
  if v == eu then return 10 - prof end
  if v == "empate" then return 0 end
  if v then return prof - 10 end
  local maximizando = (vez == eu)
  local melhor = maximizando and -math.huge or math.huge
  for _, p in ipairs(M.jogadas(t)) do
    t[p] = vez
    local s = minimax(t, outro(vez), eu, prof + 1, alfa, beta)
    t[p] = " "
    if maximizando then
      if s > melhor then melhor = s end
      if melhor > alfa then alfa = melhor end
    else
      if s < melhor then melhor = s end
      if melhor < beta then beta = melhor end
    end
    if beta <= alfa then break end
  end
  return melhor
end

-- Melhor jogada para `jogador`; nil se o jogo terminou.
function M.melhor_jogada(t, jogador)
  if M.vencedor(t) then return nil end
  local melhor, pos = -math.huge, nil
  for _, p in ipairs(M.jogadas(t)) do
    t[p] = jogador
    local s = minimax(t, outro(jogador), jogador, 1, -math.huge, math.huge)
    t[p] = " "
    if s > melhor then melhor, pos = s, p end
  end
  return pos
end

function M.jogar(t, pos, jogador)
  if type(pos) ~= "number" or pos < 1 or pos > 9 or pos % 1 ~= 0 then
    return nil, "posição inválida"
  end
  if t[pos] ~= " " then return nil, "posição ocupada" end
  t[pos] = jogador
  return true
end

return M

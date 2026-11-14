-- Gerador de labirinto (DFS com backtracking, seed determinística) e solver BFS.
-- O labirinto tem largura x altura células; cada célula guarda as paredes.
local M = {}

-- Gerador congruencial linear próprio: mesma seed => mesmo labirinto
-- em qualquer versão de Lua.
local function criar_rng(seed)
  local estado = (seed or 1) % 2147483647
  if estado <= 0 then estado = estado + 2147483646 end
  return function(n)
    estado = (estado * 48271) % 2147483647
    return estado % n + 1
  end
end

local DIRS = {
  { dx = 0, dy = -1, lado = "N", oposto = "S" },
  { dx = 1, dy = 0, lado = "L", oposto = "O" },
  { dx = 0, dy = 1, lado = "S", oposto = "N" },
  { dx = -1, dy = 0, lado = "O", oposto = "L" },
}

function M.gerar(largura, altura, seed)
  assert(largura >= 1 and altura >= 1, "dimensões inválidas")
  local rng = criar_rng(seed)
  local lab = { largura = largura, altura = altura, celulas = {} }
  for y = 1, altura do
    lab.celulas[y] = {}
    for x = 1, largura do
      lab.celulas[y][x] = { N = true, S = true, L = true, O = true, visitada = false }
    end
  end
  local pilha = { { 1, 1 } }
  lab.celulas[1][1].visitada = true
  while #pilha > 0 do
    local x, y = table.unpack(pilha[#pilha])
    local candidatos = {}
    for _, d in ipairs(DIRS) do
      local nx, ny = x + d.dx, y + d.dy
      if nx >= 1 and nx <= largura and ny >= 1 and ny <= altura
         and not lab.celulas[ny][nx].visitada then
        candidatos[#candidatos + 1] = { d = d, x = nx, y = ny }
      end
    end
    if #candidatos == 0 then
      pilha[#pilha] = nil
    else
      local c = candidatos[rng(#candidatos)]
      lab.celulas[y][x][c.d.lado] = false
      lab.celulas[c.y][c.x][c.d.oposto] = false
      lab.celulas[c.y][c.x].visitada = true
      pilha[#pilha + 1] = { c.x, c.y }
    end
  end
  return lab
end

-- Menor caminho de (x1,y1) a (x2,y2) por BFS; lista de {x,y} ou nil.
function M.resolver(lab, x1, y1, x2, y2)
  x1, y1 = x1 or 1, y1 or 1
  x2, y2 = x2 or lab.largura, y2 or lab.altura
  local function dentro(x, y) return x >= 1 and x <= lab.largura and y >= 1 and y <= lab.altura end
  if not dentro(x1, y1) or not dentro(x2, y2) then return nil, "fora do labirinto" end
  local chave = function(x, y) return y * (lab.largura + 1) + x end
  local pai = { [chave(x1, y1)] = false }
  local fila, ini = { { x1, y1 } }, 1
  while ini <= #fila do
    local x, y = table.unpack(fila[ini]); ini = ini + 1
    if x == x2 and y == y2 then break end
    for _, d in ipairs(DIRS) do
      if not lab.celulas[y][x][d.lado] then
        local nx, ny = x + d.dx, y + d.dy
        local k = chave(nx, ny)
        if pai[k] == nil then
          pai[k] = { x, y }
          fila[#fila + 1] = { nx, ny }
        end
      end
    end
  end
  if pai[chave(x2, y2)] == nil then return nil, "sem caminho" end
  local caminho, x, y = {}, x2, y2
  while true do
    table.insert(caminho, 1, { x = x, y = y })
    local p = pai[chave(x, y)]
    if not p then break end
    x, y = p[1], p[2]
  end
  return caminho
end

-- Desenha em ASCII; se `caminho` for dado, marca com "*".
function M.desenhar(lab, caminho)
  local marca = {}
  for _, p in ipairs(caminho or {}) do marca[p.y * (lab.largura + 1) + p.x] = true end
  local linhas = { "+" .. string.rep("---+", lab.largura) }
  for y = 1, lab.altura do
    local meio, baixo = { "|" }, { "+" }
    for x = 1, lab.largura do
      local c = lab.celulas[y][x]
      meio[#meio + 1] = marca[y * (lab.largura + 1) + x] and " * " or "   "
      meio[#meio + 1] = c.L and "|" or " "
      baixo[#baixo + 1] = c.S and "---+" or "   +"
    end
    linhas[#linhas + 1] = table.concat(meio)
    linhas[#linhas + 1] = table.concat(baixo)
  end
  return table.concat(linhas, "\n")
end

return M

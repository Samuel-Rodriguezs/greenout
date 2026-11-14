-- Jogo da Vida de Conway em grade finita (bordas mortas).
local M = {}

-- Cria grade a partir de uma lista de strings ("#" = viva, qualquer outro = morta).
function M.de_texto(linhas)
  local g = { altura = #linhas, largura = 0, c = {} }
  for _, l in ipairs(linhas) do
    if #l > g.largura then g.largura = #l end
  end
  for y, l in ipairs(linhas) do
    g.c[y] = {}
    for x = 1, g.largura do
      g.c[y][x] = l:sub(x, x) == "#"
    end
  end
  return g
end

function M.para_texto(g)
  local out = {}
  for y = 1, g.altura do
    local l = {}
    for x = 1, g.largura do l[x] = g.c[y][x] and "#" or "." end
    out[y] = table.concat(l)
  end
  return table.concat(out, "\n")
end

function M.vizinhos(g, x, y)
  local n = 0
  for dy = -1, 1 do
    for dx = -1, 1 do
      if not (dx == 0 and dy == 0) then
        local r = g.c[y + dy]
        if r and r[x + dx] then n = n + 1 end
      end
    end
  end
  return n
end

function M.passo(g)
  local novo = { altura = g.altura, largura = g.largura, c = {} }
  for y = 1, g.altura do
    novo.c[y] = {}
    for x = 1, g.largura do
      local n = M.vizinhos(g, x, y)
      if g.c[y][x] then
        novo.c[y][x] = (n == 2 or n == 3)
      else
        novo.c[y][x] = (n == 3)
      end
    end
  end
  return novo
end

function M.populacao(g)
  local n = 0
  for y = 1, g.altura do
    for x = 1, g.largura do if g.c[y][x] then n = n + 1 end end
  end
  return n
end

function M.geracoes(g, n)
  for _ = 1, n do g = M.passo(g) end
  return g
end

return M

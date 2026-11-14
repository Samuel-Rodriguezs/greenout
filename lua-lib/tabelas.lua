-- Utilitários de tabelas.
local M = {}

-- Cópia profunda preservando ciclos e metatabelas.
function M.copia_profunda(t, vistos)
  if type(t) ~= "table" then return t end
  vistos = vistos or {}
  if vistos[t] then return vistos[t] end
  local c = {}
  vistos[t] = c
  for k, v in pairs(t) do
    c[M.copia_profunda(k, vistos)] = M.copia_profunda(v, vistos)
  end
  return setmetatable(c, getmetatable(t))
end

-- Mescla profunda: devolve nova tabela; valores de `b` prevalecem sobre `a`.
-- Listas (sequências) são substituídas, não mescladas.
local function eh_lista(t)
  return type(t) == "table" and #t > 0
end

function M.mesclar(a, b)
  local r = M.copia_profunda(a)
  for k, v in pairs(b) do
    if type(v) == "table" and type(r[k]) == "table" and not eh_lista(v) and not eh_lista(r[k]) then
      r[k] = M.mesclar(r[k], v)
    else
      r[k] = M.copia_profunda(v)
    end
  end
  return r
end

-- Chaves em ordem determinística (números antes de textos).
function M.chaves(t)
  local r = {}
  for k in pairs(t) do r[#r + 1] = k end
  table.sort(r, function(x, y)
    local tx, ty = type(x), type(y)
    if tx ~= ty then return tx < ty end
    if tx == "number" or tx == "string" then return x < y end
    return tostring(x) < tostring(y)
  end)
  return r
end

function M.valores(t)
  local r = {}
  for i, k in ipairs(M.chaves(t)) do r[i] = t[k] end
  return r
end

function M.tamanho(t)
  local n = 0
  for _ in pairs(t) do n = n + 1 end
  return n
end

-- Ordena (cópia) uma lista de tabelas por `chave`; estável em empates.
function M.ordenar_por(lista, chave, decrescente)
  local idx = {}
  for i, v in ipairs(lista) do idx[i] = { v = v, i = i } end
  table.sort(idx, function(x, y)
    local a, b = x.v[chave], y.v[chave]
    if a == b then return x.i < y.i end
    if decrescente then return a > b end
    return a < b
  end)
  local r = {}
  for i, e in ipairs(idx) do r[i] = e.v end
  return r
end

function M.igual_profundo(a, b)
  if a == b then return true end
  if type(a) ~= "table" or type(b) ~= "table" then return false end
  if M.tamanho(a) ~= M.tamanho(b) then return false end
  for k, v in pairs(a) do
    if not M.igual_profundo(v, b[k]) then return false end
  end
  return true
end

function M.inverter(t)
  local r = {}
  for k, v in pairs(t) do r[v] = k end
  return r
end

function M.contem(lista, valor)
  for _, v in ipairs(lista) do if v == valor then return true end end
  return false
end

return M

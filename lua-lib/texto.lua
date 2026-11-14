-- Utilitários de strings.
local M = {}

-- Divide `s` por `sep` (texto literal, não padrão). Separador vazio divide em caracteres.
-- `max` limita o número de partes (a última guarda o resto).
function M.dividir(s, sep, max)
  local r = {}
  if sep == nil or sep == "" then
    for c in s:gmatch(utf8.charpattern) do r[#r + 1] = c end
    return r
  end
  local pos = 1
  while true do
    if max and #r == max - 1 then break end
    local i, j = s:find(sep, pos, true)
    if not i then break end
    r[#r + 1] = s:sub(pos, i - 1)
    pos = j + 1
  end
  r[#r + 1] = s:sub(pos)
  return r
end

function M.aparar(s) return (s:match("^%s*(.-)%s*$")) end
function M.aparar_esq(s) return (s:match("^%s*(.*)$")) end
function M.aparar_dir(s) return (s:match("^(.-)%s*$")) end

function M.comeca_com(s, prefixo) return s:sub(1, #prefixo) == prefixo end
function M.termina_com(s, sufixo) return sufixo == "" or s:sub(-#sufixo) == sufixo end

-- Preenche à esquerda até `n` caracteres UTF-8 usando `c` (um caractere).
function M.preencher_esq(s, n, c)
  c = c or " "
  local falta = n - utf8.len(s)
  return falta > 0 and c:rep(falta) .. s or s
end

function M.preencher_dir(s, n, c)
  c = c or " "
  local falta = n - utf8.len(s)
  return falta > 0 and s .. c:rep(falta) or s
end

function M.centralizar(s, n, c)
  c = c or " "
  local falta = n - utf8.len(s)
  if falta <= 0 then return s end
  local esq = falta // 2
  return c:rep(esq) .. s .. c:rep(falta - esq)
end

-- Substitui ${nome} (ou ${a.b}) pelos valores de `dados`; ausentes viram "".
-- Use "$${" para escapar o literal "${".
function M.modelo(s, dados)
  s = s:gsub("%$%${", "\0")
  s = s:gsub("%${([%w_%.]+)}", function(chave)
    local v = dados
    for parte in chave:gmatch("[^%.]+") do
      if type(v) ~= "table" then v = nil break end
      v = v[parte]
    end
    return v == nil and "" or tostring(v)
  end)
  return (s:gsub("\0", "${"))
end

function M.capitalizar(s)
  return (s:gsub("^%l", string.upper))
end

function M.contar(s, sub)
  if sub == "" then return 0 end
  local n, pos = 0, 1
  while true do
    local i, j = s:find(sub, pos, true)
    if not i then return n end
    n, pos = n + 1, j + 1
  end
end

function M.juntar(lista, sep)
  local t = {}
  for i, v in ipairs(lista) do t[i] = tostring(v) end
  return table.concat(t, sep or "")
end

return M

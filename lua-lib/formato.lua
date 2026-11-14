-- Formatação legível de bytes, durações e números.
local M = {}

local UNIDADES = { "B", "KB", "MB", "GB", "TB", "PB" }

-- Bytes em base 1024: 1536 -> "1.5 KB". `casas` padrão 2 (zeros finais removidos).
function M.bytes(n, casas)
  if type(n) ~= "number" or n ~= n then error("bytes: numero esperado", 2) end
  casas = casas or 2
  local sinal = n < 0 and "-" or ""
  n = math.abs(n)
  local i = 1
  while n >= 1024 and i < #UNIDADES do
    n = n / 1024
    i = i + 1
  end
  local s
  if i == 1 then
    s = string.format("%d", math.floor(n))
  else
    s = string.format("%." .. casas .. "f", n)
    if s:find("%.") then s = s:gsub("0+$", ""):gsub("%.$", "") end
  end
  return sinal .. s .. " " .. UNIDADES[i]
end

-- Segundos -> "1d 2h 3m 4s"; partes zeradas são omitidas; 0 -> "0s".
-- Frações são truncadas.
function M.duracao(segundos)
  if type(segundos) ~= "number" or segundos ~= segundos then error("duracao: numero esperado", 2) end
  if segundos < 0 then error("duracao negativa", 2) end
  local total = math.floor(segundos)
  if total == 0 then return "0s" end
  local d, resto = total // 86400, total % 86400
  local h, resto2 = resto // 3600, resto % 3600
  local m, s = resto2 // 60, resto2 % 60
  local p = {}
  if d > 0 then p[#p + 1] = d .. "d" end
  if h > 0 then p[#p + 1] = h .. "h" end
  if m > 0 then p[#p + 1] = m .. "m" end
  if s > 0 then p[#p + 1] = s .. "s" end
  return table.concat(p, " ")
end

-- Inverso de `duracao`: "1h30m", "2d 4s", "90s" -> segundos. nil, erro se inválido.
function M.analisar_duracao(texto)
  local sem = texto:gsub("%s+", "")
  if sem == "" then return nil, "duracao vazia" end
  local mult = { d = 86400, h = 3600, m = 60, s = 1 }
  local total, pos = 0, 1
  while pos <= #sem do
    local n, u, prox = sem:match("^(%d+)([dhms])()", pos)
    if not n then return nil, "duracao invalida" end
    total = total + tonumber(n) * mult[u]
    pos = prox
  end
  return total
end

-- Milhares com separador: 1234567 -> "1.234.567" (separador configurável).
function M.milhares(n, sep)
  sep = sep or "."
  local sinal, inteiro, frac = tostring(n):match("^(-?)(%d+)(%.?%d*)$")
  if not inteiro then error("milhares: numero esperado", 2) end
  inteiro = inteiro:reverse():gsub("(%d%d%d)", "%1" .. sep:gsub("%%", "%%%%")):reverse()
  if inteiro:sub(1, #sep) == sep then inteiro = inteiro:sub(#sep + 1) end
  return sinal .. inteiro .. frac
end

-- Percentual: 0.256 -> "25.6%".
function M.percentual(frac, casas)
  casas = casas or 1
  return string.format("%." .. casas .. "f%%", frac * 100)
end

return M

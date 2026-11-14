-- Formatador de tabelas em texto: colunas alinhadas, com cabeçalho e bordas.
-- Largura medida em caracteres UTF-8 (utf8.len).
local M = {}

local function largura(s) return utf8.len(s) or #s end

local function preencher(s, w, alinhamento)
  local falta = w - largura(s)
  if falta <= 0 then return s end
  if alinhamento == "direita" then return string.rep(" ", falta) .. s end
  if alinhamento == "centro" then
    local e = falta // 2
    return string.rep(" ", e) .. s .. string.rep(" ", falta - e)
  end
  return s .. string.rep(" ", falta)
end

-- opcoes.alinhar = { [coluna] = "esquerda"|"direita"|"centro" }
-- Números são alinhados à direita por padrão.
function M.formatar(cabecalho, linhas, opcoes)
  opcoes = opcoes or {}
  local alinhar = opcoes.alinhar or {}
  local ncol = #cabecalho
  for _, l in ipairs(linhas) do
    if #l > ncol then ncol = #l end
  end
  if ncol == 0 then return "" end
  local celulas = {}
  local function textos(l)
    local r = {}
    for j = 1, ncol do
      local v = l[j]
      r[j] = v == nil and "" or tostring(v)
    end
    return r
  end
  local cab = textos(cabecalho)
  local w = {}
  for j = 1, ncol do w[j] = largura(cab[j]) end
  for i, l in ipairs(linhas) do
    celulas[i] = textos(l)
    for j = 1, ncol do
      if largura(celulas[i][j]) > w[j] then w[j] = largura(celulas[i][j]) end
    end
  end
  local sep = { "+" }
  for j = 1, ncol do sep[#sep + 1] = string.rep("-", w[j] + 2) .. "+" end
  sep = table.concat(sep)

  local function linha(cel, e_cabecalho, orig)
    local partes = { "|" }
    for j = 1, ncol do
      local a = alinhar[j]
      if not a then
        a = (not e_cabecalho and type(orig[j]) == "number") and "direita" or "esquerda"
      end
      if e_cabecalho then a = alinhar[j] == "direita" and "direita" or (alinhar[j] or "esquerda") end
      partes[#partes + 1] = " " .. preencher(cel[j], w[j], a) .. " |"
    end
    return table.concat(partes)
  end

  local saida = { sep }
  if #cabecalho > 0 then
    saida[#saida + 1] = linha(cab, true, cabecalho)
    saida[#saida + 1] = sep
  end
  for i, l in ipairs(linhas) do saida[#saida + 1] = linha(celulas[i], false, l) end
  saida[#saida + 1] = sep
  return table.concat(saida, "\n")
end

return M

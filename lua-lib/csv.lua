-- Parser e gerador de CSV (RFC 4180 simplificado): aspas, "" escapado, quebras de linha em campos.
local M = {}

-- Converte texto em lista de linhas (listas de strings). Linhas totalmente vazias são ignoradas.
-- Erro (nil, mensagem) se houver aspas sem fechamento.
function M.analisar(texto, sep)
  sep = sep or ","
  if #sep ~= 1 then error("separador deve ter 1 caractere", 2) end
  local linhas, linha, campo = {}, {}, {}
  local em_aspas, inicio_campo, linha_ativa = false, true, false
  local i, n = 1, #texto

  local function fechar_campo()
    linha[#linha + 1] = table.concat(campo)
    campo, inicio_campo = {}, true
  end
  local function fechar_linha()
    if linha_ativa then
      fechar_campo()
      linhas[#linhas + 1] = linha
    end
    linha, campo, inicio_campo, linha_ativa = {}, {}, true, false
  end

  while i <= n do
    local c = texto:sub(i, i)
    if em_aspas then
      if c == '"' then
        if texto:sub(i + 1, i + 1) == '"' then
          campo[#campo + 1] = '"'
          i = i + 1
        else
          em_aspas = false
        end
      else
        campo[#campo + 1] = c
      end
    elseif c == '"' and inicio_campo then
      em_aspas, inicio_campo, linha_ativa = true, false, true
    elseif c == sep then
      linha_ativa = true
      fechar_campo()
    elseif c == "\r" or c == "\n" then
      if c == "\r" and texto:sub(i + 1, i + 1) == "\n" then i = i + 1 end
      fechar_linha()
    else
      campo[#campo + 1] = c
      inicio_campo, linha_ativa = false, true
    end
    i = i + 1
  end
  if em_aspas then return nil, "aspas sem fechamento" end
  fechar_linha()
  return linhas
end

-- Usa a primeira linha como cabeçalho; devolve lista de tabelas {coluna=valor}.
function M.com_cabecalho(texto, sep)
  local linhas, err = M.analisar(texto, sep)
  if not linhas then return nil, err end
  local cab = table.remove(linhas, 1)
  if not cab then return {} end
  local r = {}
  for li, l in ipairs(linhas) do
    local reg = {}
    for ci, nome in ipairs(cab) do reg[nome] = l[ci] end
    r[li] = reg
  end
  return r, cab
end

local function escapar(v, sep)
  v = tostring(v)
  if v:find('[' .. (sep == "%" and "%%" or sep) .. '"\r\n]') or v:find("^%s") or v:find("%s$") then
    return '"' .. v:gsub('"', '""') .. '"'
  end
  return v
end

-- Gera texto CSV (cada linha termina em "\n") a partir de lista de listas.
function M.gerar(linhas, sep)
  sep = sep or ","
  local saida = {}
  for _, l in ipairs(linhas) do
    local campos = {}
    for i, v in ipairs(l) do campos[i] = escapar(v, sep) end
    saida[#saida + 1] = table.concat(campos, sep) .. "\n"
  end
  return table.concat(saida)
end

return M

-- Tokenizer para uma linguagem tipo C simplificada.
-- Tokens: {tipo=..., valor=..., linha=n, coluna=n}
-- Tipos: palavra_chave, identificador, numero, string, operador, pontuacao.
local M = {}

local PALAVRAS = {}
for p in ("se senao enquanto para função retorne var verdadeiro falso nulo"):gmatch("%S+") do
  PALAVRAS[p] = true
end

local OPS2 = { ["=="] = true, ["!="] = true, ["<="] = true, [">="] = true,
  ["&&"] = true, ["||"] = true, ["->"] = true, ["++"] = true, ["--"] = true }
local OPS1 = "+-*/%=<>!&|^~"
local PONT = "(){}[],;:."

-- Retorna lista de tokens ou nil, mensagem (com linha:coluna).
function M.tokenizar(src)
  local toks, i, linha, col = {}, 1, 1, 1
  local n = #src
  local function avancar(k)
    for _ = 1, k do
      if src:sub(i, i) == "\n" then linha = linha + 1; col = 1 else col = col + 1 end
      i = i + 1
    end
  end
  local function emitir(tipo, valor, l, c)
    toks[#toks + 1] = { tipo = tipo, valor = valor, linha = l, coluna = c }
  end
  while i <= n do
    local c = src:sub(i, i)
    local l0, c0 = linha, col
    if c:match("%s") then
      avancar(1)
    elseif src:sub(i, i + 1) == "//" then
      local fim = src:find("\n", i, true) or n + 1
      avancar(fim - i)
    elseif src:sub(i, i + 1) == "/*" then
      local fim = src:find("*/", i + 2, true)
      if not fim then return nil, string.format("%d:%d: comentário não terminado", l0, c0) end
      avancar(fim + 2 - i)
    elseif c:match("%d") then
      local num = src:match("^%d+%.%d+", i) or src:match("^%d+", i)
      emitir("numero", tonumber(num), l0, c0)
      avancar(#num)
    elseif c:match("[%a_\128-\255]") then
      local id = src:match("^[%w_\128-\255]+", i)
      emitir(PALAVRAS[id] and "palavra_chave" or "identificador", id, l0, c0)
      avancar(#id)
    elseif c == '"' then
      local j, buf = i + 1, {}
      while true do
        local d = src:sub(j, j)
        if d == "" or d == "\n" then
          return nil, string.format("%d:%d: string não terminada", l0, c0)
        elseif d == "\\" then
          local e = src:sub(j + 1, j + 1)
          local mapa = { n = "\n", t = "\t", ['"'] = '"', ["\\"] = "\\" }
          if not mapa[e] then
            return nil, string.format("%d:%d: escape inválido '\\%s'", l0, c0, e)
          end
          buf[#buf + 1] = mapa[e]
          j = j + 2
        elseif d == '"' then
          break
        else
          buf[#buf + 1] = d
          j = j + 1
        end
      end
      emitir("string", table.concat(buf), l0, c0)
      avancar(j + 1 - i)
    elseif OPS2[src:sub(i, i + 1)] then
      emitir("operador", src:sub(i, i + 1), l0, c0)
      avancar(2)
    elseif OPS1:find(c, 1, true) then
      emitir("operador", c, l0, c0)
      avancar(1)
    elseif PONT:find(c, 1, true) then
      emitir("pontuacao", c, l0, c0)
      avancar(1)
    else
      return nil, string.format("%d:%d: caractere inesperado '%s'", l0, c0, c)
    end
  end
  return toks
end

return M

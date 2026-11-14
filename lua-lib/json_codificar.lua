-- Codificador JSON (somente encode). Chaves de objetos saem ordenadas (saída determinística).
-- Listas = tabelas sequenciais 1..n; tabela vazia vira "[]" (ou "{}" com opcoes.vazia_objeto).
local M = {}

local ESCAPES = {
  ['"'] = '\\"', ["\\"] = "\\\\", ["\b"] = "\\b", ["\f"] = "\\f",
  ["\n"] = "\\n", ["\r"] = "\\r", ["\t"] = "\\t",
}

local function escapar(s)
  return '"' .. s:gsub('[%c"\\]', function(c)
    return ESCAPES[c] or string.format("\\u%04x", c:byte())
  end) .. '"'
end

local function numero(n)
  if n ~= n or n == math.huge or n == -math.huge then
    error("numero nao representavel em JSON: " .. tostring(n), 0)
  end
  if math.type(n) == "integer" then return tostring(n) end
  for casas = 15, 17 do
    local s = string.format("%." .. casas .. "g", n)
    if tonumber(s) == n then
      if not s:find("[%.eE]") then s = s .. ".0" end
      return s
    end
  end
end

local function eh_lista(t)
  local n = 0
  for _ in pairs(t) do n = n + 1 end
  for i = 1, n do if t[i] == nil then return false end end
  return true, n
end

local function codificar(v, op, nivel, pilha)
  local tv = type(v)
  if tv == "nil" then return "null" end
  if tv == "boolean" then return tostring(v) end
  if tv == "number" then return numero(v) end
  if tv == "string" then return escapar(v) end
  if tv ~= "table" then error("tipo nao suportado em JSON: " .. tv, 0) end
  if pilha[v] then error("referencia circular", 0) end
  pilha[v] = true

  local resultado
  local lista, n = eh_lista(v)
  local indent = op.indentar
  local sep, abre_nl, fecha_nl = ",", "", ""
  if indent then
    sep = ",\n" .. indent:rep(nivel + 1)
    abre_nl = "\n" .. indent:rep(nivel + 1)
    fecha_nl = "\n" .. indent:rep(nivel)
  end
  local dois_pontos = indent and ": " or ":"

  if lista and (n > 0 or not op.vazia_objeto) then
    if n == 0 then
      resultado = "[]"
    else
      local partes = {}
      for i = 1, n do partes[i] = codificar(v[i], op, nivel + 1, pilha) end
      resultado = "[" .. abre_nl .. table.concat(partes, sep) .. fecha_nl .. "]"
    end
  else
    local chaves = {}
    for k in pairs(v) do
      if type(k) ~= "string" then error("chave de objeto deve ser string", 0) end
      chaves[#chaves + 1] = k
    end
    table.sort(chaves)
    if #chaves == 0 then
      resultado = "{}"
    else
      local partes = {}
      for i, k in ipairs(chaves) do
        partes[i] = escapar(k) .. dois_pontos .. codificar(v[k], op, nivel + 1, pilha)
      end
      resultado = "{" .. abre_nl .. table.concat(partes, sep) .. fecha_nl .. "}"
    end
  end
  pilha[v] = nil
  return resultado
end

-- opcoes: indentar = "  " (formatado), vazia_objeto = true.
-- Retorna o texto JSON, ou nil, mensagem de erro.
function M.codificar(valor, opcoes)
  local ok, r = pcall(codificar, valor, opcoes or {}, 0, {})
  if ok then return r end
  return nil, r
end

return M

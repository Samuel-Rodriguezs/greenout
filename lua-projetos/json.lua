-- Mini-JSON: codificador e decodificador.
-- Arrays Lua (chaves 1..n) viram listas JSON; demais tabelas viram objetos
-- com chaves ordenadas (saída determinística). json.nulo representa null.
local M = {}

M.nulo = setmetatable({}, { __tostring = function() return "null" end })

local ESC = { ['"'] = '\\"', ["\\"] = "\\\\", ["\b"] = "\\b", ["\f"] = "\\f",
  ["\n"] = "\\n", ["\r"] = "\\r", ["\t"] = "\\t" }

local function escapar(s)
  return '"' .. s:gsub('[%c"\\]', function(c)
    return ESC[c] or string.format("\\u%04x", c:byte())
  end) .. '"'
end

local function eh_lista(t)
  local n = 0
  for _ in pairs(t) do n = n + 1 end
  for i = 1, n do if t[i] == nil then return false end end
  return true
end

local function codificar(v, vistos)
  local tp = type(v)
  if v == M.nulo or v == nil then return "null" end
  if tp == "boolean" then return tostring(v) end
  if tp == "number" then
    if v ~= v or v == math.huge or v == -math.huge then
      error("número não representável em JSON", 0)
    end
    if v % 1 == 0 and math.abs(v) < 1e15 then return string.format("%d", v) end
    return string.format("%.14g", v)
  end
  if tp == "string" then return escapar(v) end
  if tp == "table" then
    if vistos[v] then error("referência circular", 0) end
    vistos[v] = true
    local partes = {}
    if eh_lista(v) then
      for i = 1, #v do partes[i] = codificar(v[i], vistos) end
      vistos[v] = nil
      return "[" .. table.concat(partes, ",") .. "]"
    end
    local chaves = {}
    for k in pairs(v) do
      if type(k) ~= "string" then error("chave de objeto deve ser string", 0) end
      chaves[#chaves + 1] = k
    end
    table.sort(chaves)
    for i, k in ipairs(chaves) do
      partes[i] = escapar(k) .. ":" .. codificar(v[k], vistos)
    end
    vistos[v] = nil
    return "{" .. table.concat(partes, ",") .. "}"
  end
  error("tipo não suportado: " .. tp, 0)
end

function M.codificar(v) return codificar(v, {}) end

-- Decodificação ---------------------------------------------------------
local function utf8_de(cp) return utf8.char(cp) end

function M.decodificar(s)
  local i = 1
  local function erro(msg) error(msg .. " na posição " .. i, 0) end
  local function espaco() i = s:find("[^ \t\r\n]", i) or #s + 1 end
  local valor

  local function texto()
    i = i + 1 -- aspas de abertura
    local buf = {}
    while true do
      local c = s:sub(i, i)
      if c == "" then erro("string não terminada") end
      if c == '"' then i = i + 1; break end
      if c == "\\" then
        local n = s:sub(i + 1, i + 1)
        local mapa = { b = "\b", f = "\f", n = "\n", r = "\r", t = "\t",
          ['"'] = '"', ["\\"] = "\\", ["/"] = "/" }
        if n == "u" then
          local hex = s:match("^%x%x%x%x", i + 2)
          if not hex then erro("escape unicode inválido") end
          local cp = tonumber(hex, 16)
          i = i + 6
          if cp >= 0xD800 and cp <= 0xDBFF then
            local baixo = s:match("^\\u(%x%x%x%x)", i)
            if not baixo then erro("par substituto inválido") end
            cp = 0x10000 + ((cp - 0xD800) << 10) + (tonumber(baixo, 16) - 0xDC00)
            i = i + 6
          end
          buf[#buf + 1] = utf8_de(cp)
        elseif mapa[n] then
          buf[#buf + 1] = mapa[n]
          i = i + 2
        else
          erro("escape inválido")
        end
      elseif c:byte() < 32 then
        erro("caractere de controle em string")
      else
        buf[#buf + 1] = c
        i = i + 1
      end
    end
    return table.concat(buf)
  end

  valor = function()
    espaco()
    local c = s:sub(i, i)
    if c == "{" then
      i = i + 1
      local obj = {}
      espaco()
      if s:sub(i, i) == "}" then i = i + 1; return obj end
      while true do
        espaco()
        if s:sub(i, i) ~= '"' then erro("chave esperada") end
        local k = texto()
        espaco()
        if s:sub(i, i) ~= ":" then erro("':' esperado") end
        i = i + 1
        obj[k] = valor()
        espaco()
        local d = s:sub(i, i)
        i = i + 1
        if d == "}" then return obj end
        if d ~= "," then i = i - 1; erro("',' ou '}' esperado") end
      end
    elseif c == "[" then
      i = i + 1
      local arr = {}
      espaco()
      if s:sub(i, i) == "]" then i = i + 1; return arr end
      while true do
        arr[#arr + 1] = valor()
        espaco()
        local d = s:sub(i, i)
        i = i + 1
        if d == "]" then return arr end
        if d ~= "," then i = i - 1; erro("',' ou ']' esperado") end
      end
    elseif c == '"' then
      return texto()
    elseif s:sub(i, i + 3) == "true" then i = i + 4; return true
    elseif s:sub(i, i + 4) == "false" then i = i + 5; return false
    elseif s:sub(i, i + 3) == "null" then i = i + 4; return M.nulo
    else
      local n = s:match("^-?%d+%.?%d*[eE]?[+-]?%d*", i)
      if not n or n == "" or not tonumber(n) then erro("valor inesperado") end
      i = i + #n
      return math.tointeger(tonumber(n)) or tonumber(n)
    end
  end

  local r = valor()
  espaco()
  if i <= #s then erro("conteúdo extra") end
  return r
end

function M.tentar(s)
  local ok, r = pcall(M.decodificar, s)
  if ok then return r end
  return nil, r
end

return M

-- Parser e avaliador de expressões aritméticas (descida recursiva).
-- Suporta + - * / % ^, parênteses, menos unário, decimais, variáveis e funções.
local M = {}

local FUNCOES = {
  sqrt = math.sqrt, abs = math.abs, max = math.max, min = math.min,
  floor = math.floor, ceil = math.ceil,
}

local function tokenizar(s)
  local toks, i = {}, 1
  while i <= #s do
    local c = s:sub(i, i)
    if c:match("%s") then
      i = i + 1
    elseif c:match("%d") or (c == "." and s:sub(i + 1, i + 1):match("%d")) then
      local n = s:match("^%d*%.?%d+", i) or s:match("^%d+", i)
      toks[#toks + 1] = { t = "num", v = tonumber(n) }
      i = i + #n
    elseif c:match("[%a_]") then
      local id = s:match("^[%a_][%w_]*", i)
      toks[#toks + 1] = { t = "id", v = id }
      i = i + #id
    elseif c:match("[%+%-%*/%%%^%(%),]") then
      toks[#toks + 1] = { t = c }
      i = i + 1
    else
      error("caractere inesperado '" .. c .. "'", 0)
    end
  end
  toks[#toks + 1] = { t = "fim" }
  return toks
end

-- Constrói a AST. Nós: {tipo="num",v}, {tipo="var",nome}, {tipo="bin",op,a,b},
-- {tipo="neg",a}, {tipo="chamada",nome,args}
function M.parse(s)
  local toks, pos = tokenizar(s), 1
  local function atual() return toks[pos] end
  local function consome(t)
    local k = toks[pos]
    if t and k.t ~= t then error("esperado '" .. t .. "' mas veio '" .. k.t .. "'", 0) end
    pos = pos + 1
    return k
  end
  local expr

  local function primario()
    local k = atual()
    if k.t == "num" then
      consome()
      return { tipo = "num", v = k.v }
    elseif k.t == "id" then
      consome()
      if atual().t == "(" then
        consome("(")
        local args = {}
        if atual().t ~= ")" then
          repeat
            args[#args + 1] = expr()
            local mais = atual().t == ","
            if mais then consome(",") end
          until not mais
        end
        consome(")")
        return { tipo = "chamada", nome = k.v, args = args }
      end
      return { tipo = "var", nome = k.v }
    elseif k.t == "(" then
      consome("(")
      local e = expr()
      consome(")")
      return e
    end
    error("expressão inesperada em '" .. k.t .. "'", 0)
  end

  local unario
  -- potência: associativa à direita e com precedência maior que o menos unário
  local function potencia()
    local base = primario()
    if atual().t == "^" then
      consome()
      return { tipo = "bin", op = "^", a = base, b = unario() }
    end
    return base
  end
  unario = function()
    if atual().t == "-" then
      consome()
      return { tipo = "neg", a = unario() }
    elseif atual().t == "+" then
      consome()
      return unario()
    end
    return potencia()
  end
  local function termo()
    local e = unario()
    while atual().t == "*" or atual().t == "/" or atual().t == "%" do
      local op = consome().t
      e = { tipo = "bin", op = op, a = e, b = unario() }
    end
    return e
  end
  expr = function()
    local e = termo()
    while atual().t == "+" or atual().t == "-" do
      local op = consome().t
      e = { tipo = "bin", op = op, a = e, b = termo() }
    end
    return e
  end

  local arvore = expr()
  if atual().t ~= "fim" then
    error("sobrou entrada após a expressão: '" .. atual().t .. "'", 0)
  end
  return arvore
end

local function aval(n, vars)
  if n.tipo == "num" then return n.v end
  if n.tipo == "var" then
    local v = vars[n.nome]
    if v == nil then error("variável indefinida: " .. n.nome, 0) end
    return v
  end
  if n.tipo == "neg" then return -aval(n.a, vars) end
  if n.tipo == "chamada" then
    local f = FUNCOES[n.nome]
    if not f then error("função desconhecida: " .. n.nome, 0) end
    local args = {}
    for i, a in ipairs(n.args) do args[i] = aval(a, vars) end
    return f(table.unpack(args))
  end
  local a, b = aval(n.a, vars), aval(n.b, vars)
  if n.op == "+" then return a + b
  elseif n.op == "-" then return a - b
  elseif n.op == "*" then return a * b
  elseif n.op == "/" then
    if b == 0 then error("divisão por zero", 0) end
    return a / b
  elseif n.op == "%" then
    if b == 0 then error("divisão por zero", 0) end
    return a % b
  else return a ^ b end
end

-- Avalia; levanta erro (string) em caso de problema.
function M.avaliar(s, vars)
  return aval(M.parse(s), vars or {})
end

-- Versão segura: retorna valor ou nil, mensagem.
function M.tentar(s, vars)
  local ok, r = pcall(M.avaliar, s, vars)
  if ok then return r end
  return nil, r
end

return M

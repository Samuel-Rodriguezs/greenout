-- Memoização com tabelas fracas: o cache não impede a coleta das chaves-objeto.
-- Funções de um argumento. Chaves-objeto (tabelas, funções, userdata) vivem em cache de
-- chaves fracas; chaves primitivas (números, strings, booleanos) em cache comum.
-- Resultados nil são memorizados; NaN não é cacheado (não pode ser chave).
local M = {}

local NIL = {}  -- marcador para a chave nil

local function eh_objeto(k)
  local t = type(k)
  return t == "table" or t == "function" or t == "userdata" or t == "thread"
end

-- Retorna a função memorizada e um objeto de controle { limpar(), contar() }.
function M.memoizar(f)
  local fraco = setmetatable({}, { __mode = "k" })
  local forte = {}

  local function memorizada(arg)
    if arg ~= arg then return f(arg) end  -- NaN
    local chave = arg == nil and NIL or arg
    local cache = eh_objeto(arg) and fraco or forte
    local e = cache[chave]
    if e == nil then
      e = table.pack(f(arg))
      cache[chave] = e
    end
    return table.unpack(e, 1, e.n)
  end

  local controle = {}
  function controle.limpar()
    for k in pairs(fraco) do fraco[k] = nil end
    for k in pairs(forte) do forte[k] = nil end
  end
  -- Retorna (entradas fracas, entradas fortes).
  function controle.contar()
    local a, b = 0, 0
    for _ in pairs(fraco) do a = a + 1 end
    for _ in pairs(forte) do b = b + 1 end
    return a, b
  end
  return memorizada, controle
end

-- Tabela fraca de valores: útil para caches de objetos reaproveitáveis (ex.: internação).
function M.tabela_valores_fracos()
  return setmetatable({}, { __mode = "v" })
end

return M

local Logger = require("logger")

local linhas = {}
local function saida(l) linhas[#linhas + 1] = l end

-- nível padrão info: debug suprimido
local l = Logger.novo { saida = saida }
assert(l:debug("x") == false and #linhas == 0)
assert(l:info("ola") == true and linhas[1] == "[INFO] ola")
l:aviso("a")
l:erro("e")
assert(linhas[2] == "[AVISO] a" and linhas[3] == "[ERRO] e")

-- formatação
linhas = {}
l:info("%s tem %d anos", "Ana", 30)
assert(linhas[1] == "[INFO] Ana tem 30 anos")
l:info("100%")                                  -- sem args: não interpreta %
assert(linhas[2] == "[INFO] 100%")
l:info(42)
assert(linhas[3] == "[INFO] 42")

-- níveis
linhas = {}
l:definir_nivel("debug")
l:debug("d")
assert(linhas[1] == "[DEBUG] d" and l:habilitado("debug"))
l:definir_nivel("erro")
assert(not l:habilitado("aviso") and l:habilitado("erro"))
assert(l:aviso("x") == false and l:erro("y") == true and #linhas == 2)
l:definir_nivel("nenhum")
assert(l:erro("z") == false and #linhas == 2)
assert(not pcall(l.definir_nivel, l, "xyz"))
assert(not pcall(Logger.novo, { nivel = "xyz" }))

-- relógio e prefixo injetados
linhas = {}
local t = 0
local c = Logger.novo { saida = saida, relogio = function() t = t + 1; return "T" .. t end, prefixo = "app" }
c:info("a"); c:info("b")
assert(linhas[1] == "T1 [INFO] app: a" and linhas[2] == "T2 [INFO] app: b")

-- filhos acumulam prefixo e herdam saída
linhas = {}
local f = Logger.novo { saida = saida }:filho("db"):filho("pool")
f:erro("caiu")
assert(linhas[1] == "[ERRO] db.pool: caiu")

-- saída como objeto com :write
local buf = {}
local alvo = { write = function(_, ...) buf[#buf + 1] = table.concat { ... } end }
Logger.novo { saida = alvo }:info("via objeto")
assert(buf[1] == "[INFO] via objeto\n")
print("ok")

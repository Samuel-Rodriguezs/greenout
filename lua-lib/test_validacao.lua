local V = require("validacao")

local function ok(v, e) local r = V.validar(v, e); return r end
local function erros(v, e) local _, errs = V.validar(v, e); return errs end

-- tipos básicos
assert(ok("x", { tipo = "string" }) and not ok(1, { tipo = "string" }))
assert(ok(1.5, { tipo = "numero" }) and not ok("1", { tipo = "numero" }))
assert(not ok(0 / 0, { tipo = "numero" }))
assert(ok(3, { tipo = "inteiro" }) and not ok(3.5, { tipo = "inteiro" }))
assert(ok(false, { tipo = "booleano" }) and ok({}, { tipo = "tabela" }) and ok(print, { tipo = "funcao" }))
assert(ok(nil, { tipo = "string" }))                     -- opcional por padrão
assert(not ok(nil, { tipo = "string", obrigatorio = true }))
assert(ok(5, {}) and ok("x", { tipo = "qualquer" }))

-- limites
assert(ok(5, { tipo = "numero", min = 1, max = 5 }))
assert(not ok(0, { tipo = "numero", min = 1 }) and not ok(6, { tipo = "numero", max = 5 }))
assert(ok("abc", { tipo = "string", min = 3, max = 3 }))
assert(not ok("", { tipo = "string", min = 1 }) and not ok("abcd", { tipo = "string", max = 3 }))
assert(not ok({ 1, 2, 3 }, { tipo = "lista", max = 2 }))
assert(erros("", { tipo = "string", min = 1 })[1] == "$: tamanho menor que o minimo 1")

-- padrão e enum
assert(ok("abc123", { tipo = "string", padrao = "^%a+%d+$" }) and not ok("123", { tipo = "string", padrao = "^%a+$" }))
assert(ok("b", { enum = { "a", "b" } }) and not ok("c", { enum = { "a", "b" } }))

-- validador personalizado
local par = { tipo = "inteiro", validador = function(n) return n % 2 == 0, "deve ser par" end }
assert(ok(4, par))
assert(erros(3, par)[1] == "$: deve ser par")

-- listas
local lst = { tipo = "lista", itens = { tipo = "inteiro", min = 0 } }
assert(ok({}, lst) and ok({ 1, 2 }, lst))
local e = erros({ 1, -1, "x" }, lst)
assert(#e == 2 and e[1]:find("%$%[2%]") and e[2]:find("%$%[3%]"))
assert(not ok({ a = 1 }, { tipo = "lista" }))

-- objetos aninhados com múltiplos erros em ordem determinística
local usuario = {
  tipo = "tabela",
  campos = {
    nome = { tipo = "string", obrigatorio = true, min = 2 },
    idade = { tipo = "inteiro", min = 0, max = 150 },
    endereco = { tipo = "tabela", campos = { cep = { tipo = "string", padrao = "^%d%d%d%d%d%-?%d%d%d$" } } },
  },
}
assert(ok({ nome = "Ana", idade = 30, endereco = { cep = "01001-000" } }, usuario))
local r, errs = V.validar({ nome = "A", idade = 200, endereco = { cep = "x" } }, usuario)
assert(r == false and #errs == 3)
assert(errs[1]:find("^%$%.endereco%.cep") and errs[2]:find("^%$%.idade") and errs[3]:find("^%$%.nome"))
assert(erros({}, usuario)[1] == "$.nome: campo obrigatorio")
assert(erros("x", usuario)[1] == "$: esperado tabela, recebido string")

-- estrito
local est = { tipo = "tabela", estrito = true, campos = { a = { tipo = "numero" } } }
assert(ok({ a = 1 }, est))
assert(erros({ a = 1, b = 2 }, est)[1] == "$: campo nao permitido 'b'")

-- esquema inválido
assert(not pcall(V.validar, 1, { tipo = "xyz" }))
print("ok")

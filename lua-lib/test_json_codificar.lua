local J = require("json_codificar")
local enc = J.codificar

-- escalares
assert(enc(nil) == "null" and enc(true) == "true" and enc(false) == "false")
assert(enc(0) == "0" and enc(-42) == "-42" and enc(1.5) == "1.5" and enc(-0.25) == "-0.25")
assert(enc(3.0) == "3.0" and enc(1e100) == "1e+100")
assert(enc(0.1) == "0.1" and tonumber(enc(1 / 3)) == 1 / 3)
assert(enc(math.maxinteger) == "9223372036854775807")

-- strings e escapes
assert(enc("") == '""' and enc("oi") == '"oi"')
assert(enc('a"b\\c') == '"a\\"b\\\\c"')
assert(enc("l1\nl2\t\r") == '"l1\\nl2\\t\\r"')
assert(enc("\0\1\31") == '"\\u0000\\u0001\\u001f"')
assert(enc("ação ✓") == '"ação ✓"')              -- UTF-8 preservado

-- listas e objetos
assert(enc({}) == "[]")
assert(enc({}, { vazia_objeto = true }) == "{}")
assert(enc({ 1, 2, 3 }) == "[1,2,3]")
assert(enc({ "a", { true, false } }) == '["a",[true,false]]')
assert(enc({ b = 1, a = 2 }) == '{"a":2,"b":1}')                  -- chaves ordenadas
assert(enc({ lista = { 1 }, obj = { x = "y" } }) == '{"lista":[1],"obj":{"x":"y"}}')
assert(enc({ ['a"b'] = 1 }) == '{"a\\"b":1}')

-- tabela com buracos ou misto vira objeto/erro
local r, e = enc({ 1, 2, x = 3 })
assert(r == nil and e:find("chave de objeto"))
r, e = enc({ [1] = "a", [3] = "c" })
assert(r == nil and e:find("chave de objeto"))

-- formatado
assert(enc({ a = 1, b = { 2, 3 } }, { indentar = "  " }) == '{\n  "a": 1,\n  "b": [\n    2,\n    3\n  ]\n}')
assert(enc({}, { indentar = "  " }) == "[]")
assert(enc({ a = {} }, { indentar = "\t" }) == '{\n\t"a": []\n}')

-- erros
r, e = enc(0 / 0)
assert(r == nil and e:find("nao representavel"))
assert(enc(math.huge) == nil and enc(-math.huge) == nil)
r, e = enc(print)
assert(r == nil and e:find("tipo nao suportado"))
r, e = enc({ f = print })
assert(r == nil)
local ciclo = {}
ciclo.self = ciclo
r, e = enc(ciclo)
assert(r == nil and e == "referencia circular")

-- mesma tabela referenciada duas vezes (sem ciclo) é permitida
local comp = { 1 }
assert(enc({ comp, comp }) == "[[1],[1]]")

-- profundidade
local fundo = {}
local cur = fundo
for _ = 1, 100 do cur[1] = {}; cur = cur[1] end
assert(#enc(fundo) == 2 + 2 * 100)
print("ok")

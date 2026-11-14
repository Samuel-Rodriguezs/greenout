local j = require("json")
-- codificação
assert(j.codificar(1) == "1")
assert(j.codificar(1.5) == "1.5")
assert(j.codificar(true) == "true")
assert(j.codificar(j.nulo) == "null")
assert(j.codificar("oi") == '"oi"')
assert(j.codificar('a"b\\c\n') == '"a\\"b\\\\c\\n"')
assert(j.codificar("\1") == '"\\u0001"')
assert(j.codificar({}) == "[]")
assert(j.codificar({ 1, 2, 3 }) == "[1,2,3]")
assert(j.codificar({ b = 1, a = { 1, "x" } }) == '{"a":[1,"x"],"b":1}')
local ok, e = pcall(j.codificar, 0/0); assert(not ok and e:find("não representável"))
local c = {}; c.self = c
ok, e = pcall(j.codificar, c); assert(not ok and e == "referência circular")
ok, e = pcall(j.codificar, { [1] = "a", [3] = "c" }); assert(not ok and e:find("string"))
ok, e = pcall(j.codificar, print); assert(not ok and e:find("não suportado"))

-- decodificação
assert(j.decodificar("42") == 42)
assert(j.decodificar("-3.5") == -3.5)
assert(j.decodificar("1e3") == 1000)
assert(j.decodificar(" true ") == true)
assert(j.decodificar("false") == false)
assert(j.decodificar("null") == j.nulo)
assert(j.decodificar('"a\\nb"') == "a\nb")
assert(j.decodificar('"\\u00e9"') == "é")
assert(j.decodificar('"\\ud83d\\ude00"') == "😀")
local t = j.decodificar('{"a":[1,2,{"b":null}],"c":"x"}')
assert(t.a[2] == 2 and t.a[3].b == j.nulo and t.c == "x")
assert(#j.decodificar("[ ]") == 0)
assert(next(j.decodificar("{ }")) == nil)

-- ida e volta
local orig = { nome = "Ana", idade = 30, tags = { "a", "b" }, ativo = true, aninhado = { x = 1.25 } }
local volta = j.decodificar(j.codificar(orig))
assert(volta.nome == "Ana" and volta.idade == 30 and volta.tags[2] == "b")
assert(volta.ativo == true and volta.aninhado.x == 1.25)
assert(j.codificar(volta) == j.codificar(orig))

-- erros
for _, ruim in ipairs({ "", "{", "[1,", '{"a"}', '{"a":1,}', "[1 2]", '"abc', "tru", "1 2", '"\\x"', "{1:2}" }) do
  local v, m = j.tentar(ruim)
  assert(v == nil and m, "deveria falhar: " .. ruim)
end
print("ok")

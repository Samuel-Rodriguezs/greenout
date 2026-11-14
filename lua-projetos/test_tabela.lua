local t = require("tabela")
local r = t.formatar({ "Nome", "Idade" }, { { "Ana", 30 }, { "Bartolomeu", 5 } })
local esperado = table.concat({
  "+------------+-------+",
  "| Nome       | Idade |",
  "+------------+-------+",
  "| Ana        |    30 |",
  "| Bartolomeu |     5 |",
  "+------------+-------+",
}, "\n")
assert(r == esperado, r)

-- UTF-8: largura por caractere, não por byte
local u = t.formatar({ "Cidade" }, { { "São Paulo" }, { "Açu" } })
local ls = {}
for l in u:gmatch("[^\n]+") do ls[#ls + 1] = utf8.len(l) end
for i = 2, #ls do assert(ls[i] == ls[1]) end

-- alinhamentos explícitos
local c = t.formatar({ "A", "B" }, { { "x", "y" } }, { alinhar = { "centro", "direita" } })
assert(c:find("| A | B |", 1, true) and c:find("| x | y |", 1, true))
local c2 = t.formatar({ "Titulo" }, { { "ab" } }, { alinhar = { "centro" } })
assert(c2:find("| Titulo |", 1, true) and c2:find("|   ab   |", 1, true))
local d = t.formatar({ "Titulo" }, { { "ab" } }, { alinhar = { "direita" } })
assert(d:find("|     ab |", 1, true))

-- bordas: sem linhas, linhas curtas, sem cabeçalho, vazio
local sl = t.formatar({ "X", "Y" }, {})
assert(sl == "+---+---+\n| X | Y |\n+---+---+\n+---+---+")
local curta = t.formatar({ "A", "B", "C" }, { { 1 } })
assert(curta:find("|   1 |   |   |", 1, true) or curta:find("| 1 |   |   |", 1, true))
local sc = t.formatar({}, { { "a", "b" } })
assert(sc == "+---+---+\n| a | b |\n+---+---+")
assert(t.formatar({}, {}) == "")
-- mais colunas na linha que no cabeçalho
local mais = t.formatar({ "A" }, { { 1, 2 } })
assert(mais:find("| A |   |", 1, true))
-- valores booleanos e decimais viram texto
assert(t.formatar({ "v" }, { { true }, { 1.5 } }):find("true", 1, true))
print("ok")

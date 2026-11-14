local csv = require("csv")

local function plano(linhas)
  local t = {}
  for i, l in ipairs(linhas) do t[i] = table.concat(l, "|") end
  return table.concat(t, ";")
end

assert(plano(csv.analisar("a,b,c\n1,2,3\n")) == "a|b|c;1|2|3")
assert(plano(csv.analisar("a,b\n1,2")) == "a|b;1|2")              -- sem \n final
assert(plano(csv.analisar("a,b\r\n1,2\r\n")) == "a|b;1|2")         -- CRLF
assert(#csv.analisar("") == 0 and #csv.analisar("\n\n") == 0)      -- vazio
assert(plano(csv.analisar("a\n\nb\n")) == "a;b")                   -- linhas em branco ignoradas

-- campos vazios
local l = csv.analisar(",,\n")[1]
assert(#l == 3 and l[1] == "" and l[3] == "")
l = csv.analisar("a,\n")[1]
assert(#l == 2 and l[2] == "")

-- aspas
assert(csv.analisar('"a,b",c\n')[1][1] == "a,b")
assert(csv.analisar('"diz ""oi""",x\n')[1][1] == 'diz "oi"')
assert(csv.analisar('"linha1\nlinha2",x\n')[1][1] == "linha1\nlinha2")
assert(#csv.analisar('"linha1\nlinha2",x\n') == 1)
assert(csv.analisar('""\n')[1][1] == "")
assert(csv.analisar('a"b,c\n')[1][1] == 'a"b')                      -- aspas no meio são literais
local r, e = csv.analisar('"aberta,x')
assert(r == nil and e == "aspas sem fechamento")

-- separador customizado
assert(plano(csv.analisar("a;b;c\n1;2;3", ";")) == "a|b|c;1|2|3")
assert(csv.analisar("a\tb", "\t")[1][2] == "b")
assert(not pcall(csv.analisar, "a", ",,"))

-- cabeçalho
local regs, cab = csv.com_cabecalho("nome,idade\nAna,30\nBia,25\n")
assert(#regs == 2 and regs[1].nome == "Ana" and regs[2].idade == "25" and #cab == 2)
assert(#csv.com_cabecalho("") == 0)
assert(csv.com_cabecalho("a,b\n1\n")[1].b == nil)

-- geração e ida-e-volta
local dados = { { "a", "b,c", 'd"e' }, { "x\ny", "", " z" }, { 1, 2.5, true } }
local texto = csv.gerar(dados)
assert(texto:sub(1, 15) == 'a,"b,c","d""e"\n')
local volta = csv.analisar(texto)
assert(#volta == 3 and volta[1][2] == "b,c" and volta[1][3] == 'd"e')
assert(volta[2][1] == "x\ny" and volta[2][2] == "" and volta[2][3] == " z")
assert(volta[3][1] == "1" and volta[3][3] == "true")
assert(csv.gerar({}) == "")
assert(csv.gerar({ { "a;b" } }, ";") == '"a;b"\n')
print("ok")

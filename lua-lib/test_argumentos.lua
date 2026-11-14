local A = require("argumentos")

local ops = {
  verboso = { tipo = "booleano", curto = "v" },
  forcar = { tipo = "booleano", curto = "f" },
  saida = { tipo = "texto", curto = "o", padrao = "a.out" },
  nivel = { tipo = "numero", curto = "n", padrao = 1 },
  incluir = { tipo = "texto", curto = "i", repetivel = true },
}

local r = A.analisar({}, ops)
assert(r.opcoes.saida == "a.out" and r.opcoes.nivel == 1 and r.opcoes.verboso == nil and #r.posicionais == 0)

r = A.analisar({ "--verboso", "--saida=x.bin", "arq1", "--nivel", "3", "arq2" }, ops)
assert(r.opcoes.verboso == true and r.opcoes.saida == "x.bin" and r.opcoes.nivel == 3)
assert(#r.posicionais == 2 and r.posicionais[1] == "arq1" and r.posicionais[2] == "arq2")

-- curtas, agrupadas e com valor colado
r = A.analisar({ "-vf", "-o", "y", "-n5" }, ops)
assert(r.opcoes.verboso and r.opcoes.forcar and r.opcoes.saida == "y" and r.opcoes.nivel == 5)
r = A.analisar({ "-vo", "z" }, ops)
assert(r.opcoes.verboso and r.opcoes.saida == "z")
r = A.analisar({ "-ofoo" }, ops)
assert(r.opcoes.saida == "foo")

-- repetíveis
r = A.analisar({ "-i", "a", "--incluir=b", "--incluir", "c" }, ops)
assert(#r.opcoes.incluir == 3 and r.opcoes.incluir[1] == "a" and r.opcoes.incluir[3] == "c")

-- "--" encerra opções; "-" e números negativos são posicionais
r = A.analisar({ "--", "--verboso", "-x" }, ops)
assert(r.opcoes.verboso == nil and #r.posicionais == 2 and r.posicionais[1] == "--verboso")
r = A.analisar({ "-", "-5", "x" }, ops)
assert(#r.posicionais == 3 and r.posicionais[1] == "-" and r.posicionais[2] == "-5")

-- booleano com valor explícito
r = A.analisar({ "--verboso=false" }, ops)
assert(r.opcoes.verboso == false)

-- valor com "=" dentro
r = A.analisar({ "--saida=a=b" }, ops)
assert(r.opcoes.saida == "a=b")

-- erros
local function erro(args) local res, e = A.analisar(args, ops); assert(res == nil); return e end
assert(erro({ "--nada" }) == "opcao desconhecida: --nada")
assert(erro({ "-z" }) == "opcao desconhecida: -z")
assert(erro({ "--saida" }) == "opcao --saida requer um valor")
assert(erro({ "-o" }) == "opcao -o requer um valor")
assert(erro({ "--nivel", "abc" }) == "valor invalido para --nivel: abc")
assert(erro({ "--verboso=talvez" }):find("valor invalido"))

-- ajuda
local h = A.ajuda({ b = { tipo = "texto", curto = "b", descricao = "um texto" }, a = { tipo = "booleano" } })
assert(h == "      --a\n  -b, --b <texto>  um texto")
print("ok")

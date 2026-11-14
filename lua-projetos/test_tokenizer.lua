local tk = require("tokenizer")
local function resumo(src)
  local t, e = tk.tokenizar(src)
  assert(t, e)
  local r = {}
  for i, x in ipairs(t) do r[i] = x.tipo:sub(1, 1) .. ":" .. tostring(x.valor) end
  return table.concat(r, " ")
end
assert(resumo("") == "")
assert(resumo("   \n\t ") == "")
assert(resumo("var x = 10;") == "p:var i:x o:= n:10 p:;")
assert(resumo("a<=b && c!=d") == "i:a o:<= i:b o:&& i:c o:!= i:d")
assert(resumo("x = 3.14") == "i:x o:= n:3.14")
assert(resumo("f(a, b)") == "i:f p:( i:a p:, i:b p:)")
assert(resumo('s = "olá\\n\\"mundo\\""') == 'i:s o:= s:olá\n"mundo"')
assert(resumo('"a\\tb"') == "s:a\tb")
assert(resumo("1 // comentário\n2") == "n:1 n:2")
assert(resumo("1 /* multi\nlinha */ 2") == "n:1 n:2")
assert(resumo("variável_1 ação") == "i:variável_1 i:ação")
assert(resumo("i++ ; i--") == "i:i o:++ p:; i:i o:--")

-- tipos e posições
local t = tk.tokenizar("se x\n  retorne 7")
assert(t[1].tipo == "palavra_chave" and t[1].linha == 1 and t[1].coluna == 1)
assert(t[2].tipo == "identificador" and t[2].coluna == 4)
assert(t[3].tipo == "palavra_chave" and t[3].linha == 2 and t[3].coluna == 3)
assert(t[4].tipo == "numero" and t[4].valor == 7 and t[4].coluna == 11)
assert(tk.tokenizar("x")[1].tipo == "identificador")
assert(tk.tokenizar("a.b")[2].tipo == "pontuacao")

-- erros com posição
local r, e = tk.tokenizar("x = @")
assert(r == nil and e == "1:5: caractere inesperado '@'")
r, e = tk.tokenizar('a\n"abc')
assert(r == nil and e == "2:1: string não terminada")
r, e = tk.tokenizar('"abc\ndef"'); assert(r == nil and e:find("string não terminada"))
r, e = tk.tokenizar('"a\\qb"'); assert(r == nil and e:find("escape inválido"))
r, e = tk.tokenizar("1 /* aberto"); assert(r == nil and e == "1:3: comentário não terminado")
print("ok")

local esc = require("escalonador")
local s = esc.novo()
local saida = {}
s:criar("A", function()
  saida[#saida + 1] = "A1"
  esc.dormir(3)
  saida[#saida + 1] = "A2"
end)
s:criar("B", function()
  saida[#saida + 1] = "B1"
  esc.dormir(1)
  saida[#saida + 1] = "B2"
  esc.dormir(5)
  saida[#saida + 1] = "B3"
end)
assert(s:pendentes() == 2)
local fim = s:executar()
assert(table.concat(saida, ",") == "A1,B1,B2,A2,B3")
assert(fim == 6 and s:pendentes() == 0)
assert(table.concat(s.log, ",") == "0:A,0:B,1:B,3:A,6:B")

-- ceder: intercala sem passar o tempo
local s2 = esc.novo()
local o = {}
for _, nome in ipairs({ "x", "y" }) do
  s2:criar(nome, function()
    for i = 1, 3 do o[#o + 1] = nome .. i; esc.ceder() end
  end)
end
assert(s2:executar() == 0)
assert(table.concat(o, ",") == "x1,y1,x2,y2,x3,y3")

-- argumentos e retorno sem ceder
local s3 = esc.novo()
local soma
s3:criar("soma", function(a, b) soma = a + b end, 2, 3)
s3:executar()
assert(soma == 5)

-- erro numa tarefa não derruba as outras
local s4 = esc.novo()
local viva = false
s4:criar("ruim", function() esc.dormir(1); error("falhou") end)
s4:criar("boa", function() esc.dormir(2); viva = true end)
s4:executar()
assert(viva and #s4.erros == 1 and s4.erros[1].nome == "ruim" and s4.erros[1].erro:find("falhou"))

-- limite de tempo deixa tarefas pendentes
local s5 = esc.novo()
local n = 0
s5:criar("loop", function() while true do n = n + 1; esc.dormir(10) end end)
s5:executar(35)
assert(n == 4 and s5:pendentes() == 1)   -- ticks 0,10,20,30

-- tarefa criada por outra tarefa
local s6 = esc.novo()
local filha = false
s6:criar("mae", function() s6:criar("filha", function() filha = true end) end)
s6:executar()
assert(filha)

-- escalonador vazio e validações
assert(esc.novo():executar() == 0)
assert(not pcall(s.criar, s, "x", 42))
assert(not pcall(esc.dormir, -1))
print("ok")

local b = require("banco")
local c = b.Conta.nova("Ana", 100)
assert(c.saldo == 100)
assert(c:depositar(50) == 150)
assert(c:sacar(30) == 120)
local r, e = c:sacar(500); assert(r == nil and e == "saldo insuficiente")
r, e = c:sacar(0); assert(r == nil and e == "valor inválido")
r, e = c:sacar(-5); assert(r == nil and e == "valor inválido")
r, e = c:depositar("x"); assert(r == nil and e == "valor inválido")
assert(c:sacar(120) == 0)           -- zera exatamente
assert(#c.historico == 3 and c.historico[3].tipo == "saque")
assert(tostring(c) == "Ana: R$ 0.00")
assert(not pcall(b.Conta.nova, ""))
assert(not pcall(b.Conta.nova, "Bia", -1))

-- herança: conta especial
local e1 = b.ContaEspecial.nova("Caio", 50, 100)
assert(e1:disponivel() == 150)
assert(e1:sacar(120) == -70)
r, e = e1:sacar(31); assert(r == nil and e == "saldo insuficiente")
assert(e1:sacar(30) == -100)
assert(e1:depositar(10) == -90)     -- método herdado
assert(tostring(e1) == "Caio: R$ -90.00")
assert(getmetatable(e1) == b.ContaEspecial)
assert(not pcall(b.ContaEspecial.nova, "Z", 0, -1))
assert(b.ContaEspecial.nova("Sem limite", 5):disponivel() == 5)

-- banco e transferências
local bk = b.Banco.novo()
local i1 = bk:abrir(b.Conta.nova("A", 100))
local i2 = bk:abrir(b.Conta.nova("B", 20))
local i3 = bk:abrir(b.ContaEspecial.nova("C", 0, 50))
assert(bk:total() == 120)
assert(bk:transferir(i1, i2, 60))
assert(bk:conta(i1).saldo == 40 and bk:conta(i2).saldo == 80)
r, e = bk:transferir(i1, i2, 100); assert(r == nil and e == "saldo insuficiente")
assert(bk:conta(i1).saldo == 40 and bk:conta(i2).saldo == 80)  -- nada mudou
r, e = bk:transferir(i1, 99, 1); assert(r == nil and e == "conta inexistente")
r, e = bk:transferir(i1, i1, 1); assert(r == nil and e == "mesma conta")
assert(bk:transferir(i3, i1, 50))   -- usa o limite
assert(bk:conta(i3).saldo == -50 and bk:total() == 120)  -- transferência conserva o total
print("ok")

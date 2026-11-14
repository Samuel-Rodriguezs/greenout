local Pilha = require("pilha")

local p = Pilha.nova()
assert(p:vazia() and #p == 0 and not p:cheia())
local v, e = p:desempilhar()
assert(v == nil and e == "pilha vazia")
v, e = p:topo()
assert(v == nil and e == "pilha vazia")

assert(p:empilhar(1) and p:empilhar(2) and p:empilhar(3))
assert(#p == 3 and p:topo() == 3)
assert(p:desempilhar() == 3 and p:desempilhar() == 2 and #p == 1)
local l = Pilha.nova(); l:empilhar("a"); l:empilhar("b")
assert(table.concat(l:para_lista(), "") == "ba")

-- false é valor legítimo
local f = Pilha.nova()
f:empilhar(false)
assert(#f == 1 and f:desempilhar() == false and f:vazia())

-- capacidade
local c = Pilha.nova(2)
assert(c:empilhar(1) and c:empilhar(2) and c:cheia())
local ok, msg = c:empilhar(3)
assert(ok == nil and msg == "pilha cheia" and #c == 2)
c:desempilhar()
assert(not c:cheia() and c:empilhar(9))
assert(not pcall(Pilha.nova, 0))
assert(not pcall(Pilha.nova, 1.5))
assert(not pcall(Pilha.nova, "x"))

-- balanceamento
assert(Pilha.balanceado("") and Pilha.balanceado("(a[b]{c})"))
assert(not Pilha.balanceado("(]") and not Pilha.balanceado("((") and not Pilha.balanceado(")"))
assert(not Pilha.balanceado("([)]"))
print("ok")

local Deque = require("deque")

local d = Deque.novo()
assert(d:vazia() and #d == 0)
assert(d:remover_inicio() == nil and d:remover_fim() == nil)
assert(d:espiar_inicio() == nil and d:espiar_fim() == nil)

d:empurrar_fim(1):empurrar_fim(2):empurrar_inicio(0):empurrar_inicio(-1)
assert(#d == 4 and d:espiar_inicio() == -1 and d:espiar_fim() == 2)
assert(d:obter(1) == -1 and d:obter(4) == 2 and d:obter(0) == nil and d:obter(5) == nil)

local lista = {}
for i, v in d:itens() do lista[i] = v end
assert(table.concat(lista, ",") == "-1,0,1,2")

assert(d:remover_inicio() == -1 and d:remover_fim() == 2)
assert(#d == 2 and d:obter(1) == 0 and d:obter(2) == 1)
assert(d:remover_fim() == 1 and d:remover_fim() == 0 and d:vazia())

-- reutilização após esvaziar
d:empurrar_inicio("a")
assert(d:espiar_fim() == "a" and d:remover_inicio() == "a" and d:vazia())

-- comportamento de fila FIFO
local q = Deque.novo()
for i = 1, 100 do q:enfileirar(i) end
for i = 1, 100 do assert(q:desenfileirar() == i) end
assert(q:vazia())

-- falso/booleano são valores válidos
local b = Deque.novo()
b:empurrar_fim(false)
assert(#b == 1 and b:remover_inicio() == false)

q:enfileirar(1); q:limpar()
assert(q:vazia() and #q == 0)
print("ok")

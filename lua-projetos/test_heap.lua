local heap = require("heap")
local h = heap.novo()
assert(h:vazio() and h:tamanho() == 0 and h:topo() == nil and h:remover() == nil)
for _, v in ipairs({ 5, 3, 8, 1, 9, 2, 7 }) do h:inserir(v) end
assert(h:tamanho() == 7 and h:topo() == 1)
local out = {}
while not h:vazio() do out[#out + 1] = h:remover() end
assert(table.concat(out, ",") == "1,2,3,5,7,8,9")

-- heap de máximo
local mx = heap.novo(function(a, b) return a > b end)
for _, v in ipairs({ 4, 10, 2 }) do mx:inserir(v) end
assert(mx:remover() == 10 and mx:remover() == 4 and mx:remover() == 2)

-- prioridade com tabelas
local tarefas = heap.novo(function(a, b) return a.prio < b.prio end)
tarefas:inserir({ nome = "baixa", prio = 9 })
tarefas:inserir({ nome = "urgente", prio = 1 })
tarefas:inserir({ nome = "media", prio = 5 })
assert(tarefas:remover().nome == "urgente" and tarefas:topo().nome == "media")

-- duplicados e elemento único
local d = heap.ordenar({ 3, 1, 3, 1, 2 })
assert(table.concat(d, ",") == "1,1,2,3,3")
assert(#heap.ordenar({}) == 0)
assert(heap.ordenar({ 42 })[1] == 42)
assert(table.concat(heap.ordenar({ "b", "c", "a" }), "") == "abc")
assert(table.concat(heap.ordenar({ 1, 2, 3 }, function(a, b) return a > b end), ",") == "3,2,1")

-- aleatório contra table.sort
math.randomseed(123)
local l = {}
for i = 1, 500 do l[i] = math.random(1, 100) end
local ref = { table.unpack(l) }
table.sort(ref)
local r = heap.ordenar(l)
for i = 1, 500 do assert(r[i] == ref[i]) end
assert(not pcall(h.inserir, h, nil))
print("ok")

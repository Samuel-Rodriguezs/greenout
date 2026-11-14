local ps = require("pubsub")
local bus = ps.novo()
local recebidos = {}
local id1 = bus:assinar("pedido.criado", function(t, v) recebidos[#recebidos + 1] = t .. ":" .. tostring(v) end)
bus:assinar("pedido.*", function(t) recebidos[#recebidos + 1] = "curinga:" .. t end)
bus:assinar("*", function(t) recebidos[#recebidos + 1] = "todos:" .. t end)

assert(bus:publicar("pedido.criado", 7) == 3)
assert(recebidos[1] == "pedido.criado:7" and recebidos[2] == "curinga:pedido.criado" and recebidos[3] == "todos:pedido.criado")
assert(bus:publicar("pedido.pago") == 2)          -- só curinga e "*"
assert(bus:publicar("usuario.criado") == 1)       -- só "*"
assert(bus:publicar("pedido.item.novo") == 1)     -- segmentos diferentes: curinga não casa

-- cancelar
assert(bus:cancelar(id1) == true)
assert(bus:cancelar(id1) == false)
assert(bus:publicar("pedido.criado") == 2)

-- uma vez
local n = 0
bus:assinar_uma_vez("ping", function() n = n + 1 end)
local antes = bus:total()
bus:publicar("ping"); bus:publicar("ping")
assert(n == 1 and bus:total() == antes - 1)

-- callback com erro não derruba os outros
local b2 = ps.novo()
local ok = false
b2:assinar("x", function() error("boom") end)
b2:assinar("x", function() ok = true end)
assert(b2:publicar("x") == 2 and ok and #b2.erros == 1 and b2.erros[1]:find("boom"))

-- publicar sem assinantes; argumentos inválidos
assert(ps.novo():publicar("nada") == 0)
assert(not pcall(bus.assinar, bus, "", print))
assert(not pcall(bus.assinar, bus, "a", nil))

-- cancelar dentro do callback durante a publicação
local b3 = ps.novo()
local cont = 0
local idA
idA = b3:assinar("t", function() cont = cont + 1; b3:cancelar(idA) end)
b3:assinar("t", function() cont = cont + 10 end)
b3:publicar("t"); b3:publicar("t")
assert(cont == 21)
print("ok")

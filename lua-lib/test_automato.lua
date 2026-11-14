local Automato = require("automato")

local log = {}
local m = Automato.novo {
  inicial = "parado",
  finais = { "quebrado" },
  transicoes = {
    { de = "parado", evento = "ligar", para = "rodando" },
    { de = "rodando", evento = "parar", para = "parado" },
    { de = { "parado", "rodando" }, evento = "pausar", para = "pausado",
      acao = function(_, de, para) log[#log + 1] = "acao:" .. de .. ">" .. para end },
    { de = "pausado", evento = "ligar", para = "rodando",
      guarda = function(_, ok) return ok == true end },
    { de = "*", evento = "quebrar", para = "quebrado" },
  },
  ao_entrar = { rodando = function(_, de) log[#log + 1] = "entrou:rodando<" .. de end },
  ao_sair = { parado = function(_, para) log[#log + 1] = "saiu:parado>" .. para end },
}

assert(m.estado == "parado" and not m:final())
local ok, v = m:disparar("ligar")
assert(ok and v == "rodando" and m.estado == "rodando")
assert(log[1] == "saiu:parado>rodando" and log[2] == "entrou:rodando<parado")

-- evento inválido não muda o estado
ok, v = m:disparar("ligar")
assert(ok == false and v:find("transicao invalida") and m.estado == "rodando")
ok = m:disparar("inexistente")
assert(ok == false)

-- origem em lista + ação
m:disparar("pausar")
assert(m.estado == "pausado" and log[#log] == "acao:rodando>pausado")

-- guardas
assert(not m:pode("ligar") and m:pode("ligar", true))
assert(m:disparar("ligar") == false and m.estado == "pausado")
assert(m:disparar("ligar", true) and m.estado == "rodando")

-- eventos possíveis e histórico
local ev = m:eventos_possiveis()
assert(table.concat(ev, ",") == "pausar,parar,quebrar" or table.concat(ev, ",") == "parar,pausar,quebrar")
assert(table.concat(m.historico, ">") == "parado>rodando>pausado>rodando")

-- curinga e estado final bloqueia tudo
assert(m:disparar("quebrar") and m:final() and m.estado == "quebrado")
ok, v = m:disparar("parar")
assert(ok == false and v == "estado final")

-- definições inválidas
assert(not pcall(Automato.novo, {}))
assert(not pcall(Automato.novo, nil))
assert(not pcall(Automato.novo, { inicial = "a", transicoes = { { de = "a", evento = "x" } } }))

-- máquina sem transições
local vazio = Automato.novo { inicial = 1 }
assert(vazio:disparar("x") == false and #vazio:eventos_possiveis() == 0)
print("ok")

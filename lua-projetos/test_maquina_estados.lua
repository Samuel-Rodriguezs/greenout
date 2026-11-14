local fsm = require("maquina_estados")
local log = {}
local m = fsm.nova({
  inicial = "verde",
  transicoes = {
    { "avancar", "verde", "amarelo" },
    { "avancar", "amarelo", "vermelho" },
    { "avancar", "vermelho", "verde" },
    { "pane", "*", "piscando" },
    { "reparar", "piscando", "verde" },
  },
  ao_entrar = { amarelo = function(_, de) log[#log + 1] = "entrou amarelo de " .. de end },
  ao_sair = { verde = function(_, para) log[#log + 1] = "saiu verde para " .. para end },
})
assert(m.estado == "verde")
assert(m:pode("avancar") and not m:pode("reparar") and not m:pode("nada"))
assert(m:disparar("avancar") == "amarelo")
assert(log[1] == "saiu verde para amarelo" and log[2] == "entrou amarelo de verde")
assert(m:disparar("avancar") == "vermelho")
assert(m:disparar("avancar") == "verde")
local r, e = m:disparar("reparar")
assert(r == nil and e == "transição inválida: reparar em verde")
r, e = m:disparar("xyz"); assert(r == nil and e == "evento desconhecido: xyz")
assert(m:disparar("pane") == "piscando")      -- coringa "*"
assert(m:disparar("reparar") == "verde")
assert(table.concat(m.historico, ",") == "verde,amarelo,vermelho,verde,piscando,verde")

-- guarda
local moedas = 0
local porta = fsm.nova({
  inicial = "fechada",
  transicoes = { { "abrir", "fechada", "aberta", function() return moedas >= 2 end },
                 { "fechar", "aberta", "fechada" } },
})
r, e = porta:disparar("abrir"); assert(r == nil and e == "guarda bloqueou a transição")
assert(porta:pode("abrir") == false)
moedas = 2
assert(porta:pode("abrir") == true)
assert(porta:disparar("abrir") == "aberta" and porta:disparar("fechar") == "fechada")

-- auto-transição e definição inválida
local s = fsm.nova({ inicial = "a", transicoes = { { "x", "a", "a" } } })
assert(s:disparar("x") == "a" and #s.historico == 2)
assert(not pcall(fsm.nova, {}))
assert(not pcall(fsm.nova))
print("ok")

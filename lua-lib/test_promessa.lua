local P = require("promessa")

local function valor(p) P.executar(); return p.estado, p.valor end

-- resolução básica e assíncrona (callbacks só rodam em executar)
local log = {}
local p = P.resolvida(5)
local q = p:entao(function(v) log[#log + 1] = v; return v * 2 end)
assert(#log == 0 and q.estado == "pendente")
local st, v = valor(q)
assert(st == "cumprida" and v == 10 and log[1] == 5)

-- encadeamento e propagação de erro
local r = P.resolvida(1)
  :entao(function(x) return x + 1 end)
  :entao(function(x) error("ops", 0) end)
  :entao(function() log.nunca = true end)
  :capturar(function(e) return "tratado:" .. e end)
st, v = valor(r)
assert(st == "cumprida" and v == "tratado:ops" and not log.nunca)

-- rejeição sem tratador propaga
st, v = valor(P.rejeitada("x"):entao(function() end))
assert(st == "rejeitada" and v == "x")

-- executor que lança erro rejeita; segunda resolução é ignorada
st, v = valor(P.nova(function() error("boom", 0) end))
assert(st == "rejeitada" and v == "boom")
st, v = valor(P.nova(function(res, rej) res(1); res(2); rej(3) end))
assert(st == "cumprida" and v == 1)

-- resolver com outra promessa (adoção)
local interna = P.nova(function(res) res("dentro") end)
st, v = valor(P.nova(function(res) res(interna) end))
assert(st == "cumprida" and v == "dentro")
-- ciclo: promessa resolvida com ela mesma é rejeitada
local ciclo_res
local ciclo = P.nova(function(res) ciclo_res = res end)
ciclo_res(ciclo)
st, v = valor(ciclo)
assert(st == "rejeitada" and v:find("ciclo"))

-- promessa pendente resolvida depois
local res_ext
local pend = P.nova(function(res) res_ext = res end)
local capturado
pend:entao(function(x) capturado = x end)
P.executar()
assert(capturado == nil and pend.estado == "pendente")
res_ext("tarde")
P.executar()
assert(capturado == "tarde")

-- finalmente
local fin = 0
st, v = valor(P.resolvida(7):finalmente(function() fin = fin + 1 end))
assert(st == "cumprida" and v == 7 and fin == 1)
st, v = valor(P.rejeitada("e"):finalmente(function() fin = fin + 1 end))
assert(st == "rejeitada" and v == "e" and fin == 2)

-- todas
st, v = valor(P.todas({ P.resolvida(1), 2, P.resolvida(3) }))
assert(st == "cumprida" and #v == 3 and v[1] == 1 and v[2] == 2 and v[3] == 3)
st, v = valor(P.todas({}))
assert(st == "cumprida" and #v == 0)
st, v = valor(P.todas({ P.resolvida(1), P.rejeitada("falha") }))
assert(st == "rejeitada" and v == "falha")

-- corrida
st, v = valor(P.corrida({ P.resolvida("a"), P.resolvida("b") }))
assert(st == "cumprida" and v == "a")
st, v = valor(P.corrida({ P.rejeitada("r"), P.resolvida("b") }))
assert(st == "rejeitada" and v == "r")

-- async/await com corrotinas
local a = P.assincrona(function(x)
  local s = P.aguardar(P.resolvida(x))
  local t = P.aguardar(P.nova(function(res) res(s + 1) end))
  return t * 10
end, 4)
st, v = valor(a)
assert(st == "cumprida" and v == 50)

-- await de rejeição vira erro capturável
local b = P.assincrona(function()
  local ok, err = pcall(P.aguardar, P.rejeitada("nao"))
  assert(not ok and err == "nao")
  return "recuperado"
end)
st, v = valor(b)
assert(st == "cumprida" and v == "recuperado")

-- erro não tratado na corrotina rejeita a promessa
st, v = valor(P.assincrona(function() error("quebrou", 0) end))
assert(st == "rejeitada" and v == "quebrou")
st, v = valor(P.assincrona(function() P.aguardar(P.rejeitada("rej")) end))
assert(st == "rejeitada" and v == "rej")

-- aguardar fora de corrotina
assert(not pcall(P.aguardar, P.resolvida(1)))
-- executar sem tarefas
assert(P.executar() == 0)
print("ok")

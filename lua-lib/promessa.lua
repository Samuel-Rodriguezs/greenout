-- Promessa (Promise/Future simplificada) com fila de microtarefas e async/await via corrotinas.
-- O agendamento é explícito: chame `Promessa.executar()` para processar as tarefas pendentes.
local Promessa = {}
Promessa.__index = Promessa

local fila, ini, fim = {}, 1, 0

local function agendar(f)
  fim = fim + 1
  fila[fim] = f
end

-- Executa todas as microtarefas (inclusive as criadas durante a execução).
function Promessa.executar()
  local n = 0
  while ini <= fim do
    local f = fila[ini]
    fila[ini] = nil
    ini = ini + 1
    f()
    n = n + 1
  end
  ini, fim = 1, 0
  return n
end

local function eh_promessa(v) return getmetatable(v) == Promessa end

local function nova_interna()
  return setmetatable({ estado = "pendente", valor = nil, _cbs = {} }, Promessa)
end

local function assentar(p, estado, valor)
  if p.estado ~= "pendente" then return end
  p.estado, p.valor = estado, valor
  local cbs = p._cbs
  p._cbs = nil
  for _, cb in ipairs(cbs) do agendar(cb) end
end

-- Cria as funções resolver/rejeitar; só a primeira chamada tem efeito.
local function resolvedores(p)
  local usado = false
  local resolver, rejeitar
  rejeitar = function(motivo)
    if usado then return end
    usado = true
    assentar(p, "rejeitada", motivo)
  end
  resolver = function(v)
    if usado then return end
    usado = true
    if v == p then assentar(p, "rejeitada", "ciclo: promessa resolvida com ela mesma"); return end
    if eh_promessa(v) then
      v:entao(function(x) assentar(p, "cumprida", x) end, function(e) assentar(p, "rejeitada", e) end)
    else
      assentar(p, "cumprida", v)
    end
  end
  return resolver, rejeitar
end

-- executor(resolver, rejeitar) roda imediatamente; erro nele rejeita a promessa.
function Promessa.nova(executor)
  local p = nova_interna()
  local res, rej = resolvedores(p)
  local ok, err = pcall(executor, res, rej)
  if not ok then rej(err) end
  return p
end

function Promessa.resolvida(v)
  if eh_promessa(v) then return v end
  return Promessa.nova(function(res) res(v) end)
end

function Promessa.rejeitada(motivo)
  return Promessa.nova(function(_, rej) rej(motivo) end)
end

function Promessa:entao(ao_cumprir, ao_rejeitar)
  local filha = nova_interna()
  local res, rej = resolvedores(filha)
  local function tratar()
    local cumprida = self.estado == "cumprida"
    local cb = cumprida and ao_cumprir or ao_rejeitar
    if type(cb) ~= "function" then
      if cumprida then res(self.valor) else rej(self.valor) end
      return
    end
    local ok, r = pcall(cb, self.valor)
    if ok then res(r) else rej(r) end
  end
  if self.estado == "pendente" then
    self._cbs[#self._cbs + 1] = tratar
  else
    agendar(tratar)
  end
  return filha
end

function Promessa:capturar(f) return self:entao(nil, f) end

-- f roda em qualquer desfecho; o valor/motivo original é preservado.
function Promessa:finalmente(f)
  return self:entao(
    function(v) f(); return v end,
    function(e) f(); error(e, 0) end)
end

-- Cumpre com a lista de resultados (em ordem); rejeita na primeira rejeição.
function Promessa.todas(lista)
  return Promessa.nova(function(res, rej)
    local n, restantes, resultados = #lista, #lista, {}
    if n == 0 then res(resultados); return end
    for i, item in ipairs(lista) do
      Promessa.resolvida(item):entao(function(v)
        resultados[i] = v
        restantes = restantes - 1
        if restantes == 0 then res(resultados) end
      end, rej)
    end
  end)
end

-- Assume o desfecho da primeira promessa a se assentar.
function Promessa.corrida(lista)
  return Promessa.nova(function(res, rej)
    for _, item in ipairs(lista) do Promessa.resolvida(item):entao(res, rej) end
  end)
end

-- Executa f(...) numa corrotina; dentro dela use `Promessa.aguardar(p)`.
function Promessa.assincrona(f, ...)
  local args = table.pack(...)
  return Promessa.nova(function(res, rej)
    local co = coroutine.create(f)
    local passo
    passo = function(...)
      local r = table.pack(coroutine.resume(co, ...))
      if not r[1] then rej(r[2]); return end
      if coroutine.status(co) == "dead" then res(r[2]); return end
      Promessa.resolvida(r[2]):entao(
        function(v) passo(true, v) end,
        function(e) passo(false, e) end)
    end
    passo(table.unpack(args, 1, args.n))
  end)
end

-- Suspende a corrotina atual até a promessa se assentar; relança o erro se rejeitada.
function Promessa.aguardar(p)
  if not coroutine.isyieldable() then error("aguardar fora de Promessa.assincrona", 2) end
  local ok, v = coroutine.yield(p)
  if not ok then error(v, 0) end
  return v
end

return Promessa

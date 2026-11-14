-- EventEmitter: registro e disparo de eventos nomeados.
local Emissor = {}
Emissor.__index = Emissor

function Emissor.novo()
  return setmetatable({ _ouvintes = {} }, Emissor)
end

local function adicionar(self, evento, f, uma_vez)
  if evento == nil then error("evento nil", 3) end
  if type(f) ~= "function" then error("ouvinte deve ser funcao", 3) end
  local lista = self._ouvintes[evento]
  if not lista then lista = {}; self._ouvintes[evento] = lista end
  lista[#lista + 1] = { f = f, uma_vez = uma_vez }
  return f
end

-- Registra ouvinte; retorna a própria função (útil para `desligar`).
function Emissor:ligar(evento, f) return adicionar(self, evento, f, false) end
function Emissor:uma_vez(evento, f) return adicionar(self, evento, f, true) end

-- Remove um ouvinte (ou todos do evento quando `f` é nil). Retorna quantos removeu.
function Emissor:desligar(evento, f)
  local lista = self._ouvintes[evento]
  if not lista then return 0 end
  if f == nil then
    self._ouvintes[evento] = nil
    return #lista
  end
  local novos, removidos = {}, 0
  for _, o in ipairs(lista) do
    if o.f == f and removidos == 0 then removidos = 1 else novos[#novos + 1] = o end
  end
  self._ouvintes[evento] = #novos > 0 and novos or nil
  return removidos
end

-- Dispara o evento; devolve a quantidade de ouvintes chamados.
-- Trabalha sobre uma cópia, então ouvintes podem se (des)registrar durante o disparo.
function Emissor:emitir(evento, ...)
  local lista = self._ouvintes[evento]
  if not lista then return 0 end
  local copia = { table.unpack(lista) }
  for _, o in ipairs(copia) do
    if o.uma_vez then self:desligar(evento, o.f) end
  end
  for _, o in ipairs(copia) do o.f(...) end
  return #copia
end

function Emissor:contar(evento)
  local l = self._ouvintes[evento]
  return l and #l or 0
end

function Emissor:eventos()
  local r = {}
  for e in pairs(self._ouvintes) do r[#r + 1] = e end
  table.sort(r, function(a, b) return tostring(a) < tostring(b) end)
  return r
end

return Emissor

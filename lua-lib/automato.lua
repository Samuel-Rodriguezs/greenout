-- Máquina de estados finita com guardas, ações, hooks de entrada/saída e histórico.
-- def = { inicial = "a", finais = {"z"}, transicoes = { {de=, evento=, para=, guarda=fn, acao=fn}, ... },
--         ao_entrar = { estado = fn }, ao_sair = { estado = fn } }
-- `de` pode ser uma lista de estados ou "*" (qualquer estado).
local Automato = {}
Automato.__index = Automato

function Automato.novo(def)
  if type(def) ~= "table" or def.inicial == nil then error("definicao requer 'inicial'", 2) end
  local m = setmetatable({
    estado = def.inicial,
    _tabela = {},       -- [evento] = lista de transições
    _finais = {},
    _entrar = def.ao_entrar or {},
    _sair = def.ao_sair or {},
    historico = { def.inicial },
  }, Automato)
  for _, f in ipairs(def.finais or {}) do m._finais[f] = true end
  for _, t in ipairs(def.transicoes or {}) do
    if t.evento == nil or t.para == nil or t.de == nil then
      error("transicao incompleta (de, evento, para)", 2)
    end
    local lista = m._tabela[t.evento]
    if not lista then lista = {}; m._tabela[t.evento] = lista end
    lista[#lista + 1] = t
  end
  return m
end

local function origem_casa(t, estado)
  if t.de == "*" then return true end
  if type(t.de) == "table" then
    for _, e in ipairs(t.de) do if e == estado then return true end end
    return false
  end
  return t.de == estado
end

local function achar(self, evento, ...)
  for _, t in ipairs(self._tabela[evento] or {}) do
    if origem_casa(t, self.estado) and (not t.guarda or t.guarda(self, ...)) then return t end
  end
end

function Automato:pode(evento, ...)
  return achar(self, evento, ...) ~= nil
end

-- Dispara um evento. Retorna true, novo_estado; ou false, motivo se não houver transição.
function Automato:disparar(evento, ...)
  if self:final() then return false, "estado final" end
  local t = achar(self, evento, ...)
  if not t then return false, "transicao invalida: " .. tostring(evento) .. " em " .. tostring(self.estado) end
  local antes = self.estado
  if self._sair[antes] then self._sair[antes](self, t.para, ...) end
  self.estado = t.para
  self.historico[#self.historico + 1] = t.para
  if t.acao then t.acao(self, antes, t.para, ...) end
  if self._entrar[t.para] then self._entrar[t.para](self, antes, ...) end
  return true, t.para
end

function Automato:final() return self._finais[self.estado] == true end

-- Eventos aceitos no estado atual (ignorando guardas), em ordem alfabética.
function Automato:eventos_possiveis()
  local r = {}
  for ev, lista in pairs(self._tabela) do
    for _, t in ipairs(lista) do
      if origem_casa(t, self.estado) then r[#r + 1] = ev; break end
    end
  end
  table.sort(r, function(a, b) return tostring(a) < tostring(b) end)
  return r
end

return Automato

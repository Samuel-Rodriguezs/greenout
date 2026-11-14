-- Máquina de estados finitos com transições nomeadas, guardas e callbacks.
local M = {}
M.__index = M

-- definicao = { inicial = "x", transicoes = { {evento, de, para, guarda?}, ... },
--               ao_entrar = { estado = fn }, ao_sair = { estado = fn } }
function M.nova(def)
  assert(def and def.inicial, "estado inicial obrigatório")
  local self = setmetatable({}, M)
  self.estado = def.inicial
  self.tabela = {}
  self.ao_entrar = def.ao_entrar or {}
  self.ao_sair = def.ao_sair or {}
  self.historico = { def.inicial }
  for _, t in ipairs(def.transicoes or {}) do
    local evento, de, para, guarda = t[1], t[2], t[3], t[4]
    self.tabela[evento] = self.tabela[evento] or {}
    self.tabela[evento][de] = { para = para, guarda = guarda }
  end
  return self
end

function M:pode(evento)
  local t = self.tabela[evento] and (self.tabela[evento][self.estado] or self.tabela[evento]["*"])
  if not t then return false end
  return t.guarda == nil or t.guarda(self) and true or false
end

-- Dispara um evento. Retorna o novo estado ou nil, motivo.
function M:disparar(evento)
  if not self.tabela[evento] then return nil, "evento desconhecido: " .. evento end
  local t = self.tabela[evento][self.estado] or self.tabela[evento]["*"]
  if not t then
    return nil, "transição inválida: " .. evento .. " em " .. self.estado
  end
  if t.guarda and not t.guarda(self) then return nil, "guarda bloqueou a transição" end
  local antigo = self.estado
  if self.ao_sair[antigo] then self.ao_sair[antigo](self, t.para) end
  self.estado = t.para
  self.historico[#self.historico + 1] = t.para
  if self.ao_entrar[t.para] then self.ao_entrar[t.para](self, antigo) end
  return self.estado
end

return M

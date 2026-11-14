-- Publicação/assinatura (pub/sub) com tópicos e curinga "*" por segmento.
local M = {}
M.__index = M

function M.novo()
  return setmetatable({ assinaturas = {}, proximo_id = 1 }, M)
end

-- Compara tópico "a.b.c" com padrão "a.*.c" ou "*" (qualquer coisa).
local function casa(padrao, topico)
  if padrao == "*" or padrao == topico then return true end
  local p, t = {}, {}
  for s in padrao:gmatch("[^%.]+") do p[#p + 1] = s end
  for s in topico:gmatch("[^%.]+") do t[#t + 1] = s end
  if #p ~= #t then return false end
  for i = 1, #p do
    if p[i] ~= "*" and p[i] ~= t[i] then return false end
  end
  return true
end

-- Retorna um id de assinatura (usado em cancelar).
function M:assinar(padrao, fn, uma_vez)
  assert(type(padrao) == "string" and padrao ~= "", "padrão inválido")
  assert(type(fn) == "function", "callback deve ser função")
  local id = self.proximo_id
  self.proximo_id = id + 1
  self.assinaturas[#self.assinaturas + 1] = { id = id, padrao = padrao, fn = fn, uma_vez = uma_vez }
  return id
end

function M:assinar_uma_vez(padrao, fn) return self:assinar(padrao, fn, true) end

function M:cancelar(id)
  for i, a in ipairs(self.assinaturas) do
    if a.id == id then
      table.remove(self.assinaturas, i)
      return true
    end
  end
  return false
end

-- Publica; devolve quantos assinantes receberam. Erros em callbacks não
-- interrompem os demais; são coletados em self.erros.
function M:publicar(topico, ...)
  local alvos = {}
  for _, a in ipairs(self.assinaturas) do
    if casa(a.padrao, topico) then alvos[#alvos + 1] = a end
  end
  self.erros = {}
  for _, a in ipairs(alvos) do
    if a.uma_vez then self:cancelar(a.id) end
    local ok, err = pcall(a.fn, topico, ...)
    if not ok then self.erros[#self.erros + 1] = err end
  end
  return #alvos
end

function M:total() return #self.assinaturas end

return M

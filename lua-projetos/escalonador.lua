-- Escalonador cooperativo com corrotinas e relógio virtual de "ticks".
-- Tarefas cedem o controle com escalonador.dormir(n) ou escalonador.ceder().
local M = {}
M.__index = M

function M.novo()
  return setmetatable({ agora = 0, tarefas = {}, proximo_id = 1, log = {}, erros = {} }, M)
end

-- Cria uma tarefa; retorna seu id. Argumentos extras vão para a função.
function M:criar(nome, fn, ...)
  assert(type(fn) == "function", "tarefa deve ser função")
  local id = self.proximo_id
  self.proximo_id = id + 1
  local args = table.pack(...)
  local co = coroutine.create(function() return fn(table.unpack(args, 1, args.n)) end)
  self.tarefas[#self.tarefas + 1] = { id = id, nome = nome, co = co, acorda_em = self.agora }
  return id
end

-- Chamadas feitas de dentro de uma tarefa:
function M.dormir(ticks)
  assert(type(ticks) == "number" and ticks >= 0, "ticks inválido")
  coroutine.yield(ticks)
end
function M.ceder() coroutine.yield(0) end

-- Executa uma tarefa até ela ceder; devolve true se ainda está viva.
local function avancar(self, t)
  local ok, pedido = coroutine.resume(t.co)
  if not ok then
    self.erros[#self.erros + 1] = { nome = t.nome, erro = pedido }
    return false
  end
  if coroutine.status(t.co) == "dead" then return false end
  t.acorda_em = self.agora + (pedido or 0)
  return true
end

-- Roda até todas as tarefas terminarem (ou até `limite` ticks). Retorna o tempo final.
function M:executar(limite)
  while #self.tarefas > 0 do
    if limite and self.agora > limite then break end
    -- escolhe as tarefas prontas, em ordem de criação
    local prontas = {}
    for _, t in ipairs(self.tarefas) do
      if t.acorda_em <= self.agora then prontas[#prontas + 1] = t end
    end
    if #prontas == 0 then
      local prox = math.huge
      for _, t in ipairs(self.tarefas) do
        if t.acorda_em < prox then prox = t.acorda_em end
      end
      if limite and prox > limite then break end
      self.agora = prox
    else
      for _, t in ipairs(prontas) do
        self.log[#self.log + 1] = self.agora .. ":" .. t.nome
        if not avancar(self, t) then
          for i, x in ipairs(self.tarefas) do
            if x == t then table.remove(self.tarefas, i); break end
          end
        end
      end
    end
  end
  return self.agora
end

function M:pendentes() return #self.tarefas end

return M

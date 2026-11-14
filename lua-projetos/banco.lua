-- Simulador de banco com OOP via metatables e herança.
local M = {}

-- Conta base --------------------------------------------------------------
local Conta = {}
Conta.__index = Conta
M.Conta = Conta

function Conta.nova(titular, saldo_inicial)
  assert(type(titular) == "string" and titular ~= "", "titular inválido")
  saldo_inicial = saldo_inicial or 0
  assert(saldo_inicial >= 0, "saldo inicial negativo")
  local self = setmetatable({}, Conta)
  self.titular = titular
  self.saldo = saldo_inicial
  self.historico = {}
  return self
end

function Conta:_registrar(tipo, valor)
  self.historico[#self.historico + 1] = { tipo = tipo, valor = valor, saldo = self.saldo }
end

function Conta:depositar(valor)
  if type(valor) ~= "number" or valor <= 0 then return nil, "valor inválido" end
  self.saldo = self.saldo + valor
  self:_registrar("deposito", valor)
  return self.saldo
end

-- Quanto ainda pode ser sacado (sobrescrito em ContaEspecial).
function Conta:disponivel() return self.saldo end

function Conta:sacar(valor)
  if type(valor) ~= "number" or valor <= 0 then return nil, "valor inválido" end
  if valor > self:disponivel() then return nil, "saldo insuficiente" end
  self.saldo = self.saldo - valor
  self:_registrar("saque", valor)
  return self.saldo
end

function Conta:__tostring()
  return string.format("%s: R$ %.2f", self.titular, self.saldo)
end

-- Conta especial (cheque especial) -------------------------------------------
local ContaEspecial = setmetatable({}, { __index = Conta })
ContaEspecial.__index = ContaEspecial
ContaEspecial.__tostring = Conta.__tostring
M.ContaEspecial = ContaEspecial

function ContaEspecial.nova(titular, saldo_inicial, limite)
  local self = Conta.nova(titular, saldo_inicial)
  assert(limite == nil or limite >= 0, "limite negativo")
  self.limite = limite or 0
  return setmetatable(self, ContaEspecial)
end

function ContaEspecial:disponivel() return self.saldo + self.limite end

-- Banco -----------------------------------------------------------------
local Banco = {}
Banco.__index = Banco
M.Banco = Banco

function Banco.novo()
  return setmetatable({ contas = {}, proximo = 1 }, Banco)
end

function Banco:abrir(conta)
  local id = self.proximo
  self.proximo = id + 1
  self.contas[id] = conta
  return id
end

function Banco:conta(id) return self.contas[id] end

function Banco:transferir(de, para, valor)
  local o, d = self.contas[de], self.contas[para]
  if not o or not d then return nil, "conta inexistente" end
  if de == para then return nil, "mesma conta" end
  local ok, err = o:sacar(valor)
  if not ok then return nil, err end
  d:depositar(valor)
  return true
end

function Banco:total()
  local t = 0
  for _, c in pairs(self.contas) do t = t + c.saldo end
  return t
end

return M

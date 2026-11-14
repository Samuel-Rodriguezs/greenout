-- Logger com níveis, saída injetável e relógio injetável (testável sem I/O real).
local Logger = {}
Logger.__index = Logger

local NIVEIS = { debug = 1, info = 2, aviso = 3, erro = 4, nenhum = 5 }
local NOMES = { "DEBUG", "INFO", "AVISO", "ERRO" }

-- opcoes: nivel ("info"), saida (função(linha) ou objeto com :write), relogio (função -> texto),
--         prefixo (texto)
function Logger.novo(opcoes)
  opcoes = opcoes or {}
  local nivel = NIVEIS[opcoes.nivel or "info"]
  if not nivel then error("nivel desconhecido: " .. tostring(opcoes.nivel), 2) end
  local saida = opcoes.saida
  if saida == nil then
    saida = function(linha) io.stderr:write(linha, "\n") end
  elseif type(saida) ~= "function" then
    local alvo = saida
    saida = function(linha) alvo:write(linha, "\n") end
  end
  return setmetatable({
    _nivel = nivel, _saida = saida, _relogio = opcoes.relogio, _prefixo = opcoes.prefixo,
  }, Logger)
end

function Logger:definir_nivel(nome)
  if not NIVEIS[nome] then error("nivel desconhecido: " .. tostring(nome), 2) end
  self._nivel = NIVEIS[nome]
end

function Logger:habilitado(nome)
  return NIVEIS[nome] >= self._nivel
end

local function registrar(self, n, msg, ...)
  if n < self._nivel then return false end
  if select("#", ...) > 0 then msg = string.format(msg, ...) else msg = tostring(msg) end
  local partes = {}
  if self._relogio then partes[#partes + 1] = self._relogio() end
  partes[#partes + 1] = "[" .. NOMES[n] .. "]"
  if self._prefixo then partes[#partes + 1] = self._prefixo .. ":" end
  partes[#partes + 1] = msg
  self._saida(table.concat(partes, " "))
  return true
end

-- Cada método retorna true se a mensagem foi emitida.
function Logger:debug(...) return registrar(self, 1, ...) end
function Logger:info(...) return registrar(self, 2, ...) end
function Logger:aviso(...) return registrar(self, 3, ...) end
function Logger:erro(...) return registrar(self, 4, ...) end

-- Logger derivado que compartilha saída, nível atual e relógio, com prefixo acumulado.
function Logger:filho(prefixo)
  local p = self._prefixo and (self._prefixo .. "." .. prefixo) or prefixo
  return setmetatable({
    _nivel = self._nivel, _saida = self._saida, _relogio = self._relogio, _prefixo = p,
  }, Logger)
end

return Logger

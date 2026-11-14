-- Sistema de classes com herança simples.
-- Uso: local Animal = classe.nova(); function Animal:init(nome) self.nome = nome end
--      local Cao = classe.nova(Animal, "Cao"); local c = Cao("rex")
local M = {}

-- Cria uma nova classe, opcionalmente derivada de `base`.
function M.nova(base, nome)
  local cls = {}
  cls.__index = cls
  cls.base = base
  cls.nome = nome or "Classe"
  cls.__tostring = function()
    return "instancia de " .. cls.nome
  end
  -- metamétodos não são herdados por __index, então copiamos da base
  if base then
    for _, mm in ipairs { "__eq", "__lt", "__le", "__add", "__sub", "__mul", "__div", "__concat", "__len" } do
      cls[mm] = base[mm]
    end
  end
  setmetatable(cls, {
    __index = base,
    __call = function(c, ...)
      local obj = setmetatable({}, c)
      if c.init then c.init(obj, ...) end
      return obj
    end,
  })
  return cls
end

-- Verifica se `obj` é instância de `cls` (ou de uma subclasse).
function M.instancia_de(obj, cls)
  if type(obj) ~= "table" then return false end
  local c = getmetatable(obj)
  while c do
    if c == cls then return true end
    c = c.base
  end
  return false
end

-- Chama o método `metodo` da superclasse de `cls` sobre `self`.
function M.super(cls, metodo, self, ...)
  local base = cls.base
  if not base then error("classe sem superclasse: " .. tostring(cls.nome), 2) end
  local f = base[metodo]
  if type(f) ~= "function" then error("metodo inexistente na superclasse: " .. tostring(metodo), 2) end
  return f(self, ...)
end

return M

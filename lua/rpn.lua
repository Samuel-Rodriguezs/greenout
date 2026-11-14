-- Mini-parser de notação polonesa reversa (RPN).
local M = {}

local ops = {
  ["+"] = function(a, b) return a + b end,
  ["-"] = function(a, b) return a - b end,
  ["*"] = function(a, b) return a * b end,
  ["/"] = function(a, b)
    if b == 0 then error("divisão por zero", 0) end
    return a / b
  end,
}

-- Avalia a expressão; levanta erro (string) se for inválida.
function M.avaliar(expr)
  local pilha = {}
  for token in expr:gmatch("%S+") do
    if ops[token] then
      if #pilha < 2 then error("operandos insuficientes para '" .. token .. "'", 0) end
      local b = table.remove(pilha)
      local a = table.remove(pilha)
      pilha[#pilha + 1] = ops[token](a, b)
    else
      local n = tonumber(token)
      if not n then error("token inválido: " .. token, 0) end
      pilha[#pilha + 1] = n
    end
  end
  if #pilha ~= 1 then error("expressão malformada", 0) end
  return pilha[1]
end

-- Versão segura: retorna valor ou nil, mensagem.
function M.tentar(expr)
  local ok, r = pcall(M.avaliar, expr)
  if ok then return r end
  return nil, r
end

return M

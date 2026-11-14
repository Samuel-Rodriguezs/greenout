-- FizzBuzz: devolve a sequência de 1 a n com substituições.
local M = {}

-- Retorna a representação de um único número.
function M.converter(n)
  if n % 15 == 0 then return "FizzBuzz"
  elseif n % 3 == 0 then return "Fizz"
  elseif n % 5 == 0 then return "Buzz" end
  return tostring(n)
end

-- Retorna uma tabela com os resultados de 1 até n (vazia se n < 1).
function M.fizzbuzz(n)
  local r = {}
  for i = 1, n do r[#r + 1] = M.converter(i) end
  return r
end

return M

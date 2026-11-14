-- Gerador de UUID versão 4 (RFC 4122) com semente opcional (determinístico para testes).
-- Não é criptograficamente seguro: usa o LCG do módulo `prng`.
local Prng = require("prng")
local M = {}

local PADRAO = "^%x%x%x%x%x%x%x%x%-%x%x%x%x%-4%x%x%x%-[89abAB]%x%x%x%-%x%x%x%x%x%x%x%x%x%x%x%x$"

-- `fonte` pode ser um gerador Prng, uma semente inteira, ou nil (semente = tempo + relógio).
function M.gerar(fonte)
  local g
  if type(fonte) == "table" then
    g = fonte
  elseif fonte == nil then
    g = Prng.novo(os.time() * 1000003 + math.floor(os.clock() * 1e6))
  else
    g = Prng.novo(fonte)
  end
  local b = {}
  for i = 1, 16 do b[i] = g:inteiro(0, 255) end
  b[7] = (b[7] & 0x0F) | 0x40   -- versão 4
  b[9] = (b[9] & 0x3F) | 0x80   -- variante RFC 4122
  local h = {}
  for i = 1, 16 do h[i] = string.format("%02x", b[i]) end
  return table.concat(h, "", 1, 4) .. "-" .. table.concat(h, "", 5, 6) .. "-"
    .. table.concat(h, "", 7, 8) .. "-" .. table.concat(h, "", 9, 10) .. "-"
    .. table.concat(h, "", 11, 16)
end

function M.valido(s)
  return type(s) == "string" and s:find(PADRAO) ~= nil
end

-- Nulo (todos os bits zero) é válido na RFC mas não é v4.
M.NULO = "00000000-0000-0000-0000-000000000000"

return M

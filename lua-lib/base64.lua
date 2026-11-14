-- Codificação e decodificação Base64 (RFC 4648), com variante URL-safe, usando operadores de bits.
local M = {}

local ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
local ALFABETO_URL = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"

local function tabelas(alfa)
  local enc, dec = {}, {}
  for i = 1, 64 do
    local c = alfa:sub(i, i)
    enc[i - 1] = c
    dec[c:byte()] = i - 1
  end
  return enc, dec
end

local ENC, DEC = tabelas(ALFABETO)
local ENC_URL, DEC_URL = tabelas(ALFABETO_URL)

-- opcoes: { url = true } usa alfabeto URL-safe; { sem_padding = true } omite "=".
function M.codificar(dados, opcoes)
  opcoes = opcoes or {}
  local enc = opcoes.url and ENC_URL or ENC
  local saida = {}
  for i = 1, #dados, 3 do
    local a, b, c = dados:byte(i, i + 2)
    local n = (a << 16) | ((b or 0) << 8) | (c or 0)
    saida[#saida + 1] = enc[(n >> 18) & 63] .. enc[(n >> 12) & 63]
      .. (b and enc[(n >> 6) & 63] or "=")
      .. (c and enc[n & 63] or "=")
  end
  local r = table.concat(saida)
  if opcoes.sem_padding then r = r:gsub("=+$", "") end
  return r
end

-- Retorna a string decodificada, ou nil, mensagem se a entrada for inválida.
-- Aceita (e ignora) espaços em branco; padding opcional.
function M.decodificar(texto, opcoes)
  opcoes = opcoes or {}
  local dec = opcoes.url and DEC_URL or DEC
  texto = texto:gsub("%s+", "")
  local corpo, pad = texto:match("^([^=]*)(=*)$")
  if not corpo then return nil, "padding no meio do texto" end
  if #pad > 2 then return nil, "padding excessivo" end
  local resto = #corpo % 4
  if resto == 1 then return nil, "tamanho invalido" end
  if #pad > 0 and (#corpo + #pad) % 4 ~= 0 then return nil, "padding incorreto" end
  local saida = {}
  local n, bits = 0, 0
  for i = 1, #corpo do
    local v = dec[corpo:byte(i)]
    if not v then return nil, "caractere invalido: " .. corpo:sub(i, i) end
    n = (n << 6) | v
    bits = bits + 6
    if bits >= 8 then
      bits = bits - 8
      saida[#saida + 1] = string.char((n >> bits) & 0xFF)
      n = n & ((1 << bits) - 1)
    end
  end
  return table.concat(saida)
end

return M

-- Operações de bits sobre inteiros de 64 bits (operadores nativos do Lua 5.3+).
-- Funções com `largura` tratam o valor como inteiro sem sinal de 1 a 64 bits (padrão 32).
local M = {}

local function checar_inteiro(n)
  if math.type(n) ~= "integer" then error("inteiro esperado", 3) end
end

local function checar_largura(l)
  if math.type(l) ~= "integer" or l < 1 or l > 64 then error("largura deve estar entre 1 e 64", 3) end
end

-- Máscara com `largura` bits em 1.
function M.mascara(largura)
  checar_largura(largura)
  return largura == 64 and -1 or (1 << largura) - 1
end

-- Quantidade de bits em 1 (considera os 64 bits).
function M.contar(n)
  checar_inteiro(n)
  local c = 0
  while n ~= 0 do
    n = n & (n - 1)  -- remove o bit mais baixo
    c = c + 1
  end
  return c
end

function M.testar(n, pos)
  checar_inteiro(n)
  if pos < 0 or pos > 63 then error("posicao fora de 0..63", 2) end
  return (n >> pos) & 1 == 1
end

function M.definir(n, pos)
  checar_inteiro(n)
  if pos < 0 or pos > 63 then error("posicao fora de 0..63", 2) end
  return n | (1 << pos)
end

function M.limpar(n, pos)
  checar_inteiro(n)
  if pos < 0 or pos > 63 then error("posicao fora de 0..63", 2) end
  return n & ~(1 << pos)
end

function M.alternar(n, pos)
  checar_inteiro(n)
  if pos < 0 or pos > 63 then error("posicao fora de 0..63", 2) end
  return n ~ (1 << pos)
end

function M.potencia_de_dois(n)
  checar_inteiro(n)
  return n > 0 and n & (n - 1) == 0
end

-- Isola o bit mais baixo em 1 (0 se n == 0).
function M.bit_baixo(n)
  checar_inteiro(n)
  return n & -n
end

function M.paridade(n)
  return M.contar(n) % 2
end

function M.girar_esq(n, k, largura)
  largura = largura or 32
  checar_inteiro(n)
  local m = M.mascara(largura)
  n = n & m
  k = k % largura
  if k == 0 then return n end
  return ((n << k) | (n >> (largura - k))) & m
end

function M.girar_dir(n, k, largura)
  largura = largura or 32
  checar_largura(largura)
  return M.girar_esq(n, largura - (k % largura), largura)
end

-- Inverte os `largura` bits baixos.
function M.inverter(n, largura)
  largura = largura or 32
  checar_inteiro(n)
  return (~n) & M.mascara(largura)
end

-- Representação binária com zeros à esquerda até `largura` dígitos (padrão: mínimo necessário, ao menos 1).
function M.para_binario(n, largura)
  checar_inteiro(n)
  local d = {}
  if n == 0 then d[1] = "0" end
  local v = n
  while v ~= 0 do
    table.insert(d, 1, tostring(v & 1))
    v = v >> 1       -- deslocamento lógico: termina em até 64 passos
  end
  local s = table.concat(d)
  if largura and #s < largura then s = ("0"):rep(largura - #s) .. s end
  return s
end

function M.de_binario(s)
  if type(s) ~= "string" or not s:match("^[01]+$") or #s > 64 then
    return nil, "binario invalido"
  end
  local n = 0
  for i = 1, #s do n = (n << 1) | (s:byte(i) - 48) end
  return n
end

-- Empacota/desempacota inteiros sem sinal de 32 bits em 4 bytes big-endian.
function M.empacotar_u32(n)
  n = n & 0xFFFFFFFF
  return string.char((n >> 24) & 0xFF, (n >> 16) & 0xFF, (n >> 8) & 0xFF, n & 0xFF)
end

function M.desempacotar_u32(s)
  if #s ~= 4 then error("sao necessarios 4 bytes", 2) end
  local a, b, c, d = s:byte(1, 4)
  return (a << 24) | (b << 16) | (c << 8) | d
end

return M

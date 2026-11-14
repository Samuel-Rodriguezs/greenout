-- Helpers de datas sobre os.time/os.date. Cálculos de calendário são independentes de fuso.
local M = {}

function M.bissexto(ano)
  return (ano % 4 == 0 and ano % 100 ~= 0) or ano % 400 == 0
end

local DIAS = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 }

function M.dias_no_mes(ano, mes)
  if mes < 1 or mes > 12 then error("mes invalido: " .. tostring(mes), 2) end
  if mes == 2 and M.bissexto(ano) then return 29 end
  return DIAS[mes]
end

function M.valida(ano, mes, dia)
  return math.type(ano) == "integer" and math.type(mes) == "integer" and math.type(dia) == "integer"
    and mes >= 1 and mes <= 12 and dia >= 1 and dia <= M.dias_no_mes(ano, mes)
end

-- Dias desde 1970-01-01 (algoritmo civil de Howard Hinnant).
function M.dias_desde_epoca(ano, mes, dia)
  if mes <= 2 then ano = ano - 1 end
  local era = ano // 400
  local yoe = ano - era * 400
  local doy = (153 * (mes + (mes > 2 and -3 or 9)) + 2) // 5 + dia - 1
  local doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
  return era * 146097 + doe - 719468
end

-- Diferença em dias (b - a) entre duas datas {ano=,mes=,dia=}.
function M.diferenca_dias(a, b)
  return M.dias_desde_epoca(b.ano, b.mes, b.dia) - M.dias_desde_epoca(a.ano, a.mes, a.dia)
end

-- Dia da semana: 0 = domingo ... 6 = sábado.
function M.dia_da_semana(ano, mes, dia)
  return (M.dias_desde_epoca(ano, mes, dia) + 4) % 7
end

-- Soma `n` dias (pode ser negativo) a uma data; devolve {ano=,mes=,dia=}.
function M.somar_dias(data, n)
  local z = M.dias_desde_epoca(data.ano, data.mes, data.dia) + n + 719468
  local era = z // 146097
  local doe = z - era * 146097
  local yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
  local doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
  local mp = (5 * doy + 2) // 153
  local dia = doy - (153 * mp + 2) // 5 + 1
  local mes = mp + (mp < 10 and 3 or -9)
  local ano = yoe + era * 400 + (mes <= 2 and 1 or 0)
  return { ano = ano, mes = mes, dia = dia }
end

-- Cria timestamp local (os.time); campos fora do intervalo são normalizados.
function M.criar(ano, mes, dia, hora, min, seg)
  return os.time { year = ano, month = mes, day = dia, hour = hora or 12, min = min or 0, sec = seg or 0 }
end

-- Formata com os.date (padrões strftime); `t` padrão é agora.
function M.formatar(t, fmt)
  return os.date(fmt or "%Y-%m-%d %H:%M:%S", t)
end

-- Lê "AAAA-MM-DD" ou "AAAA-MM-DD HH:MM:SS" (aceita 'T'); nil, erro se inválida.
function M.analisar_iso(s)
  local a, m, d, rest = s:match("^(%d%d%d%d)-(%d%d)-(%d%d)(.*)$")
  if not a then return nil, "formato invalido" end
  a, m, d = tonumber(a), tonumber(m), tonumber(d)
  if not M.valida(a, m, d) then return nil, "data inexistente" end
  local h, mi, s2 = 12, 0, 0
  if rest ~= "" then
    local hh, mm, ss = rest:match("^[T ](%d%d):(%d%d):(%d%d)$")
    if not hh then return nil, "formato invalido" end
    h, mi, s2 = tonumber(hh), tonumber(mm), tonumber(ss)
    if h > 23 or mi > 59 or s2 > 59 then return nil, "hora invalida" end
  end
  return M.criar(a, m, d, h, mi, s2)
end

function M.inicio_do_dia(t)
  local d = os.date("*t", t)
  return os.time { year = d.year, month = d.month, day = d.day, hour = 0, min = 0, sec = 0 }
end

-- Idade em anos completos na data de referência.
function M.idade(nasc, ref)
  local n = os.date("*t", nasc)
  local r = os.date("*t", ref)
  local anos = r.year - n.year
  if r.month < n.month or (r.month == n.month and r.day < n.day) then anos = anos - 1 end
  return anos
end

return M

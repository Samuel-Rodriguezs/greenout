local D = require("datas")

-- bissexto
assert(D.bissexto(2024) and not D.bissexto(2023) and not D.bissexto(1900) and D.bissexto(2000))
assert(D.dias_no_mes(2024, 2) == 29 and D.dias_no_mes(2023, 2) == 28 and D.dias_no_mes(2023, 12) == 31)
assert(not pcall(D.dias_no_mes, 2024, 13) and not pcall(D.dias_no_mes, 2024, 0))

-- validação
assert(D.valida(2024, 2, 29) and not D.valida(2023, 2, 29) and not D.valida(2024, 4, 31))
assert(not D.valida(2024, 0, 1) and not D.valida(2024, 1, 0) and not D.valida(2024, 1.5, 1))

-- dias desde a época
assert(D.dias_desde_epoca(1970, 1, 1) == 0 and D.dias_desde_epoca(1970, 1, 2) == 1)
assert(D.dias_desde_epoca(1969, 12, 31) == -1)
assert(D.dias_desde_epoca(2000, 3, 1) == 11017)
assert(D.diferenca_dias({ ano = 2024, mes = 1, dia = 1 }, { ano = 2025, mes = 1, dia = 1 }) == 366)
assert(D.diferenca_dias({ ano = 2024, mes = 3, dia = 1 }, { ano = 2024, mes = 2, dia = 1 }) == -29)
assert(D.diferenca_dias({ ano = 2024, mes = 5, dia = 5 }, { ano = 2024, mes = 5, dia = 5 }) == 0)

-- dia da semana
assert(D.dia_da_semana(1970, 1, 1) == 4)    -- quinta
assert(D.dia_da_semana(2024, 2, 29) == 4)   -- quinta
assert(D.dia_da_semana(2000, 1, 1) == 6)    -- sábado
assert(D.dia_da_semana(2023, 10, 1) == 0)   -- domingo

-- somar dias (viradas de mês, ano e bissexto)
local function s(a, m, d, n)
  local r = D.somar_dias({ ano = a, mes = m, dia = d }, n)
  return string.format("%04d-%02d-%02d", r.ano, r.mes, r.dia)
end
assert(s(2024, 2, 28, 1) == "2024-02-29" and s(2023, 2, 28, 1) == "2023-03-01")
assert(s(2024, 12, 31, 1) == "2025-01-01" and s(2025, 1, 1, -1) == "2024-12-31")
assert(s(2024, 1, 31, 0) == "2024-01-31" and s(2024, 1, 1, 366) == "2025-01-01")
assert(s(2024, 3, 1, -1) == "2024-02-29" and s(1999, 12, 31, 1) == "2000-01-01")

-- criar/formatar (consistentes no fuso local)
local t = D.criar(2024, 7, 4, 15, 30, 45)
assert(D.formatar(t, "%Y-%m-%d %H:%M:%S") == "2024-07-04 15:30:45")
assert(D.formatar(D.criar(2024, 1, 32), "%Y-%m-%d") == "2024-02-01")   -- normalização
assert(D.formatar(D.criar(2024, 7, 4), "%H") == "12")

-- análise ISO
assert(D.formatar(D.analisar_iso("2024-02-29"), "%Y-%m-%d") == "2024-02-29")
assert(D.formatar(D.analisar_iso("2024-02-29T10:20:30"), "%H:%M:%S") == "10:20:30")
assert(D.formatar(D.analisar_iso("2024-02-29 01:02:03"), "%H:%M:%S") == "01:02:03")
local r, e = D.analisar_iso("2023-02-29")
assert(r == nil and e == "data inexistente")
assert(select(2, D.analisar_iso("hoje")) == "formato invalido")
assert(select(2, D.analisar_iso("2024-01-01 25:00:00")) == "hora invalida")
assert(select(2, D.analisar_iso("2024-01-01X")) == "formato invalido")

-- início do dia e idade
assert(D.formatar(D.inicio_do_dia(t), "%H:%M:%S") == "00:00:00")
assert(D.idade(D.criar(2000, 6, 15), D.criar(2024, 6, 14)) == 23)
assert(D.idade(D.criar(2000, 6, 15), D.criar(2024, 6, 15)) == 24)
assert(D.idade(D.criar(2000, 6, 15), D.criar(2000, 6, 15)) == 0)
print("ok")

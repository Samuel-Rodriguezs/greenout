"""Parcelamento com arredondamento: o resto de centavos vai para a primeira ou última parcela."""
from __future__ import annotations

import calendar
from datetime import date
from decimal import Decimal


def parcelar(total: object, n: int, resto_na_primeira: bool = True,
             entrada: object = 0) -> list[Decimal]:
    """Divide (total - entrada) em `n` parcelas; a soma + entrada = total.

    Retorna as `n` parcelas (a entrada não entra na lista).
    """
    if n <= 0:
        raise ValueError("número de parcelas deve ser positivo")
    t = Decimal(str(total)) - Decimal(str(entrada))
    if t < 0:
        raise ValueError("entrada maior que o total")
    centavos = t * 100
    if centavos != centavos.to_integral_value():
        raise ValueError("valores devem ter no máximo 2 casas decimais")
    base, resto = divmod(int(centavos), n)
    partes = [base] * n
    if resto_na_primeira:
        partes[0] += resto
    else:
        partes[-1] += resto
    return [Decimal(p) / 100 for p in partes]


def vencimentos(primeiro: date, n: int) -> list[date]:
    """Vencimentos mensais mantendo o dia (ajustado ao último dia do mês quando preciso)."""
    if n <= 0:
        raise ValueError("número de parcelas deve ser positivo")
    datas = []
    for k in range(n):
        indice = primeiro.year * 12 + primeiro.month - 1 + k
        ano, mes0 = divmod(indice, 12)
        mes = mes0 + 1
        datas.append(date(ano, mes, min(primeiro.day, calendar.monthrange(ano, mes)[1])))
    return datas

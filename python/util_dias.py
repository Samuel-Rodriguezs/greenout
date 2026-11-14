from datetime import date, datetime, timedelta


def _como_data(valor: date | datetime | str) -> date:
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if isinstance(valor, str):
        return date.fromisoformat(valor)
    raise TypeError("esperado date, datetime ou string AAAA-MM-DD")


def diferenca_em_dias(inicio, fim) -> int:
    """Dias entre duas datas (negativo se fim for anterior a inicio)."""
    return (_como_data(fim) - _como_data(inicio)).days


def dias_uteis_entre(inicio, fim) -> int:
    """Conta dias úteis (seg-sex) em [inicio, fim), sem considerar feriados."""
    a, b = _como_data(inicio), _como_data(fim)
    if b < a:
        raise ValueError("fim deve ser posterior ou igual a inicio")
    total = 0
    atual = a
    while atual < b:
        if atual.weekday() < 5:
            total += 1
        atual += timedelta(days=1)
    return total


def eh_bissexto(ano: int) -> bool:
    return ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0)

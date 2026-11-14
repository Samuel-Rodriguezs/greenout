"""Números e valores em reais por extenso, em português do Brasil."""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

_UNIDADES = (
    "zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez",
    "onze", "doze", "treze", "catorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove",
)
_DEZENAS = ("", "", "vinte", "trinta", "quarenta", "cinquenta", "sessenta", "setenta", "oitenta", "noventa")
_CENTENAS = (
    "", "cento", "duzentos", "trezentos", "quatrocentos", "quinhentos",
    "seiscentos", "setecentos", "oitocentos", "novecentos",
)
# (singular, plural) para 10^3, 10^6, 10^9, 10^12
_ESCALAS = (("mil", "mil"), ("milhão", "milhões"), ("bilhão", "bilhões"), ("trilhão", "trilhões"))
LIMITE = 10**15


def _feminino(texto: str) -> str:
    texto = texto.replace("duzentos", "duzentas").replace("trezentos", "trezentas")
    texto = texto.replace("quatrocentos", "quatrocentas").replace("quinhentos", "quinhentas")
    texto = texto.replace("seiscentos", "seiscentas").replace("setecentos", "setecentas")
    texto = texto.replace("oitocentos", "oitocentas").replace("novecentos", "novecentas")
    palavras = texto.split(" ")
    # "um" -> "uma" e "dois" -> "duas" apenas como palavras inteiras
    return " ".join({"um": "uma", "dois": "duas"}.get(p, p) for p in palavras)


def _grupo(n: int) -> str:
    """Texto de 1 a 999."""
    if n == 100:
        return "cem"
    partes: list[str] = []
    c, resto = divmod(n, 100)
    if c:
        partes.append(_CENTENAS[c])
    if resto:
        if resto < 20:
            partes.append(_UNIDADES[resto])
        else:
            d, u = divmod(resto, 10)
            partes.append(_DEZENAS[d])
            if u:
                partes.append(_UNIDADES[u])
    return " e ".join(partes)


def numero_por_extenso(n: int, feminino: bool = False) -> str:
    """Ex.: 1234 -> 'mil duzentos e trinta e quatro'. Aceita |n| < 10^15."""
    if abs(n) >= LIMITE:
        raise ValueError("número grande demais (limite: menos de 10^15)")
    if n < 0:
        return "menos " + numero_por_extenso(-n, feminino)
    if n == 0:
        return "zero"
    grupos: list[int] = []
    resto = n
    while resto:
        resto, g = divmod(resto, 1000)
        grupos.append(g)
    partes: list[str] = []
    valores: list[int] = []
    for indice in range(len(grupos) - 1, -1, -1):
        g = grupos[indice]
        if g == 0:
            continue
        if indice == 0:
            texto = _grupo(g)
            if feminino:
                texto = _feminino(texto)
        elif indice == 1:
            texto = "mil" if g == 1 else f"{_feminino(_grupo(g)) if feminino else _grupo(g)} mil"
        else:
            singular, plural = _ESCALAS[indice - 1]
            texto = f"{_grupo(g)} {singular if g == 1 else plural}"
        partes.append(texto)
        valores.append(g)
    if len(partes) == 1:
        return partes[0]
    ultimo = valores[-1]
    if ultimo < 100 or ultimo % 100 == 0:
        return " ".join(partes[:-1]) + " e " + partes[-1]
    return " ".join(partes)


def reais_por_extenso(valor: Decimal | int | float | str) -> str:
    """Ex.: 1.5 -> 'um real e cinquenta centavos'; 1_000_000 -> 'um milhão de reais'."""
    dec = valor if isinstance(valor, Decimal) else Decimal(str(valor))
    centavos_total = int((dec * 100).quantize(Decimal(1), rounding=ROUND_HALF_UP))
    if centavos_total < 0:
        return "menos " + reais_por_extenso(Decimal(-centavos_total) / 100)
    reais, centavos = divmod(centavos_total, 100)
    partes: list[str] = []
    if reais or not centavos:
        texto = numero_por_extenso(reais)
        if reais >= 10**6 and reais % 10**6 == 0:
            texto += " de"
        partes.append(f"{texto} {'real' if reais == 1 else 'reais'}")
    if centavos:
        partes.append(f"{numero_por_extenso(centavos)} {'centavo' if centavos == 1 else 'centavos'}")
    return " e ".join(partes)

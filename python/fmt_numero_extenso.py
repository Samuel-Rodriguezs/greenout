"""Números por extenso em pt-BR: texto -> inteiro e inteiro -> texto."""
from __future__ import annotations

import unicodedata


class ErroNumero(ValueError):
    """Número por extenso inválido."""


_UNID = ["zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez", "onze",
         "doze", "treze", "quatorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove"]
_DEZ = {2: "vinte", 3: "trinta", 4: "quarenta", 5: "cinquenta", 6: "sessenta", 7: "setenta", 8: "oitenta",
        9: "noventa"}
_CEN = {1: "cento", 2: "duzentos", 3: "trezentos", 4: "quatrocentos", 5: "quinhentos", 6: "seiscentos",
        7: "setecentos", 8: "oitocentos", 9: "novecentos"}
_ESCALAS = [(10**12, "trilhão", "trilhões"), (10**9, "bilhão", "bilhões"), (10**6, "milhão", "milhões"),
            (10**3, "mil", "mil")]


def _sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if not unicodedata.combining(c))


def _grupo(n: int) -> str:
    """Escreve 1..999."""
    if n == 100:
        return "cem"
    partes: list[str] = []
    c, resto = divmod(n, 100)
    if c:
        partes.append(_CEN[c])
    if resto:
        if resto < 20:
            partes.append(_UNID[resto])
        else:
            d, u = divmod(resto, 10)
            partes.append(_DEZ[d])
            if u:
                partes.append(_UNID[u])
    return " e ".join(partes)


def para_extenso(n: int) -> str:
    """Converte um inteiro (|n| < 10**15) em texto por extenso."""
    if not isinstance(n, int) or isinstance(n, bool):
        raise ErroNumero("esperado um inteiro")
    if abs(n) >= 10**15:
        raise ErroNumero("número grande demais")
    if n < 0:
        return "menos " + para_extenso(-n)
    if n == 0:
        return "zero"
    partes: list[tuple[int, str]] = []
    for valor, sing, plur in _ESCALAS:
        q, n = divmod(n, valor)
        if not q:
            continue
        if valor == 1000:
            texto = "mil" if q == 1 else f"{_grupo(q)} mil"
        else:
            texto = f"{_grupo(q)} {sing if q == 1 else plur}"
        partes.append((q, texto))
    if n:
        partes.append((n, _grupo(n)))
    # "e" liga o último bloco quando ele é < 100 ou múltiplo de 100
    saida = partes[0][1]
    for i in range(1, len(partes)):
        q, texto = partes[i]
        ultimo = i == len(partes) - 1
        saida += (" e " if ultimo and (q < 100 or q % 100 == 0) else " ") + texto
    return saida


_PALAVRAS: dict[str, tuple[str, int]] = {}
for _i, _p in enumerate(_UNID):
    _PALAVRAS[_sem_acento(_p)] = ("u", _i)
_PALAVRAS["duas"] = ("u", 2)
_PALAVRAS["catorze"] = ("u", 14)
_PALAVRAS["dezasseis"] = ("u", 16)
_PALAVRAS["dezassete"] = ("u", 17)
for _k, _p in _DEZ.items():
    _PALAVRAS[_p] = ("d", _k * 10)
for _k, _p in _CEN.items():
    _PALAVRAS[_p] = ("c", _k * 100)
_PALAVRAS["cem"] = ("c", 100)
_PALAVRAS["duzentas"] = ("c", 200)
_PALAVRAS["trezentas"] = ("c", 300)
_ESC = {"mil": 10**3, "milhao": 10**6, "milhoes": 10**6, "bilhao": 10**9, "bilhoes": 10**9,
        "trilhao": 10**12, "trilhoes": 10**12}


def de_extenso(texto: str) -> int:
    """Converte 'mil duzentos e trinta e quatro' em 1234."""
    tokens = [t for t in _sem_acento(texto).replace("-", " ").split() if t]
    if not tokens:
        raise ErroNumero("texto vazio")
    negativo = tokens[0] in ("menos", "negativo")
    if negativo:
        tokens = tokens[1:]
        if not tokens:
            raise ErroNumero("faltou o número após 'menos'")
    total = 0
    grupo = 0
    estado = 0  # 0 nada, 1 centena, 2 dezena (20-90), 3 unidade/teen (fim do grupo)
    escala_anterior = 10**15
    esperando_numero = False  # após um "e"
    tinha_grupo = False
    for tok in tokens:
        if tok == "e":
            if esperando_numero or not (tinha_grupo or grupo or total):
                raise ErroNumero("'e' mal posicionado")
            esperando_numero = True
            continue
        if tok in _ESC:
            valor = _ESC[tok]
            if valor >= escala_anterior:
                raise ErroNumero(f"escalas fora de ordem em {tok!r}")
            if esperando_numero:
                raise ErroNumero("'e' antes de escala")
            if not tinha_grupo:
                if valor == 1000 and grupo == 0:
                    grupo = 1  # "mil" sozinho
                elif grupo == 0:
                    raise ErroNumero(f"escala {tok!r} sem quantidade")
            if valor != 1000 and grupo == 1 and tok.endswith("oes"):
                raise ErroNumero(f"plural incorreto: {tok!r}")
            if valor != 1000 and grupo > 1 and tok.endswith("ao"):
                raise ErroNumero(f"singular incorreto: {tok!r}")
            total += grupo * valor
            grupo, estado, escala_anterior, tinha_grupo = 0, 0, valor, False
            continue
        if tok not in _PALAVRAS:
            raise ErroNumero(f"palavra desconhecida: {tok!r}")
        tipo, valor = _PALAVRAS[tok]
        esperando_numero = False
        if tipo == "c":
            if estado != 0:
                raise ErroNumero(f"ordem inválida em {tok!r}")
            grupo += valor
            estado = 1 if tok != "cem" else 3
        elif tipo == "d":
            if estado > 1:
                raise ErroNumero(f"ordem inválida em {tok!r}")
            grupo += valor
            estado = 2
        else:
            if tok == "zero":
                if len(tokens) != 1 and not (len(tokens) == 2 and negativo):
                    raise ErroNumero("'zero' só pode aparecer sozinho")
                return 0
            if estado == 3 or (estado == 2 and valor >= 10):
                raise ErroNumero(f"ordem inválida em {tok!r}")
            grupo += valor
            estado = 3
        tinha_grupo = True
    if esperando_numero:
        raise ErroNumero("texto termina em 'e'")
    total += grupo
    return -total if negativo else total

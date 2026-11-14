"""Soundex adaptado para o português brasileiro (codificação fonética simples)."""
import re
import unicodedata

_DIGRAFOS = [("CH", "X"), ("LH", "L"), ("NH", "N"), ("QU", "K"), ("PH", "F"), ("TH", "T"), ("SS", "S")]
_CODIGOS = {}
for _letras, _cod in (("BFPV", "1"), ("CGJKQSXZ", "2"), ("DT", "3"), ("L", "4"), ("MN", "5"), ("R", "6")):
    for _l in _letras:
        _CODIGOS[_l] = _cod


def _limpar(palavra: str) -> str:
    base = unicodedata.normalize("NFD", palavra.upper())
    base = "".join(c for c in base if not unicodedata.combining(c))
    return re.sub(r"[^A-Z]", "", base)


def soundex(palavra: str) -> str:
    """Retorna o código de 4 caracteres (letra + 3 dígitos); '' se não houver letras."""
    s = _limpar(palavra)
    for de, para in _DIGRAFOS:
        s = s.replace(de, para)
    if not s:
        return ""
    saida = s[0]
    anterior = _CODIGOS.get(s[0])
    for c in s[1:]:
        cod = _CODIGOS.get(c)
        if cod:
            if cod != anterior:
                saida += cod
            anterior = cod
        elif c not in "HW":
            anterior = None
    return (saida + "000")[:4]


def soam_igual(a: str, b: str) -> bool:
    ca, cb = soundex(a), soundex(b)
    return ca != "" and ca == cb

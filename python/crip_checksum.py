"""Verificadores de dígito: Luhn, ISBN-10, ISBN-13 e IBAN (mod 97)."""
from __future__ import annotations


def luhn_valido(numero: str) -> bool:
    s = numero.replace(" ", "").replace("-", "")
    if len(s) < 2 or not s.isascii() or not s.isdigit():
        return False
    return _luhn_soma(s) % 10 == 0


def _luhn_soma(s: str) -> int:
    total = 0
    for i, c in enumerate(reversed(s)):
        d = int(c)
        if i % 2:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total


def luhn_digito(corpo: str) -> int:
    """Dígito de verificação a anexar a `corpo`."""
    if not corpo.isascii() or not corpo.isdigit():
        raise ValueError("corpo deve ser numérico")
    return (10 - _luhn_soma(corpo + "0") % 10) % 10


def isbn10_valido(isbn: str) -> bool:
    s = isbn.replace("-", "").replace(" ", "").upper()
    if len(s) != 10 or not s[:9].isdigit() or not (s[9].isdigit() or s[9] == "X"):
        return False
    total = sum((10 - i) * (10 if c == "X" else int(c)) for i, c in enumerate(s))
    return total % 11 == 0


def isbn13_valido(isbn: str) -> bool:
    s = isbn.replace("-", "").replace(" ", "")
    if len(s) != 13 or not s.isascii() or not s.isdigit():
        return False
    return sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(s)) % 10 == 0


def isbn10_para_13(isbn: str) -> str:
    s = isbn.replace("-", "").replace(" ", "").upper()
    if not isbn10_valido(s):
        raise ValueError("ISBN-10 inválido")
    corpo = "978" + s[:9]
    d = (10 - sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(corpo)) % 10) % 10
    return corpo + str(d)


def iban_valido(iban: str) -> bool:
    s = iban.replace(" ", "").upper()
    if not 15 <= len(s) <= 34 or not s.isascii() or not s.isalnum():
        return False
    if not (s[:2].isalpha() and s[2:4].isdigit()):
        return False
    rearranjado = s[4:] + s[:4]
    numerico = "".join(str(int(c, 36)) for c in rearranjado)
    return int(numerico) % 97 == 1


def iban_digitos_controle(pais: str, bban: str) -> str:
    """Calcula os 2 dígitos de controle de um IBAN."""
    s = (bban.replace(" ", "") + pais + "00").upper()
    n = int("".join(str(int(c, 36)) for c in s))
    return f"{98 - n % 97:02d}"

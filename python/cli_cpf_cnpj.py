"""Validador de CPF e CNPJ em linha de comando."""
import argparse
import re
import sys
from typing import Optional, Sequence


def _digito(base: str, pesos: Sequence[int]) -> int:
    resto = sum(int(d) * p for d, p in zip(base, pesos)) % 11
    return 0 if resto < 2 else 11 - resto


def validar_cpf(texto: str) -> bool:
    d = re.sub(r"\D", "", texto)
    if len(d) != 11 or d == d[0] * 11:
        return False
    d1 = _digito(d[:9], range(10, 1, -1))
    d2 = _digito(d[:10], range(11, 1, -1))
    return d[9:] == f"{d1}{d2}"


def validar_cnpj(texto: str) -> bool:
    d = re.sub(r"\D", "", texto)
    if len(d) != 14 or d == d[0] * 14:
        return False
    p1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    p2 = [6] + p1
    d1 = _digito(d[:12], p1)
    d2 = _digito(d[:13], p2)
    return d[12:] == f"{d1}{d2}"


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Valida CPF (11 dígitos) ou CNPJ (14 dígitos).")
    p.add_argument("documentos", nargs="+")
    a = p.parse_args(argv)
    todos_validos = True
    for doc in a.documentos:
        n = len(re.sub(r"\D", "", doc))
        if n == 11:
            tipo, ok = "CPF", validar_cpf(doc)
        elif n == 14:
            tipo, ok = "CNPJ", validar_cnpj(doc)
        else:
            tipo, ok = "?", False
        todos_validos &= ok
        print(f"{doc}: {tipo} {'válido' if ok else 'inválido'}")
    return 0 if todos_validos else 1


if __name__ == "__main__":
    sys.exit(main())

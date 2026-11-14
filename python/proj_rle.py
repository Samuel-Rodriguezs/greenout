"""Compressor RLE: formato textual '<contagem><caractere>' (ex.: 3a2b1c)."""
import re


def comprimir(texto: str) -> str:
    if any(c.isdigit() for c in texto):
        raise ValueError("texto nao pode conter digitos")
    partes = []
    i = 0
    while i < len(texto):
        j = i
        while j < len(texto) and texto[j] == texto[i]:
            j += 1
        partes.append(f"{j - i}{texto[i]}")
        i = j
    return "".join(partes)


def descomprimir(codigo: str) -> str:
    if not re.fullmatch(r"(\d+\D)*", codigo, flags=re.DOTALL):
        raise ValueError("codigo RLE invalido")
    return "".join(c * int(n) for n, c in re.findall(r"(\d+)(\D)", codigo, flags=re.DOTALL))


def taxa_compressao(texto: str) -> float:
    if not texto:
        raise ValueError("texto vazio")
    return len(comprimir(texto)) / len(texto)

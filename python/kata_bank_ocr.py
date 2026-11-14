"""Bank OCR Kata: leitura de números de conta em dígitos ASCII de 3x3."""
from __future__ import annotations

_DIGITOS = {
    " _ | ||_|": "0",
    "     |  |": "1",
    " _  _||_ ": "2",
    " _  _| _|": "3",
    "   |_|  |": "4",
    " _ |_  _|": "5",
    " _ |_ |_|": "6",
    " _   |  |": "7",
    " _ |_||_|": "8",
    " _ |_| _|": "9",
}


def ler_conta(linhas: list[str]) -> str:
    """Lê 3 linhas de 27 colunas e devolve a conta ('?' em dígitos ilegíveis)."""
    if len(linhas) != 3 or any(len(l) != 27 for l in linhas):
        raise ValueError("entrada deve ter 3 linhas de 27 caracteres")
    conta = []
    for i in range(9):
        bloco = "".join(l[i * 3:i * 3 + 3] for l in linhas)
        conta.append(_DIGITOS.get(bloco, "?"))
    return "".join(conta)


def checksum_valido(conta: str) -> bool:
    """(d1*9 + d2*8 + ... + d9*1) mod 11 == 0."""
    if len(conta) != 9 or not conta.isdigit():
        return False
    return sum(int(d) * (9 - i) for i, d in enumerate(conta)) % 11 == 0


def classificar(conta: str) -> str:
    """Sufixa 'ILL' para ilegível, 'ERR' para checksum inválido."""
    if "?" in conta:
        return f"{conta} ILL"
    if not checksum_valido(conta):
        return f"{conta} ERR"
    return conta


def renderizar(conta: str) -> list[str]:
    """Inverso de ler_conta: gera as 3 linhas para dígitos válidos."""
    inverso = {v: k for k, v in _DIGITOS.items()}
    if not conta.isdigit():
        raise ValueError("apenas dígitos")
    blocos = [inverso[d] for d in conta]
    return ["".join(b[r * 3:r * 3 + 3] for b in blocos) for r in range(3)]

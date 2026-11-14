"""Máscaras e formatadores: CPF, CNPJ, telefone e CEP (apenas formatação, sem validar dígitos)."""
from __future__ import annotations

import re


def so_digitos(texto: str) -> str:
    return re.sub(r"\D", "", texto)


def _exigir(texto: str, tamanhos: tuple[int, ...], nome: str) -> str:
    d = so_digitos(texto)
    if len(d) not in tamanhos:
        raise ValueError(f"{nome} precisa de {' ou '.join(map(str, tamanhos))} dígitos, recebeu {len(d)}")
    return d


def mascarar_cpf(texto: str) -> str:
    d = _exigir(texto, (11,), "CPF")
    return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"


def mascarar_cnpj(texto: str) -> str:
    d = _exigir(texto, (14,), "CNPJ")
    return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"


def mascarar_cep(texto: str) -> str:
    d = _exigir(texto, (8,), "CEP")
    return f"{d[:5]}-{d[5:]}"


def mascarar_telefone(texto: str) -> str:
    """(11) 91234-5678, (11) 1234-5678 ou, com DDI 55, +55 (11) 91234-5678."""
    d = so_digitos(texto)
    ddi = ""
    if len(d) in (12, 13) and d.startswith("55"):
        ddi, d = "+55 ", d[2:]
    if len(d) not in (10, 11):
        raise ValueError("telefone precisa de 10 ou 11 dígitos (DDD + número)")
    if d[0] == "0" or d[1] == "0":
        raise ValueError("DDD inválido")
    corte = len(d) - 4
    return f"{ddi}({d[:2]}) {d[2:corte]}-{d[corte:]}"


def mascarar_documento(texto: str) -> str:
    """Escolhe CPF ou CNPJ pelo número de dígitos."""
    return mascarar_cpf(texto) if len(so_digitos(texto)) == 11 else mascarar_cnpj(texto)


def ocultar_cpf(texto: str) -> str:
    """Mascara o CPF escondendo o miolo: ***.456.789-**."""
    d = _exigir(texto, (11,), "CPF")
    return f"***.{d[3:6]}.{d[6:9]}-**"

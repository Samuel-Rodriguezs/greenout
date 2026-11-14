"""Normalização de acentos e texto com unicodedata."""
import re
import unicodedata


def remover_acentos(texto: str) -> str:
    decomposto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in decomposto if not unicodedata.combining(c))


def normalizar(texto: str) -> str:
    """Minúsculas, sem acentos e com espaços colapsados."""
    return re.sub(r"\s+", " ", remover_acentos(texto).lower()).strip()


def slugificar(texto: str) -> str:
    """Gera slug ASCII separado por hífens (ex.: 'Ação Rápida!' -> 'acao-rapida')."""
    base = normalizar(texto)
    return re.sub(r"[^a-z0-9]+", "-", base).strip("-")


def iguais_sem_acento(a: str, b: str) -> bool:
    return normalizar(a) == normalizar(b)


def tem_acentos(texto: str) -> bool:
    return remover_acentos(texto) != unicodedata.normalize("NFD", texto) or any(
        unicodedata.combining(c) for c in unicodedata.normalize("NFD", texto)
    )

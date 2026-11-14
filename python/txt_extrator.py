"""Extração de e-mails, telefones brasileiros e CEPs com regex."""
import re

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_TELEFONE = re.compile(
    r"(?<![\d-])(?:(?:\+55\s?)?\(?\d{2}\)?\s?9?\d{4}[-\s]?\d{4}|9?\d{4}[-\s]\d{4})(?!\d)"
)
_CEP = re.compile(r"(?<!\d)\d{5}-?\d{3}(?!\d)")


def extrair_emails(texto: str) -> list[str]:
    return _EMAIL.findall(texto)


def extrair_telefones(texto: str) -> list[str]:
    return [m.group(0).strip() for m in _TELEFONE.finditer(texto)]


def extrair_ceps(texto: str) -> list[str]:
    return _CEP.findall(texto)


def extrair_tudo(texto: str) -> dict[str, list[str]]:
    return {
        "emails": extrair_emails(texto),
        "telefones": extrair_telefones(texto),
        "ceps": extrair_ceps(texto),
    }


def apenas_digitos(valor: str) -> str:
    return re.sub(r"\D", "", valor)

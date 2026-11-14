"""Conversão entre camelCase e snake_case."""

import re


def camel_para_snake(nome: str) -> str:
    """Converte camelCase/PascalCase para snake_case (ex.: 'parseHTTPResponse' -> 'parse_http_response')."""
    nome = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", nome)
    nome = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", nome)
    return nome.lower()


def snake_para_camel(nome: str) -> str:
    """Converte snake_case para camelCase, ignorando underscores nas pontas ou repetidos."""
    partes = [p for p in nome.split("_") if p]
    if not partes:
        return ""
    return partes[0].lower() + "".join(p.capitalize() for p in partes[1:])

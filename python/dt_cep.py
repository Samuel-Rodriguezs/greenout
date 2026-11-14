"""Validação de formato, normalização e região postal de CEP brasileiro."""
from __future__ import annotations

import re

_REGIOES = {
    "0": "Grande São Paulo",
    "1": "Interior e litoral de São Paulo",
    "2": "Rio de Janeiro e Espírito Santo",
    "3": "Minas Gerais",
    "4": "Bahia e Sergipe",
    "5": "Pernambuco, Alagoas, Paraíba e Rio Grande do Norte",
    "6": "Ceará, Piauí, Maranhão, Pará, Amazonas, Amapá, Acre e Roraima",
    "7": "Distrito Federal, Goiás, Tocantins, Mato Grosso, Mato Grosso do Sul e Rondônia",
    "8": "Paraná e Santa Catarina",
    "9": "Rio Grande do Sul",
}

_FORMATO = re.compile(r"^(\d{5})-?(\d{3})$")


def normalizar_cep(cep: str) -> str:
    """Retorna os 8 dígitos do CEP (aceita 12345-678 ou 12345678)."""
    casou = _FORMATO.match(cep.strip())
    if casou is None:
        raise ValueError(f"CEP inválido: {cep!r}")
    return casou.group(1) + casou.group(2)


def validar_cep(cep: str) -> bool:
    """Formato válido e diferente de 00000-000."""
    try:
        return normalizar_cep(cep) != "00000000"
    except ValueError:
        return False


def formatar_cep(cep: str) -> str:
    n = normalizar_cep(cep)
    return f"{n[:5]}-{n[5:]}"


def regiao_postal(cep: str) -> str:
    """Região postal indicada pelo primeiro dígito."""
    n = normalizar_cep(cep)
    return _REGIOES[n[0]]


def eh_cep_unico(cep: str) -> bool:
    """CEPs terminados em -000 identificam a localidade/município (CEP único)."""
    return normalizar_cep(cep).endswith("000")

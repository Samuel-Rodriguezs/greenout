import re


def _digito(digitos: str, peso_inicial: int) -> int:
    soma = sum(int(d) * p for d, p in zip(digitos, range(peso_inicial, 1, -1)))
    resto = (soma * 10) % 11
    return 0 if resto == 10 else resto


def validar_cpf(cpf: str) -> bool:
    """Valida um CPF (com ou sem pontuação) pelos dígitos verificadores."""
    if not isinstance(cpf, str):
        return False
    if re.search(r"[^\d.\-]", cpf):
        return False
    numeros = re.sub(r"\D", "", cpf)
    if len(numeros) != 11 or numeros == numeros[0] * 11:
        return False
    d1 = _digito(numeros[:9], 10)
    d2 = _digito(numeros[:9] + str(d1), 11)
    return numeros[9:] == f"{d1}{d2}"


def formatar_cpf(cpf: str) -> str:
    """Formata 11 dígitos como 000.000.000-00."""
    numeros = re.sub(r"\D", "", cpf)
    if len(numeros) != 11:
        raise ValueError("CPF deve ter 11 dígitos")
    return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"

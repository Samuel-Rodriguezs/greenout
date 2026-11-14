"""Números perfeitos: iguais à soma de seus divisores próprios."""


def eh_perfeito(n: int) -> bool:
    """Retorna True se n é perfeito; 1 e números não positivos não são."""
    if n < 2:
        return False
    soma = 1
    i = 2
    while i * i <= n:
        if n % i == 0:
            soma += i
            if i != n // i:
                soma += n // i
        i += 1
    return soma == n


def perfeitos_ate(limite: int) -> list[int]:
    """Lista os números perfeitos de 1 até limite (inclusive)."""
    return [n for n in range(2, limite + 1) if eh_perfeito(n)]

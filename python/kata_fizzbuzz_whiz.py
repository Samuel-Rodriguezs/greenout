"""FizzBuzzWhiz Kata: FizzBuzz com regras configuráveis.

Regras suportadas:
- Divisibilidade: palavra se n % divisor == 0.
- Dígito: palavra se o dígito aparece em n (tem precedência sobre divisibilidade
  quando `prioridade_digito=True`, como na variante clássica "Fizz se contém 3").
"""
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(frozen=True)
class Regra:
    palavra: str
    divisor: int | None = None
    digito: int | None = None

    def __post_init__(self) -> None:
        if (self.divisor is None) == (self.digito is None):
            raise ValueError("informe exatamente um entre divisor e digito")
        if self.divisor is not None and self.divisor < 1:
            raise ValueError("divisor deve ser >= 1")
        if self.digito is not None and not 0 <= self.digito <= 9:
            raise ValueError("digito deve estar entre 0 e 9")
        if not self.palavra:
            raise ValueError("palavra não pode ser vazia")

    def aplica(self, n: int) -> bool:
        if self.divisor is not None:
            return n % self.divisor == 0
        return str(self.digito) in str(abs(n))


REGRAS_CLASSICAS = (Regra("Fizz", divisor=3), Regra("Buzz", divisor=5))
REGRAS_WHIZ = REGRAS_CLASSICAS + (Regra("Whiz", divisor=7),)


def converter(n: int, regras: tuple[Regra, ...] = REGRAS_CLASSICAS,
              prioridade_digito: bool = False) -> str:
    if prioridade_digito:
        por_digito = [r.palavra for r in regras if r.digito is not None and r.aplica(n)]
        if por_digito:
            return "".join(por_digito)
    palavras = [r.palavra for r in regras if r.aplica(n)]
    return "".join(palavras) or str(n)


def gerar(inicio: int, fim: int, regras: tuple[Regra, ...] = REGRAS_CLASSICAS,
          prioridade_digito: bool = False) -> Iterator[str]:
    """Converte inclusive de inicio até fim."""
    for n in range(inicio, fim + 1):
        yield converter(n, regras, prioridade_digito)

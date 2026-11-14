"""IDs sortáveis no estilo ULID (48 bits de tempo + 80 de aleatoriedade, Crockford base32), relógio injetável."""
from __future__ import annotations

import random
from typing import Callable

ALFABETO = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"  # Crockford: sem I, L, O, U
_VALOR = {c: i for i, c in enumerate(ALFABETO)}
MAX_TEMPO = (1 << 48) - 1
MAX_ALEATORIO = (1 << 80) - 1


def codificar(valor: int, tamanho: int) -> str:
    if valor < 0 or valor >= 32 ** tamanho:
        raise ValueError("valor fora do intervalo para o tamanho dado")
    chars = []
    for _ in range(tamanho):
        valor, r = divmod(valor, 32)
        chars.append(ALFABETO[r])
    return "".join(reversed(chars))


def decodificar(texto: str) -> int:
    v = 0
    for c in texto.upper():
        if c not in _VALOR:
            raise ValueError(f"caractere inválido: {c!r}")
        v = v * 32 + _VALOR[c]
    return v


class GeradorUlid:
    """Gera IDs de 26 caracteres, estritamente crescentes mesmo dentro do mesmo milissegundo.

    `relogio` devolve milissegundos desde a época; `rng` fornece os 80 bits aleatórios."""

    def __init__(self, rng: random.Random, relogio: Callable[[], int]) -> None:
        self._rng = rng
        self._relogio = relogio
        self._ultimo_tempo = -1
        self._ultimo_aleatorio = 0

    def proximo(self) -> str:
        agora = self._relogio()
        if not 0 <= agora <= MAX_TEMPO:
            raise ValueError("tempo fora de 48 bits")
        if agora > self._ultimo_tempo:
            self._ultimo_tempo = agora
            self._ultimo_aleatorio = self._rng.getrandbits(80)
        else:
            # mesmo ms (ou relógio recuou): mantém o último tempo e incrementa a parte aleatória
            if self._ultimo_aleatorio >= MAX_ALEATORIO:
                raise OverflowError("parte aleatória esgotada neste milissegundo")
            self._ultimo_aleatorio += 1
        return codificar(self._ultimo_tempo, 10) + codificar(self._ultimo_aleatorio, 16)


def tempo_do_ulid(ulid: str) -> int:
    if len(ulid) != 26:
        raise ValueError("ULID deve ter 26 caracteres")
    return decodificar(ulid[:10])

"""Transações bancárias fictícias com saldo coerente (valores em centavos, saldo nunca negativo)."""
from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta

TIPOS: tuple[str, ...] = ("deposito", "saque", "pix_enviado", "pix_recebido", "tarifa", "compra_debito")
CREDITOS: frozenset[str] = frozenset({"deposito", "pix_recebido"})


@dataclass(frozen=True)
class Transacao:
    sequencia: int
    quando: datetime
    tipo: str
    valor: int  # sempre positivo; o sinal vem do tipo
    saldo_apos: int

    @property
    def delta(self) -> int:
        return self.valor if self.tipo in CREDITOS else -self.valor


def gerar_extrato(
    seed: int, n: int, inicio: datetime, saldo_inicial: int = 100_000
) -> list[Transacao]:
    """Extrato cronológico; débitos são limitados ao saldo disponível."""
    if saldo_inicial < 0:
        raise ValueError("saldo inicial não pode ser negativo")
    rng = random.Random(seed)
    saldo = saldo_inicial
    t = inicio
    saida: list[Transacao] = []
    for seq in range(1, n + 1):
        t += timedelta(minutes=rng.randint(1, 60 * 24))
        tipo = rng.choice(TIPOS)
        valor = max(1, round(rng.lognormvariate(5.0, 1.0)))  # mediana ~ R$ 1,48 * 100
        if tipo == "tarifa":
            valor = rng.choice((990, 1290))
        if tipo not in CREDITOS and valor > saldo:
            if saldo == 0:
                tipo = "deposito"
                valor = rng.randint(1000, 50_000)
            else:
                valor = rng.randint(1, saldo)
        saldo += valor if tipo in CREDITOS else -valor
        saida.append(Transacao(seq, t, tipo, valor, saldo))
    return saida


def conferir_extrato(extrato: list[Transacao], saldo_inicial: int) -> bool:
    """True se cada saldo_apos é o anterior mais o delta e nenhum saldo é negativo."""
    saldo = saldo_inicial
    for tx in extrato:
        saldo += tx.delta
        if saldo != tx.saldo_apos or saldo < 0:
            return False
    return True

"""Recibos de pagamento e conciliação com o extrato bancário."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal


@dataclass(frozen=True)
class Recibo:
    numero: int
    cliente_id: int
    valor: Decimal
    data: date
    referencia: str

    def texto(self, nome_cliente: str) -> str:
        v = f"{self.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return (f"RECIBO Nº {self.numero:06d}\nRecebemos de {nome_cliente} a quantia de R$ {v}, "
                f"referente a {self.referencia}, em {self.data.strftime('%d/%m/%Y')}.")


class EmissorRecibos:
    def __init__(self, inicio: int = 1) -> None:
        self._proximo = inicio
        self.emitidos: list[Recibo] = []

    def emitir(self, cliente_id: int, valor: Decimal, data: date, referencia: str) -> Recibo:
        if valor <= 0:
            raise ValueError("valor do recibo deve ser positivo")
        if not referencia.strip():
            raise ValueError("referência obrigatória")
        r = Recibo(self._proximo, cliente_id, valor, data, referencia.strip())
        self._proximo += 1
        self.emitidos.append(r)
        return r


@dataclass(frozen=True)
class Lancamento:
    """Linha do extrato bancário."""
    data: date
    valor: Decimal
    descricao: str = ""


@dataclass(frozen=True)
class Conciliacao:
    pares: list[tuple[Recibo, Lancamento]]
    recibos_sem_lancamento: list[Recibo]
    lancamentos_sem_recibo: list[Lancamento]

    @property
    def conciliado(self) -> bool:
        return not self.recibos_sem_lancamento and not self.lancamentos_sem_recibo


def conciliar(recibos: list[Recibo], extrato: list[Lancamento], tolerancia_dias: int = 2) -> Conciliacao:
    """Casa recibo e lançamento de mesmo valor com data dentro da tolerância; cada lançamento é usado uma vez."""
    livres = [l for l in extrato if l.valor > 0]
    pares: list[tuple[Recibo, Lancamento]] = []
    sem_lanc: list[Recibo] = []
    for r in sorted(recibos, key=lambda x: (x.data, x.numero)):
        candidatos = [l for l in livres if l.valor == r.valor and abs(l.data - r.data) <= timedelta(days=tolerancia_dias)]
        if candidatos:
            melhor = min(candidatos, key=lambda l: abs(l.data - r.data))
            livres.remove(melhor)
            pares.append((r, melhor))
        else:
            sem_lanc.append(r)
    return Conciliacao(pares, sem_lanc, livres)

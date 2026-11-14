"""Honorários: contratuais fixos em parcelas, êxito percentual e saldo em aberto."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def _q(v: Decimal) -> Decimal:
    return v.quantize(CENT, rounding=ROUND_HALF_UP)


def _mes_seguinte(d: date, n: int) -> date:
    """Mesmo dia n meses depois, limitado ao último dia do mês."""
    m = d.month - 1 + n
    ano, mes = d.year + m // 12, m % 12 + 1
    dias = [31, 29 if ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return date(ano, mes, min(d.day, dias[mes - 1]))


@dataclass
class Parcela:
    numero: int
    vencimento: date
    valor: Decimal
    pago: Decimal = Decimal("0")

    @property
    def saldo(self) -> Decimal:
        return self.valor - self.pago


@dataclass
class ContratoHonorarios:
    cliente_id: int
    valor_fixo: Decimal
    percentual_exito: Decimal = Decimal("0")  # ex.: Decimal("20") = 20%
    parcelas: list[Parcela] = field(default_factory=list)
    exito_apurado: Decimal | None = None

    def valor_exito(self, ganho: Decimal) -> Decimal:
        """Honorário de êxito sobre o proveito econômico obtido."""
        if ganho < 0:
            raise ValueError("ganho não pode ser negativo")
        return _q(ganho * self.percentual_exito / 100)

    def registrar_exito(self, ganho: Decimal) -> Decimal:
        self.exito_apurado = self.valor_exito(ganho)
        return self.exito_apurado

    @property
    def total_devido(self) -> Decimal:
        return self.valor_fixo + (self.exito_apurado or Decimal("0"))

    @property
    def total_pago(self) -> Decimal:
        return sum((p.pago for p in self.parcelas), Decimal("0"))

    def saldo(self) -> Decimal:
        """Saldo geral: fixo parcelado em aberto + êxito apurado (sem parcelas)."""
        return self.total_devido - self.total_pago

    def em_atraso(self, hoje: date) -> list[Parcela]:
        return [p for p in self.parcelas if p.saldo > 0 and p.vencimento < hoje]

    def pagar(self, numero: int, valor: Decimal) -> Decimal:
        """Paga a parcela; devolve o excedente (se houver)."""
        if valor <= 0:
            raise ValueError("valor de pagamento deve ser positivo")
        p = next((x for x in self.parcelas if x.numero == numero), None)
        if p is None:
            raise KeyError(f"parcela {numero} inexistente")
        aplicado = min(valor, p.saldo)
        p.pago += aplicado
        return valor - aplicado


def criar_contrato(cliente_id: int, valor_fixo: Decimal, n_parcelas: int, primeiro_vencimento: date,
                   percentual_exito: Decimal = Decimal("0")) -> ContratoHonorarios:
    """Divide o fixo em parcelas mensais; a diferença de centavos vai para a última."""
    if valor_fixo < 0 or n_parcelas < 1:
        raise ValueError("valor fixo não negativo e ao menos 1 parcela")
    if not Decimal("0") <= percentual_exito <= 100:
        raise ValueError("percentual de êxito deve estar entre 0 e 100")
    base = (valor_fixo / n_parcelas).quantize(CENT, rounding="ROUND_DOWN")
    parcelas = [Parcela(i + 1, _mes_seguinte(primeiro_vencimento, i), base) for i in range(n_parcelas)]
    parcelas[-1].valor += valor_fixo - base * n_parcelas
    return ContratoHonorarios(cliente_id, valor_fixo, percentual_exito, parcelas)

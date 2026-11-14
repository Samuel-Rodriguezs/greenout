"""DRE (Demonstração do Resultado do Exercício) simplificada.

Alíquotas informadas pelo chamador (exemplos nos testes).
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

CENTAVOS = Decimal("0.01")


def _d(valor: object) -> Decimal:
    return valor if isinstance(valor, Decimal) else Decimal(str(valor))


def _q(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class DRE:
    receita_bruta: Decimal
    deducoes: Decimal
    receita_liquida: Decimal
    custo: Decimal
    lucro_bruto: Decimal
    despesas_operacionais: Decimal
    resultado_operacional: Decimal
    resultado_financeiro: Decimal
    lair: Decimal
    imposto_renda: Decimal
    lucro_liquido: Decimal

    @property
    def margem_bruta(self) -> Decimal:
        return _margem(self.lucro_bruto, self.receita_liquida)

    @property
    def margem_liquida(self) -> Decimal:
        return _margem(self.lucro_liquido, self.receita_liquida)


def _margem(valor: Decimal, base: Decimal) -> Decimal:
    return Decimal(0) if base == 0 else valor / base


def montar_dre(receita_bruta: object, aliquota_deducoes: object, custo: object,
               despesas_operacionais: object, resultado_financeiro: object = 0,
               aliquota_ir: object = 0) -> DRE:
    """Monta a DRE. `resultado_financeiro` é líquido (receitas - despesas).

    O imposto sobre o lucro só incide se o LAIR for positivo (sem compensação
    de prejuízo nesta versão simplificada).
    """
    rb = _q(_d(receita_bruta))
    ad, air = _d(aliquota_deducoes), _d(aliquota_ir)
    cst, desp, fin = _q(_d(custo)), _q(_d(despesas_operacionais)), _q(_d(resultado_financeiro))
    if rb < 0 or cst < 0 or desp < 0:
        raise ValueError("receita, custo e despesas não podem ser negativos")
    if not (0 <= ad <= 1) or not (0 <= air <= 1):
        raise ValueError("alíquotas devem estar entre 0 e 1")
    ded = _q(rb * ad)
    rl = rb - ded
    lb = rl - cst
    ebit = lb - desp
    lair = ebit + fin
    ir = _q(lair * air) if lair > 0 else Decimal("0.00")
    return DRE(rb, ded, rl, cst, lb, desp, ebit, fin, lair, ir, lair - ir)

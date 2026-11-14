"""Datas de nascimento fictícias por faixa etária, relativas a uma data de referência injetada."""
from __future__ import annotations

import random
from datetime import date, timedelta

FAIXAS: dict[str, tuple[int, int]] = {
    "crianca": (0, 11),
    "adolescente": (12, 17),
    "adulto_jovem": (18, 29),
    "adulto": (30, 59),
    "idoso": (60, 90),
}


def idade_em(nascimento: date, referencia: date) -> int:
    """Idade completa em anos na data de referência."""
    anos = referencia.year - nascimento.year
    if (referencia.month, referencia.day) < (nascimento.month, nascimento.day):
        anos -= 1
    return anos


def _subtrair_anos(d: date, anos: int) -> date:
    try:
        return d.replace(year=d.year - anos)
    except ValueError:  # 29/02 em ano não bissexto
        return d.replace(year=d.year - anos, day=28)


def gerar_nascimento(
    rng: random.Random, referencia: date, idade_min: int, idade_max: int
) -> date:
    """Data tal que a idade em `referencia` está em [idade_min, idade_max] (inclusive)."""
    if not 0 <= idade_min <= idade_max:
        raise ValueError("faixa etária inválida")
    # mais antigo possível: idade_max completada hoje - (quase um ano); mais novo: idade_min completada hoje
    mais_novo = _subtrair_anos(referencia, idade_min)
    mais_velho = _subtrair_anos(referencia, idade_max + 1) + timedelta(days=1)
    dias = (mais_novo - mais_velho).days
    return mais_velho + timedelta(days=rng.randint(0, dias))


def gerar_por_faixa(rng: random.Random, referencia: date, faixa: str) -> date:
    if faixa not in FAIXAS:
        raise ValueError(f"faixa desconhecida: {faixa!r}")
    lo, hi = FAIXAS[faixa]
    return gerar_nascimento(rng, referencia, lo, hi)


def gerar_populacao(
    rng: random.Random, referencia: date, n: int, pesos: dict[str, float] | None = None
) -> list[tuple[str, date]]:
    """Lista de (faixa, nascimento) com faixas sorteadas por peso."""
    pesos = pesos or {"crianca": 1, "adolescente": 1, "adulto_jovem": 2, "adulto": 4, "idoso": 2}
    nomes = list(pesos)
    escolhidas = rng.choices(nomes, weights=[pesos[k] for k in nomes], k=n)
    return [(f, gerar_por_faixa(rng, referencia, f)) for f in escolhidas]

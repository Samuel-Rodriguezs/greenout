"""Exportação da carteira de processos para CSV e Markdown."""
from __future__ import annotations

import csv
import io
from decimal import Decimal

from jur_processos import Processo

CABECALHO = ["numero", "area", "advogado", "fase", "valor_causa"]
_ROTULOS = ["Número", "Área", "Advogado", "Fase", "Valor da causa"]


def _linha(p: Processo) -> list[str]:
    return [p.numero, p.area, p.advogado, p.fase.value, f"{p.valor_causa:.2f}"]


def _brl(v: Decimal) -> str:
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _neutraliza(celula: str) -> str:
    """Evita injeção de fórmula em planilhas (células iniciadas por = + - @)."""
    return "'" + celula if celula[:1] in ("=", "+", "-", "@") else celula


def para_csv(processos: list[Processo], separador: str = ";") -> str:
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=separador, lineterminator="\n")
    w.writerow(CABECALHO)
    for p in sorted(processos, key=lambda x: x.numero):
        w.writerow([_neutraliza(c) for c in _linha(p)])
    return buf.getvalue()


def de_csv(texto: str, separador: str = ";") -> list[dict[str, str]]:
    leitor = csv.DictReader(io.StringIO(texto), delimiter=separador)
    if leitor.fieldnames != CABECALHO:
        raise ValueError("cabeçalho CSV inesperado")
    return [dict(l) for l in leitor]


def para_markdown(processos: list[Processo]) -> str:
    """Tabela Markdown com valores em reais e linha de total; `|` nas células é escapado."""
    linhas = ["| " + " | ".join(_ROTULOS) + " |", "|" + "|".join(["---"] * 4 + ["---:"]) + "|"]
    total = Decimal("0")
    for p in sorted(processos, key=lambda x: x.numero):
        total += p.valor_causa
        cels = [p.numero, p.area, p.advogado, p.fase.value, _brl(p.valor_causa)]
        linhas.append("| " + " | ".join(c.replace("|", "\\|") for c in cels) + " |")
    linhas.append(f"| **Total ({len(processos)})** | | | | **{_brl(total)}** |")
    return "\n".join(linhas) + "\n"

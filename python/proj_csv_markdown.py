"""Gerador de relatorio CSV -> tabela Markdown, com alinhamento numerico."""
import csv
import io
from typing import List


def _numerico(valor: str) -> bool:
    try:
        float(valor)
        return True
    except ValueError:
        return False


def csv_para_markdown(texto: str, delimitador: str = ",") -> str:
    linhas: List[List[str]] = [
        [c.strip() for c in l] for l in csv.reader(io.StringIO(texto), delimiter=delimitador) if l
    ]
    if not linhas:
        raise ValueError("csv vazio")
    cab, corpo = linhas[0], linhas[1:]
    for i, l in enumerate(corpo, start=2):
        if len(l) != len(cab):
            raise ValueError(f"linha {i} com {len(l)} colunas, esperado {len(cab)}")

    def esc(c: str) -> str:
        return c.replace("|", "\\|")

    larguras = [max([3, len(esc(cab[j]))] + [len(esc(l[j])) for l in corpo]) for j in range(len(cab))]
    direita = [bool(corpo) and all(_numerico(l[j]) for l in corpo) for j in range(len(cab))]

    def fmt(l: List[str]) -> str:
        cel = [
            esc(c).rjust(w) if d else esc(c).ljust(w)
            for c, w, d in zip(l, larguras, direita)
        ]
        return "| " + " | ".join(cel) + " |"

    sep = "| " + " | ".join(("-" * (w - 1) + ":") if d else "-" * w for w, d in zip(larguras, direita)) + " |"
    return "\n".join([fmt(cab), sep] + [fmt(l) for l in corpo])

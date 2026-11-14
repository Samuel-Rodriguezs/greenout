"""Linha do tempo de andamentos processuais."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Andamento:
    processo: str
    data: date
    descricao: str
    tipo: str = "movimentação"
    autor: str = ""


class LinhaDoTempo:
    def __init__(self) -> None:
        self._itens: list[Andamento] = []

    def registrar(self, a: Andamento) -> None:
        if not a.descricao.strip():
            raise ValueError("descrição obrigatória")
        if a in self._itens:
            raise ValueError("andamento duplicado")
        self._itens.append(a)

    def do_processo(self, processo: str, recentes_primeiro: bool = False) -> list[Andamento]:
        itens = [a for a in self._itens if a.processo == processo]
        # sort estável: mesma data preserva a ordem de registro; o inverso é exato
        ordenados = sorted(itens, key=lambda a: a.data)
        return ordenados[::-1] if recentes_primeiro else ordenados

    def ultimo(self, processo: str) -> Andamento | None:
        itens = self.do_processo(processo)
        return itens[-1] if itens else None

    def entre(self, processo: str, inicio: date, fim: date) -> list[Andamento]:
        return [a for a in self.do_processo(processo) if inicio <= a.data <= fim]

    def por_tipo(self, processo: str, tipo: str) -> list[Andamento]:
        return [a for a in self.do_processo(processo) if a.tipo == tipo]

    def dias_sem_movimento(self, processo: str, hoje: date) -> int | None:
        u = self.ultimo(processo)
        return None if u is None else (hoje - u.data).days

    def parados(self, hoje: date, limite_dias: int) -> list[str]:
        """Processos cujo último andamento tem mais de `limite_dias` dias."""
        return sorted(p for p in {a.processo for a in self._itens}
                      if (self.dias_sem_movimento(p, hoje) or 0) > limite_dias)

    def texto(self, processo: str) -> str:
        return "\n".join(f"{a.data.strftime('%d/%m/%Y')} - [{a.tipo}] {a.descricao}" for a in self.do_processo(processo))

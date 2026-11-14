"""Factory Method: exportadores de relatório criados por subclasses."""
from __future__ import annotations

import json
from abc import ABC, abstractmethod


class Exportador(ABC):
    @abstractmethod
    def formatar(self, linhas: list[dict]) -> str: ...


class ExportadorJson(Exportador):
    def formatar(self, linhas: list[dict]) -> str:
        return json.dumps(linhas, ensure_ascii=False)


class ExportadorCsv(Exportador):
    def formatar(self, linhas: list[dict]) -> str:
        if not linhas:
            return ""
        cols = list(linhas[0])
        out = [",".join(cols)]
        out += [",".join(str(l[c]) for c in cols) for l in linhas]
        return "\n".join(out)


class Relatorio(ABC):
    def __init__(self, linhas: list[dict]) -> None:
        self.linhas = linhas

    @abstractmethod
    def criar_exportador(self) -> Exportador: ...

    def gerar(self) -> str:
        return self.criar_exportador().formatar(self.linhas)


class RelatorioJson(Relatorio):
    def criar_exportador(self) -> Exportador:
        return ExportadorJson()


class RelatorioCsv(Relatorio):
    def criar_exportador(self) -> Exportador:
        return ExportadorCsv()

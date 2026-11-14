"""Template Method: pipeline de importação de dados com passos variáveis."""
from __future__ import annotations

import json
from abc import ABC, abstractmethod


class Importador(ABC):
    def importar(self, bruto: str) -> list[dict]:
        registros = self.ler(bruto)
        validos = [r for r in registros if self.validar(r)]
        return [self.transformar(r) for r in validos]

    @abstractmethod
    def ler(self, bruto: str) -> list[dict]: ...

    def validar(self, registro: dict) -> bool:  # gancho com padrão
        return bool(registro.get("email"))

    def transformar(self, registro: dict) -> dict:  # gancho com padrão
        return registro


class ImportadorCsv(Importador):
    def ler(self, bruto: str) -> list[dict]:
        linhas = [l for l in bruto.strip().splitlines() if l.strip()]
        if not linhas:
            return []
        cols = [c.strip() for c in linhas[0].split(",")]
        return [dict(zip(cols, (v.strip() for v in l.split(","))))
                for l in linhas[1:]]

    def transformar(self, registro: dict) -> dict:
        return {**registro, "email": registro["email"].lower()}


class ImportadorJson(Importador):
    def ler(self, bruto: str) -> list[dict]:
        return json.loads(bruto)

    def validar(self, registro: dict) -> bool:
        return "@" in registro.get("email", "")

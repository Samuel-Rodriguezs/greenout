"""Null Object: logger que não faz nada evita checagens de None."""
from __future__ import annotations

from typing import Protocol


class Logger(Protocol):
    def info(self, msg: str) -> None: ...
    def erro(self, msg: str) -> None: ...


class LoggerMemoria:
    def __init__(self) -> None:
        self.linhas: list[str] = []

    def info(self, msg: str) -> None:
        self.linhas.append(f"INFO {msg}")

    def erro(self, msg: str) -> None:
        self.linhas.append(f"ERRO {msg}")


class LoggerNulo:
    def info(self, msg: str) -> None:
        pass

    def erro(self, msg: str) -> None:
        pass


class ProcessadorLote:
    def __init__(self, logger: Logger | None = None) -> None:
        self.logger: Logger = logger if logger is not None else LoggerNulo()

    def processar(self, itens: list[str]) -> int:
        ok = 0
        for item in itens:
            if item.strip():
                self.logger.info(f"processado {item}")
                ok += 1
            else:
                self.logger.erro("item vazio")
        return ok

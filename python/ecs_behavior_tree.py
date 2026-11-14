"""Árvore de comportamento (behavior tree) com nós compostos, decoradores e memória de execução."""
from __future__ import annotations

from enum import Enum
from typing import Any, Callable


class Status(Enum):
    SUCESSO = "sucesso"
    FALHA = "falha"
    EXECUTANDO = "executando"


class No:
    def tick(self, ctx: Any) -> Status:
        raise NotImplementedError

    def resetar(self) -> None:
        """Descarta estado de execução em andamento."""


class Acao(No):
    """Folha que executa `fn(ctx) -> Status`."""

    def __init__(self, fn: Callable[[Any], Status]) -> None:
        self.fn = fn

    def tick(self, ctx: Any) -> Status:
        return self.fn(ctx)


class Condicao(No):
    def __init__(self, pred: Callable[[Any], bool]) -> None:
        self.pred = pred

    def tick(self, ctx: Any) -> Status:
        return Status.SUCESSO if self.pred(ctx) else Status.FALHA


class _Composto(No):
    def __init__(self, *filhos: No) -> None:
        if not filhos:
            raise ValueError("nó composto precisa de filhos")
        self.filhos = list(filhos)
        self._atual = 0  # filho em execução (memória)

    def resetar(self) -> None:
        self._atual = 0
        for f in self.filhos:
            f.resetar()


class Sequencia(_Composto):
    """Executa filhos em ordem; falha no primeiro que falhar; retoma o filho EXECUTANDO."""

    def tick(self, ctx: Any) -> Status:
        while self._atual < len(self.filhos):
            s = self.filhos[self._atual].tick(ctx)
            if s is Status.EXECUTANDO:
                return s
            if s is Status.FALHA:
                self.resetar()
                return s
            self._atual += 1
        self._atual = 0
        return Status.SUCESSO


class Seletor(_Composto):
    """Tenta filhos em ordem; tem sucesso no primeiro que tiver sucesso."""

    def tick(self, ctx: Any) -> Status:
        while self._atual < len(self.filhos):
            s = self.filhos[self._atual].tick(ctx)
            if s is Status.EXECUTANDO:
                return s
            if s is Status.SUCESSO:
                self.resetar()
                return s
            self._atual += 1
        self._atual = 0
        return Status.FALHA


class Paralelo(No):
    """Executa todos os filhos a cada tick. Sucesso se >= `minimo_sucessos` tiverem sucesso."""

    def __init__(self, *filhos: No, minimo_sucessos: int | None = None) -> None:
        if not filhos:
            raise ValueError("nó composto precisa de filhos")
        self.filhos = list(filhos)
        self.minimo = len(filhos) if minimo_sucessos is None else minimo_sucessos
        if not 1 <= self.minimo <= len(filhos):
            raise ValueError("minimo_sucessos fora de [1, n]")

    def tick(self, ctx: Any) -> Status:
        resultados = [f.tick(ctx) for f in self.filhos]
        ok = resultados.count(Status.SUCESSO)
        falhas = resultados.count(Status.FALHA)
        if ok >= self.minimo:
            self.resetar()
            return Status.SUCESSO
        if len(self.filhos) - falhas < self.minimo:
            self.resetar()
            return Status.FALHA
        return Status.EXECUTANDO

    def resetar(self) -> None:
        for f in self.filhos:
            f.resetar()


class Inversor(No):
    def __init__(self, filho: No) -> None:
        self.filho = filho

    def tick(self, ctx: Any) -> Status:
        s = self.filho.tick(ctx)
        if s is Status.SUCESSO:
            return Status.FALHA
        if s is Status.FALHA:
            return Status.SUCESSO
        return s

    def resetar(self) -> None:
        self.filho.resetar()


class SempreSucesso(No):
    def __init__(self, filho: No) -> None:
        self.filho = filho

    def tick(self, ctx: Any) -> Status:
        s = self.filho.tick(ctx)
        return s if s is Status.EXECUTANDO else Status.SUCESSO

    def resetar(self) -> None:
        self.filho.resetar()


class Repetir(No):
    """Repete o filho `n` vezes (sucessos); falha se o filho falhar."""

    def __init__(self, filho: No, n: int) -> None:
        if n < 1:
            raise ValueError("n deve ser >= 1")
        self.filho, self.n, self._feitas = filho, n, 0

    def tick(self, ctx: Any) -> Status:
        while self._feitas < self.n:
            s = self.filho.tick(ctx)
            if s is Status.EXECUTANDO:
                return s
            if s is Status.FALHA:
                self.resetar()
                return s
            self._feitas += 1
        self._feitas = 0
        return Status.SUCESSO

    def resetar(self) -> None:
        self._feitas = 0
        self.filho.resetar()


class Espera(No):
    """Ocupado por `ticks` ticks e depois tem sucesso (útil com tempo discreto)."""

    def __init__(self, ticks: int) -> None:
        self.ticks, self._n = ticks, 0

    def tick(self, ctx: Any) -> Status:
        self._n += 1
        if self._n > self.ticks:
            self._n = 0
            return Status.SUCESSO
        return Status.EXECUTANDO

    def resetar(self) -> None:
        self._n = 0

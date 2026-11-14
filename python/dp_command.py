"""Command com undo/redo: editor de texto simples."""
from __future__ import annotations

from abc import ABC, abstractmethod


class Editor:
    def __init__(self) -> None:
        self.texto = ""


class Comando(ABC):
    @abstractmethod
    def executar(self, ed: Editor) -> None: ...

    @abstractmethod
    def desfazer(self, ed: Editor) -> None: ...


class Inserir(Comando):
    def __init__(self, trecho: str) -> None:
        self.trecho = trecho

    def executar(self, ed: Editor) -> None:
        ed.texto += self.trecho

    def desfazer(self, ed: Editor) -> None:
        ed.texto = ed.texto[: len(ed.texto) - len(self.trecho)]


class ApagarFim(Comando):
    def __init__(self, n: int) -> None:
        self.n = n
        self._apagado = ""

    def executar(self, ed: Editor) -> None:
        corte = max(len(ed.texto) - self.n, 0)
        self._apagado = ed.texto[corte:]
        ed.texto = ed.texto[:corte]

    def desfazer(self, ed: Editor) -> None:
        ed.texto += self._apagado


class Historico:
    def __init__(self, editor: Editor) -> None:
        self.editor = editor
        self._feitos: list[Comando] = []
        self._refazer: list[Comando] = []

    def executar(self, cmd: Comando) -> None:
        cmd.executar(self.editor)
        self._feitos.append(cmd)
        self._refazer.clear()

    def desfazer(self) -> bool:
        if not self._feitos:
            return False
        cmd = self._feitos.pop()
        cmd.desfazer(self.editor)
        self._refazer.append(cmd)
        return True

    def refazer(self) -> bool:
        if not self._refazer:
            return False
        cmd = self._refazer.pop()
        cmd.executar(self.editor)
        self._feitos.append(cmd)
        return True

"""Abstract Factory: famílias de widgets de UI por tema (claro/escuro)."""
from __future__ import annotations

from abc import ABC, abstractmethod


class Botao:
    def __init__(self, tema: str) -> None:
        self.tema = tema

    def desenhar(self, rotulo: str) -> str:
        return f"[{self.tema}:botao {rotulo}]"


class Campo:
    def __init__(self, tema: str) -> None:
        self.tema = tema

    def desenhar(self, valor: str) -> str:
        return f"[{self.tema}:campo {valor}]"


class FabricaUI(ABC):
    @abstractmethod
    def botao(self) -> Botao: ...

    @abstractmethod
    def campo(self) -> Campo: ...


class FabricaClara(FabricaUI):
    def botao(self) -> Botao:
        return Botao("claro")

    def campo(self) -> Campo:
        return Campo("claro")


class FabricaEscura(FabricaUI):
    def botao(self) -> Botao:
        return Botao("escuro")

    def campo(self) -> Campo:
        return Campo("escuro")


def fabrica_para(tema: str) -> FabricaUI:
    try:
        return {"claro": FabricaClara, "escuro": FabricaEscura}[tema]()
    except KeyError:
        raise ValueError(f"tema desconhecido: {tema}") from None


def tela_login(f: FabricaUI) -> list[str]:
    return [f.campo().desenhar("usuario"), f.campo().desenhar("senha"),
            f.botao().desenhar("entrar")]

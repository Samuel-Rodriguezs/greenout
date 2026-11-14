"""Tabela de símbolos com escopos aninhados para Mini."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from comp_lexer import ErroMini


class ErroRedeclaracao(ErroMini):
    pass


@dataclass
class Simbolo:
    nome: str
    categoria: str  # "var", "param" ou "func"
    tipo: str  # tipo da variável ou tipo de retorno da função
    pos: tuple[int, int] = (0, 0)
    params: tuple[str, ...] = ()  # tipos dos parâmetros (só para func)

    @property
    def aridade(self) -> int:
        return len(self.params)


@dataclass
class Escopo:
    nome: str
    pai: Optional["Escopo"] = None
    simbolos: dict[str, Simbolo] = field(default_factory=dict)
    filhos: list["Escopo"] = field(default_factory=list)

    def declarar(self, simbolo: Simbolo) -> Simbolo:
        """Declara no escopo atual; levanta ErroRedeclaracao se já existir aqui."""
        anterior = self.simbolos.get(simbolo.nome)
        if anterior is not None:
            onde = f" (linha {anterior.pos[0]})" if anterior.pos[0] else ""
            raise ErroRedeclaracao(
                f"'{simbolo.nome}' já declarado neste escopo{onde}",
                simbolo.pos[0], simbolo.pos[1], len(simbolo.nome))
        self.simbolos[simbolo.nome] = simbolo
        return simbolo

    def resolver_local(self, nome: str) -> Optional[Simbolo]:
        return self.simbolos.get(nome)

    def resolver(self, nome: str) -> Optional[Simbolo]:
        """Procura o nome do escopo atual para fora (o mais interno vence)."""
        escopo: Optional[Escopo] = self
        while escopo is not None:
            s = escopo.simbolos.get(nome)
            if s is not None:
                return s
            escopo = escopo.pai
        return None

    @property
    def profundidade(self) -> int:
        n, e = 0, self.pai
        while e is not None:
            n, e = n + 1, e.pai
        return n

    def caminho(self) -> str:
        return (self.pai.caminho() + "/" if self.pai else "") + self.nome


class TabelaSimbolos:
    """Pilha de escopos com histórico (a árvore de escopos fica disponível)."""

    def __init__(self) -> None:
        self.global_ = Escopo("global")
        self.atual = self.global_

    def entrar(self, nome: str = "bloco") -> Escopo:
        novo = Escopo(nome, self.atual)
        self.atual.filhos.append(novo)
        self.atual = novo
        return novo

    def sair(self) -> Escopo:
        if self.atual.pai is None:
            raise RuntimeError("não é possível sair do escopo global")
        saido = self.atual
        self.atual = self.atual.pai
        return saido

    def declarar(self, simbolo: Simbolo) -> Simbolo:
        return self.atual.declarar(simbolo)

    def resolver(self, nome: str) -> Optional[Simbolo]:
        return self.atual.resolver(nome)

    def todos(self) -> list[tuple[str, Simbolo]]:
        """Lista (caminho do escopo, símbolo) de toda a árvore, em pré-ordem."""
        saida: list[tuple[str, Simbolo]] = []

        def visitar(e: Escopo) -> None:
            saida.extend((e.caminho(), s) for s in e.simbolos.values())
            for f in e.filhos:
                visitar(f)

        visitar(self.global_)
        return saida

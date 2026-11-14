"""Máquina de estados finita hierárquica (HFSM) com transições por evento ou condição."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Transicao:
    destino: str
    evento: str | None = None
    condicao: Callable[[Any], bool] | None = None


@dataclass
class Estado:
    nome: str
    pai: str | None = None
    inicial: str | None = None  # subestado inicial (estados compostos)
    ao_entrar: Callable[[Any], None] | None = None
    ao_sair: Callable[[Any], None] | None = None
    ao_atualizar: Callable[[Any, float], None] | None = None
    transicoes: list[Transicao] = field(default_factory=list)


class HFSM:
    def __init__(self) -> None:
        self._estados: dict[str, Estado] = {}
        self._atual: str | None = None

    def adicionar(self, estado: Estado) -> Estado:
        if estado.nome in self._estados:
            raise ValueError(f"estado duplicado: {estado.nome}")
        if estado.pai is not None and estado.pai not in self._estados:
            raise ValueError(f"pai inexistente: {estado.pai}")
        self._estados[estado.nome] = estado
        return estado

    @property
    def atual(self) -> str | None:
        return self._atual

    def caminho(self) -> list[str]:
        """Da raiz até o estado folha ativo."""
        return self._ancestrais(self._atual)[::-1] if self._atual else []

    def esta_em(self, nome: str) -> bool:
        return nome in self.caminho()

    def _ancestrais(self, nome: str | None) -> list[str]:
        """O próprio estado e seus pais, do mais interno ao mais externo."""
        cadeia: list[str] = []
        while nome is not None:
            cadeia.append(nome)
            nome = self._estados[nome].pai
        return cadeia

    def _descer(self, nome: str) -> str:
        """Resolve o subestado inicial até uma folha."""
        while self._estados[nome].inicial is not None:
            filho = self._estados[nome].inicial
            if filho not in self._estados or self._estados[filho].pai != nome:
                raise ValueError(f"inicial inválido em {nome}: {filho}")
            nome = filho
        return nome

    def iniciar(self, nome: str, ctx: Any = None) -> None:
        if nome not in self._estados:
            raise KeyError(nome)
        folha = self._descer(nome)
        for n in self._ancestrais(folha)[::-1]:
            self._entrar(n, ctx)
        self._atual = folha

    def _entrar(self, nome: str, ctx: Any) -> None:
        fn = self._estados[nome].ao_entrar
        if fn:
            fn(ctx)

    def _sair(self, nome: str, ctx: Any) -> None:
        fn = self._estados[nome].ao_sair
        if fn:
            fn(ctx)

    def _ir_para(self, destino: str, ctx: Any) -> None:
        folha_destino = self._descer(destino)
        origem = self._ancestrais(self._atual)
        alvo = self._ancestrais(folha_destino)
        # ancestral comum mais interno que sobrevive à transição
        # (uma transição para si mesmo ou para um ancestral reentra o estado)
        comuns = [n for n in origem if n in alvo and n != destino and n != self._atual]
        comum = comuns[0] if comuns else None
        for n in origem:
            if n == comum:
                break
            self._sair(n, ctx)
        descer = alvo[: alvo.index(comum)] if comum is not None else alvo
        for n in reversed(descer):
            self._entrar(n, ctx)
        self._atual = folha_destino

    def _tentar(self, ctx: Any, evento: str | None) -> bool:
        for nome in self._ancestrais(self._atual):  # o mais interno tem precedência
            for t in self._estados[nome].transicoes:
                if t.evento != evento:
                    continue
                if t.condicao is not None and not t.condicao(ctx):
                    continue
                self._ir_para(t.destino, ctx)
                return True
        return False

    def enviar(self, evento: str, ctx: Any = None) -> bool:
        """Processa um evento; devolve se alguma transição ocorreu."""
        if self._atual is None:
            raise RuntimeError("máquina não iniciada")
        return self._tentar(ctx, evento)

    def atualizar(self, ctx: Any = None, dt: float = 0.0) -> None:
        """Avalia transições por condição (sem evento) e então atualiza do pai para o filho."""
        if self._atual is None:
            raise RuntimeError("máquina não iniciada")
        self._tentar(ctx, None)
        for nome in reversed(self._ancestrais(self._atual)):
            fn = self._estados[nome].ao_atualizar
            if fn:
                fn(ctx, dt)

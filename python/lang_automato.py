"""Autômatos finitos: DFA, NFA (com transições epsilon), conversão NFA->DFA e minimização."""
from __future__ import annotations

from typing import Iterable

EPSILON = ""


class ErroAutomato(Exception):
    """Definição inválida de autômato."""


class DFA:
    def __init__(self, estados: Iterable[str], alfabeto: Iterable[str],
                 transicoes: dict[tuple[str, str], str], inicial: str,
                 finais: Iterable[str]) -> None:
        self.estados = set(estados)
        self.alfabeto = set(alfabeto)
        self.transicoes = dict(transicoes)
        self.inicial = inicial
        self.finais = set(finais)
        if inicial not in self.estados or not self.finais <= self.estados:
            raise ErroAutomato("estado inicial/final fora do conjunto de estados")
        for (e, s), d in self.transicoes.items():
            if e not in self.estados or d not in self.estados or s not in self.alfabeto:
                raise ErroAutomato(f"transição inválida: ({e!r}, {s!r}) -> {d!r}")

    def aceita(self, palavra: str) -> bool:
        e = self.inicial
        for s in palavra:
            if s not in self.alfabeto:
                raise ErroAutomato(f"símbolo fora do alfabeto: {s!r}")
            e = self.transicoes.get((e, s), "")  # "" = estado morto implícito
            if e == "":
                return False
        return e in self.finais

    def minimizar(self) -> "DFA":
        """Minimização por refinamento de partições (após remover inalcançáveis e completar)."""
        morto = "__morto__"
        alcancaveis, fila = {self.inicial}, [self.inicial]
        while fila:
            e = fila.pop()
            for s in self.alfabeto:
                d = self.transicoes.get((e, s), morto)
                if d not in alcancaveis:
                    alcancaveis.add(d)
                    fila.append(d)

        def delta(e: str, s: str) -> str:
            return self.transicoes.get((e, s), morto) if e != morto else morto

        classe = {e: int(e in self.finais) for e in alcancaveis}
        while True:
            assinatura = {e: (classe[e], tuple(classe[delta(e, s)] for s in sorted(self.alfabeto)))
                          for e in alcancaveis}
            ids: dict[tuple, int] = {}
            nova = {e: ids.setdefault(assinatura[e], len(ids)) for e in sorted(alcancaveis)}
            if len(set(nova.values())) == len(set(classe.values())):
                break
            classe = nova
        classe = nova
        nome = {c: f"q{c}" for c in set(classe.values())}
        classe_morta = classe.get(morto)
        trans = {}
        for e in alcancaveis:
            for s in self.alfabeto:
                d = delta(e, s)
                if classe[d] != classe_morta:
                    trans[(nome[classe[e]], s)] = nome[classe[d]]
        estados = {nome[c] for c in classe.values() if c != classe_morta}
        finais = {nome[classe[e]] for e in alcancaveis if e in self.finais}
        return DFA(estados or {nome[classe[self.inicial]]}, self.alfabeto, trans,
                   nome[classe[self.inicial]], finais)


class NFA:
    def __init__(self, estados: Iterable[str], alfabeto: Iterable[str],
                 transicoes: dict[tuple[str, str], set[str]], inicial: str,
                 finais: Iterable[str]) -> None:
        self.estados = set(estados)
        self.alfabeto = set(alfabeto)
        self.transicoes = {k: set(v) for k, v in transicoes.items()}
        self.inicial = inicial
        self.finais = set(finais)
        if inicial not in self.estados or not self.finais <= self.estados:
            raise ErroAutomato("estado inicial/final fora do conjunto de estados")
        for (e, s), ds in self.transicoes.items():
            if e not in self.estados or not ds <= self.estados or (s != EPSILON and s not in self.alfabeto):
                raise ErroAutomato(f"transição inválida: ({e!r}, {s!r})")

    def fecho_epsilon(self, conjunto: Iterable[str]) -> frozenset[str]:
        res, pilha = set(conjunto), list(conjunto)
        while pilha:
            for d in self.transicoes.get((pilha.pop(), EPSILON), ()):
                if d not in res:
                    res.add(d)
                    pilha.append(d)
        return frozenset(res)

    def aceita(self, palavra: str) -> bool:
        atual = self.fecho_epsilon({self.inicial})
        for s in palavra:
            if s not in self.alfabeto:
                raise ErroAutomato(f"símbolo fora do alfabeto: {s!r}")
            prox: set[str] = set()
            for e in atual:
                prox |= self.transicoes.get((e, s), set())
            atual = self.fecho_epsilon(prox)
            if not atual:
                return False
        return bool(atual & self.finais)

    def para_dfa(self) -> DFA:
        """Construção de subconjuntos."""
        ini = self.fecho_epsilon({self.inicial})
        nomes: dict[frozenset[str], str] = {ini: "S0"}
        fila = [ini]
        trans: dict[tuple[str, str], str] = {}
        while fila:
            cj = fila.pop(0)
            for s in sorted(self.alfabeto):
                alvo: set[str] = set()
                for e in cj:
                    alvo |= self.transicoes.get((e, s), set())
                alvo_f = self.fecho_epsilon(alvo)
                if not alvo_f:
                    continue
                if alvo_f not in nomes:
                    nomes[alvo_f] = f"S{len(nomes)}"
                    fila.append(alvo_f)
                trans[(nomes[cj], s)] = nomes[alvo_f]
        finais = {n for cj, n in nomes.items() if cj & self.finais}
        return DFA(nomes.values(), self.alfabeto, trans, "S0", finais)

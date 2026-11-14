"""Gramática livre de contexto: leitura de regras, conversão para CNF e reconhecimento por CYK.

Formato: `S -> A B | 'a'`, uma regra por linha; não terminais começam com maiúscula,
terminais são caracteres minúsculos/símbolos ou entre aspas simples; `eps` (ou 'ε') é a palavra vazia.
"""
from __future__ import annotations

from itertools import count


class ErroGramatica(Exception):
    """Gramática mal formada."""


Producao = tuple[str, ...]


def _simbolo_terminal(s: str) -> bool:
    return not s[0].isupper()


class Gramatica:
    def __init__(self, texto: str) -> None:
        self.regras: dict[str, set[Producao]] = {}
        self.inicial = ""
        for n, linha in enumerate(texto.splitlines(), 1):
            linha = linha.split("#", 1)[0].strip()
            if not linha:
                continue
            if "->" not in linha:
                raise ErroGramatica(f"linha {n}: falta '->'")
            esq, dir_ = (p.strip() for p in linha.split("->", 1))
            if not esq or not esq[0].isupper() or " " in esq:
                raise ErroGramatica(f"linha {n}: lado esquerdo inválido {esq!r}")
            if not self.inicial:
                self.inicial = esq
            for alt in dir_.split("|"):
                simbolos = tuple(self._ler_simbolo(s, n) for s in alt.split())
                if not simbolos:
                    raise ErroGramatica(f"linha {n}: alternativa vazia (use eps)")
                if simbolos in (("eps",), ("ε",)):
                    simbolos = ()
                self.regras.setdefault(esq, set()).add(simbolos)
        if not self.inicial:
            raise ErroGramatica("gramática vazia")
        for prods in self.regras.values():
            for p in prods:
                for s in p:
                    if not _simbolo_terminal(s) and s not in self.regras:
                        raise ErroGramatica(f"não terminal sem regra: {s}")
        self._cnf: tuple[dict[str, set[str]], dict[tuple[str, str], set[str]], bool, str] | None = None

    @staticmethod
    def _ler_simbolo(s: str, n: int) -> str:
        if len(s) >= 3 and s[0] == s[-1] == "'":
            return s[1:-1]
        if s[0].isupper() or len(s) == 1 or s in ("eps", "ε"):
            return s
        raise ErroGramatica(f"linha {n}: terminal com vários caracteres deve estar entre aspas: {s!r}")

    # ---- conversão para forma normal de Chomsky ----
    def _converter_cnf(self) -> tuple[dict[str, set[str]], dict[tuple[str, str], set[str]], bool, str]:
        if self._cnf is not None:
            return self._cnf
        regras = {k: set(v) for k, v in self.regras.items()}
        novos = (f"X{i}" for i in count(1))
        inicial = "S0'"
        regras[inicial] = {(self.inicial,)}
        # terminais em regras longas -> não terminais
        term_nt: dict[str, str] = {}
        for nt in list(regras):
            novas = set()
            for p in regras[nt]:
                if len(p) >= 2:
                    p = tuple(self._nt_de_terminal(s, term_nt, regras, novos) if _simbolo_terminal(s) else s for s in p)
                novas.add(p)
            regras[nt] = novas
        # binarização
        for nt in list(regras):
            novas = set()
            for p in regras[nt]:
                while len(p) > 2:
                    aux = next(novos)
                    regras[aux] = {p[-2:]}
                    p = p[:-2] + (aux,)
                novas.add(p)
            regras[nt] = novas
        # eliminar epsilon
        anulaveis = {nt for nt, ps in regras.items() if () in ps}
        mudou = True
        while mudou:
            mudou = False
            for nt, ps in regras.items():
                if nt not in anulaveis and any(p and all(s in anulaveis for s in p) for p in ps):
                    anulaveis.add(nt)
                    mudou = True
        gera_vazio = inicial in anulaveis
        for nt in list(regras):
            novas = set()
            for p in regras[nt]:
                if not p:
                    continue
                novas.add(p)
                if len(p) == 2:
                    if p[0] in anulaveis:
                        novas.add((p[1],))
                    if p[1] in anulaveis:
                        novas.add((p[0],))
            regras[nt] = novas
        # eliminar produções unitárias
        for nt in regras:
            fecho, pilha = {nt}, [nt]
            while pilha:
                for p in regras[pilha.pop()]:
                    if len(p) == 1 and not _simbolo_terminal(p[0]) and p[0] not in fecho:
                        fecho.add(p[0])
                        pilha.append(p[0])
            regras[nt] = {p for alvo in fecho for p in regras[alvo]
                          if not (len(p) == 1 and not _simbolo_terminal(p[0]))}
        terminais: dict[str, set[str]] = {}
        pares: dict[tuple[str, str], set[str]] = {}
        for nt, ps in regras.items():
            for p in ps:
                if len(p) == 1:
                    terminais.setdefault(p[0], set()).add(nt)
                elif len(p) == 2:
                    pares.setdefault((p[0], p[1]), set()).add(nt)
        self._cnf = (terminais, pares, gera_vazio, inicial)
        return self._cnf

    @staticmethod
    def _nt_de_terminal(t: str, mapa: dict[str, str], regras: dict[str, set[Producao]], novos) -> str:
        if t not in mapa:
            mapa[t] = next(novos)
            regras[mapa[t]] = {(t,)}
        return mapa[t]

    def reconhece(self, palavra: str) -> bool:
        """CYK, O(n^3 * |G|)."""
        terminais, pares, gera_vazio, inicial = self._converter_cnf()
        n = len(palavra)
        if n == 0:
            return gera_vazio
        tabela: list[list[set[str]]] = [[set() for _ in range(n)] for _ in range(n)]
        for i, c in enumerate(palavra):
            tabela[i][i] = set(terminais.get(c, ()))
        for tam in range(2, n + 1):
            for i in range(n - tam + 1):
                j = i + tam - 1
                for k in range(i, j):
                    for b in tabela[i][k]:
                        for c in tabela[k + 1][j]:
                            tabela[i][j] |= pares.get((b, c), set())
        return inicial in tabela[0][n - 1]

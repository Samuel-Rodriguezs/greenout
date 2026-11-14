"""Normalização forte de termos simplesmente tipados: todo termo bem tipado
termina, qualquer que seja a ordem de redução. Aqui isso é observável:
exploramos todas as sequências de redução e comparamos os resultados."""
from __future__ import annotations

from functools import lru_cache

from tipos_stlc import App, ErroTipo, Lam, Lit, Se, Termo, Var, verificar
from tipos_unificacao import INT, Tipo, seta


def livres(t: Termo) -> frozenset[str]:
    if isinstance(t, Var):
        return frozenset({t.nome})
    if isinstance(t, Lit):
        return frozenset()
    if isinstance(t, Lam):
        return livres(t.corpo) - {t.param}
    if isinstance(t, App):
        return livres(t.fun) | livres(t.arg)
    return livres(t.cond) | livres(t.entao) | livres(t.senao)


def _fresco(base: str, evitar: frozenset[str]) -> str:
    i = 1
    while f"{base}{i}" in evitar:
        i += 1
    return f"{base}{i}"


def substituir(t: Termo, x: str, s: Termo) -> Termo:
    if isinstance(t, Var):
        return s if t.nome == x else t
    if isinstance(t, Lit):
        return t
    if isinstance(t, App):
        return App(substituir(t.fun, x, s), substituir(t.arg, x, s))
    if isinstance(t, Se):
        return Se(substituir(t.cond, x, s), substituir(t.entao, x, s),
                  substituir(t.senao, x, s))
    if t.param == x:
        return t
    if t.param in livres(s) and x in livres(t.corpo):
        novo = _fresco(t.param, livres(s) | livres(t.corpo) | {x})
        corpo = substituir(t.corpo, t.param, Var(novo))
        return Lam(novo, t.anot, substituir(corpo, x, s))
    return Lam(t.param, t.anot, substituir(t.corpo, x, s))


def reducoes(t: Termo) -> list[Termo]:
    """Todos os termos alcançáveis por um passo (beta ou condicional)."""
    if isinstance(t, (Var, Lit)):
        return []
    if isinstance(t, Lam):
        return [Lam(t.param, t.anot, r) for r in reducoes(t.corpo)]
    if isinstance(t, App):
        saida: list[Termo] = []
        if isinstance(t.fun, Lam):
            saida.append(substituir(t.fun.corpo, t.fun.param, t.arg))
        saida += [App(r, t.arg) for r in reducoes(t.fun)]
        saida += [App(t.fun, r) for r in reducoes(t.arg)]
        return saida
    saida = []
    if isinstance(t.cond, Lit) and isinstance(t.cond.valor, bool):
        saida.append(t.entao if t.cond.valor else t.senao)
    saida += [Se(r, t.entao, t.senao) for r in reducoes(t.cond)]
    saida += [Se(t.cond, r, t.senao) for r in reducoes(t.entao)]
    saida += [Se(t.cond, t.entao, r) for r in reducoes(t.senao)]
    return saida


def canonico(t: Termo) -> Termo:
    """Renomeia variáveis ligadas por profundidade (v0, v1...) para comparar
    termos até alfa-equivalência."""
    def go(t: Termo, env: dict[str, str], n: int) -> Termo:
        if isinstance(t, Var):
            return Var(env.get(t.nome, t.nome))
        if isinstance(t, Lit):
            return t
        if isinstance(t, Lam):
            nome = f"#{n}"
            return Lam(nome, t.anot, go(t.corpo, {**env, t.param: nome}, n + 1))
        if isinstance(t, App):
            return App(go(t.fun, env, n), go(t.arg, env, n))
        return Se(go(t.cond, env, n), go(t.entao, env, n), go(t.senao, env, n))
    return go(t, {}, 0)


def _exigir_tipado(t: Termo, ctx: dict[str, Tipo] | None) -> Tipo:
    return verificar(t, ctx)  # ErroTipo se mal tipado: sem garantia de terminação


def _passo_normal(t: Termo) -> Termo | None:
    """Ordem normal: o redex mais externo e à esquerda."""
    if isinstance(t, (Var, Lit)):
        return None
    if isinstance(t, Lam):
        r = _passo_normal(t.corpo)
        return None if r is None else Lam(t.param, t.anot, r)
    if isinstance(t, App):
        if isinstance(t.fun, Lam):
            return substituir(t.fun.corpo, t.fun.param, t.arg)
        r = _passo_normal(t.fun)
        if r is not None:
            return App(r, t.arg)
        r = _passo_normal(t.arg)
        return None if r is None else App(t.fun, r)
    if isinstance(t.cond, Lit) and isinstance(t.cond.valor, bool):
        return t.entao if t.cond.valor else t.senao
    for i, parte in enumerate((t.cond, t.entao, t.senao)):
        r = _passo_normal(parte)
        if r is not None:
            partes = [t.cond, t.entao, t.senao]
            partes[i] = r
            return Se(*partes)
    return None


def normalizar(t: Termo, ctx: dict[str, Tipo] | None = None) -> tuple[Termo, int]:
    """(forma normal, nº de passos); recusa termos mal tipados."""
    _exigir_tipado(t, ctx)
    n = 0
    while (r := _passo_normal(t)) is not None:
        t, n = r, n + 1
    return t, n


class Normalizacao:
    """Exploração exaustiva do grafo de redução de um termo tipado."""

    def __init__(self, t: Termo, ctx: dict[str, Tipo] | None = None) -> None:
        self.tipo = _exigir_tipado(t, ctx)
        self.ctx = ctx
        self.inicio = canonico(t)
        self._longest = lru_cache(maxsize=None)(self._maior)
        self._shortest = lru_cache(maxsize=None)(self._menor)
        self._formas = lru_cache(maxsize=None)(self._normais)

    def _vizinhos(self, t: Termo) -> list[Termo]:
        return list({canonico(r) for r in reducoes(t)})

    def _maior(self, t: Termo) -> int:
        vs = self._vizinhos(t)
        return 0 if not vs else 1 + max(self._longest(v) for v in vs)

    def _menor(self, t: Termo) -> int:
        vs = self._vizinhos(t)
        return 0 if not vs else 1 + min(self._shortest(v) for v in vs)

    def _normais(self, t: Termo) -> frozenset[Termo]:
        vs = self._vizinhos(t)
        if not vs:
            return frozenset({t})
        return frozenset().union(*(self._formas(v) for v in vs))

    def sequencia_mais_longa(self) -> int:
        return self._longest(self.inicio)

    def sequencia_mais_curta(self) -> int:
        return self._shortest(self.inicio)

    def formas_normais(self) -> frozenset[Termo]:
        """Conjunto de formas normais alcançáveis (unitário, por confluência)."""
        return self._formas(self.inicio)

    def preserva_tipo(self) -> bool:
        """Subject reduction: cada passo de cada sequência mantém o tipo."""
        vistos: set[Termo] = set()
        pilha = [self.inicio]
        while pilha:
            t = pilha.pop()
            if t in vistos:
                continue
            vistos.add(t)
            for v in self._vizinhos(t):
                if verificar(v, self.ctx) != self.tipo:
                    return False
                pilha.append(v)
        return True


def numeral(n: int, a: Tipo = INT) -> Termo:
    """Numeral de Church tipado: (a -> a) -> a -> a."""
    corpo: Termo = Var("x")
    for _ in range(n):
        corpo = App(Var("f"), corpo)
    return Lam("f", seta(a, a), Lam("x", a, corpo))


def tipo_numeral(a: Tipo = INT) -> Tipo:
    return seta(seta(a, a), seta(a, a))


def soma_tipada(a: Tipo = INT) -> Termo:
    n = tipo_numeral(a)
    corpo = App(App(Var("m"), Var("f")), App(App(Var("n"), Var("f")), Var("x")))
    return Lam("m", n, Lam("n", n, Lam("f", seta(a, a), Lam("x", a, corpo))))


def mult_tipada(a: Tipo = INT) -> Termo:
    n = tipo_numeral(a)
    corpo = App(App(Var("m"), App(Var("n"), Var("f"))), Var("x"))
    return Lam("m", n, Lam("n", n, Lam("f", seta(a, a), Lam("x", a, corpo))))

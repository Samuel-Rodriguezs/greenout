"""Planejador: escolhe entre varredura sequencial e índice, e o algoritmo de junção.

Modelo de custo (unidades de "linha lida"):
  sequencial = n
  índice     = DESCIDA + linhas_estimadas * PENALIDADE_ALEATORIA
Seletividade: igualdade em índice único = 1 linha; igualdade em não único = 10%;
intervalo aberto de um lado = 25%; BETWEEN/dois limites = 10%.
O filtro WHERE completo é sempre reaplicado sobre o resultado (o índice só estreita).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from bd_catalogo import Catalogo, Indice, Tabela
from bd_sql_parser import Binario, Coluna, Entre, Literal, Selecionar

DESCIDA = 3.0
PENALIDADE_ALEATORIA = 4.0
SEL_IGUAL_NAO_UNICO = 0.10
SEL_INTERVALO_ABERTO = 0.25
SEL_INTERVALO_FECHADO = 0.10


@dataclass
class ScanSeq:
    tabela: str
    alias: str
    linhas_est: float = 0
    custo: float = 0


@dataclass
class ScanIndice:
    tabela: str
    alias: str
    indice: str
    coluna: str
    lo: Any = None
    hi: Any = None
    lo_incl: bool = True
    hi_incl: bool = True
    linhas_est: float = 0
    custo: float = 0

    @property
    def igualdade(self) -> bool:
        return self.lo is not None and self.lo == self.hi and self.lo_incl and self.hi_incl


@dataclass
class JuncaoPlano:
    algoritmo: str                 # 'hash' | 'loop'
    esq: Any
    dir: Any
    condicao: Any
    chave_esq: Optional[Coluna] = None
    chave_dir: Optional[Coluna] = None
    linhas_est: float = 0
    custo: float = 0


@dataclass
class Plano:
    raiz: Any
    where: Any
    consulta: Selecionar


def conjuntos(expr: Any) -> list[Any]:
    """Achata uma árvore de ANDs em lista de predicados."""
    if expr is None:
        return []
    if isinstance(expr, Binario) and expr.op == "AND":
        return conjuntos(expr.esq) + conjuntos(expr.dir)
    return [expr]


_INVERTE = {"<": ">", "<=": ">=", ">": "<", ">=": "<=", "=": "="}


class Planejador:
    def __init__(self, catalogo: Catalogo) -> None:
        self.cat = catalogo

    # ---- candidatos de índice ----
    def _coluna_da_tabela(self, c: Any, alias: str, t: Tabela, outras: list[Tabela]) -> Optional[str]:
        if not isinstance(c, Coluna):
            return None
        if c.tabela is not None:
            ok = c.tabela.lower() in (alias, t.nome)
        else:
            ok = not any(any(x.nome == c.nome.lower() for x in o.colunas) for o in outras)
        if not ok or not any(x.nome == c.nome.lower() for x in t.colunas):
            return None
        return c.nome.lower()

    def _limites(self, preds: list[Any], alias: str, t: Tabela, outras: list[Tabela]) -> dict[str, dict]:
        """Por coluna indexada: {'lo','hi','lo_incl','hi_incl'} agregando os predicados."""
        saida: dict[str, dict] = {}

        def reg(col: str, lo=None, hi=None, lo_incl=True, hi_incl=True) -> None:
            if t.indice_da_coluna(col) is None:
                return
            d = saida.setdefault(col, {"lo": None, "hi": None, "lo_incl": True, "hi_incl": True})
            if lo is not None and (d["lo"] is None or lo > d["lo"] or (lo == d["lo"] and not lo_incl)):
                d["lo"], d["lo_incl"] = lo, lo_incl
            if hi is not None and (d["hi"] is None or hi < d["hi"] or (hi == d["hi"] and not hi_incl)):
                d["hi"], d["hi_incl"] = hi, hi_incl

        for p in preds:
            if isinstance(p, Binario) and p.op in _INVERTE:
                op, a, b = p.op, p.esq, p.dir
                if isinstance(a, Literal) and not isinstance(b, Literal):
                    a, b, op = b, a, _INVERTE[op]
                col = self._coluna_da_tabela(a, alias, t, outras)
                if col is None or not isinstance(b, Literal) or b.valor is None:
                    continue
                v = b.valor
                if isinstance(v, bool) or isinstance(v, str) != (t.colunas[t.posicao(col)].tipo == "TEXT"):
                    continue  # tipos incompatíveis: deixa para o filtro acusar/descartar
                if op == "=":
                    reg(col, v, v)
                elif op in (">", ">="):
                    reg(col, lo=v, lo_incl=op == ">=")
                else:
                    reg(col, hi=v, hi_incl=op == "<=")
            elif isinstance(p, Entre) and not p.negado:
                col = self._coluna_da_tabela(p.expr, alias, t, outras)
                if col and isinstance(p.lo, Literal) and isinstance(p.hi, Literal) \
                        and p.lo.valor is not None and p.hi.valor is not None \
                        and not isinstance(p.lo.valor, bool) and not isinstance(p.hi.valor, bool) \
                        and isinstance(p.lo.valor, str) == isinstance(p.hi.valor, str) \
                        == (t.colunas[t.posicao(col)].tipo == "TEXT"):
                    reg(col, p.lo.valor, p.hi.valor)
        return saida

    def _estimar(self, t: Tabela, ind: Indice, lim: dict) -> float:
        n = max(t.n_linhas, 1)
        igual = lim["lo"] is not None and lim["lo"] == lim["hi"] and lim["lo_incl"] and lim["hi_incl"]
        if igual:
            return 1.0 if ind.unico else max(1.0, n * SEL_IGUAL_NAO_UNICO)
        if lim["lo"] is not None and lim["hi"] is not None:
            return max(1.0, n * SEL_INTERVALO_FECHADO)
        return max(1.0, n * SEL_INTERVALO_ABERTO)

    def escolher_acesso(self, tabela: str, alias: Optional[str], where: Any,
                        outras: Optional[list[str]] = None) -> Any:
        t = self.cat.tabela(tabela)
        a = (alias or t.nome).lower()
        outros = [self.cat.tabela(o) for o in (outras or [])]
        n = float(t.n_linhas)
        melhor: Any = ScanSeq(t.nome, a, n, n)
        for col, lim in self._limites(conjuntos(where), a, t, outros).items():
            ind = t.indice_da_coluna(col)
            est = self._estimar(t, ind, lim)
            custo = DESCIDA + est * PENALIDADE_ALEATORIA
            if custo < melhor.custo:
                melhor = ScanIndice(t.nome, a, ind.nome, col, lim["lo"], lim["hi"],
                                    lim["lo_incl"], lim["hi_incl"], est, custo)
        return melhor

    # ---- plano completo ----
    def planejar(self, s: Selecionar) -> Plano:
        nomes = [s.tabela] + [j.tabela for j in s.juncoes]
        for n in nomes:
            self.cat.tabela(n)  # valida existência
        aliases = [(s.alias or s.tabela).lower()] + [(j.alias or j.tabela).lower() for j in s.juncoes]
        if len(set(aliases)) != len(aliases):
            raise ValueError("alias de tabela duplicado")
        raiz = self.escolher_acesso(s.tabela, s.alias, s.where, nomes[1:])
        for j in s.juncoes:
            raiz = self._juntar(raiz, j, aliases)
        return Plano(raiz, s.where, s)

    def _juntar(self, esq: Any, j: Any, aliases: list[str]) -> JuncaoPlano:
        t = self.cat.tabela(j.tabela)
        dir_ = ScanSeq(t.nome, (j.alias or j.tabela).lower(), float(t.n_linhas), float(t.n_linhas))
        c = j.condicao
        chaves = None
        if isinstance(c, Binario) and c.op == "=" and isinstance(c.esq, Coluna) and isinstance(c.dir, Coluna):
            chaves = self._separar(c, dir_.alias, t)
        if chaves:
            ce, cd = chaves
            est = max(esq.linhas_est, dir_.linhas_est)
            custo = esq.custo + dir_.custo + esq.linhas_est + dir_.linhas_est
            return JuncaoPlano("hash", esq, dir_, c, ce, cd, est, custo)
        est = esq.linhas_est * dir_.linhas_est * 0.1
        custo = esq.custo + dir_.custo + esq.linhas_est * dir_.linhas_est
        return JuncaoPlano("loop", esq, dir_, c, None, None, est, custo)

    @staticmethod
    def _separar(c: Binario, alias_dir: str, t: Tabela) -> Optional[tuple[Coluna, Coluna]]:
        def da_dir(col: Coluna) -> bool:
            if col.tabela is not None:
                return col.tabela.lower() in (alias_dir, t.nome)
            return any(x.nome == col.nome.lower() for x in t.colunas)

        a, b = c.esq, c.dir
        if da_dir(a) == da_dir(b):
            return None  # as duas (ou nenhuma) são da tabela nova: não é junção entre lados
        return (a, b) if da_dir(b) else (b, a)


def explicar(no: Any, nivel: int = 0) -> str:
    """Árvore textual do plano (estilo EXPLAIN)."""
    if isinstance(no, Plano):
        cab = "Plano" + (" [com filtro]" if no.where is not None else "")
        return cab + "\n" + explicar(no.raiz, 1)
    pad = "  " * nivel
    if isinstance(no, ScanSeq):
        return f"{pad}ScanSeq {no.tabela} (linhas~{no.linhas_est:g}, custo={no.custo:g})"
    if isinstance(no, ScanIndice):
        faixa = f"= {no.lo!r}" if no.igualdade else (
            f"{'[' if no.lo_incl else '('}{no.lo!r}, {no.hi!r}{']' if no.hi_incl else ')'}")
        return f"{pad}ScanIndice {no.tabela} via {no.indice} {no.coluna} {faixa} (linhas~{no.linhas_est:g}, custo={no.custo:g})"
    if isinstance(no, JuncaoPlano):
        return (f"{pad}Junção[{no.algoritmo}] (linhas~{no.linhas_est:g}, custo={no.custo:g})\n"
                f"{explicar(no.esq, nivel + 1)}\n{explicar(no.dir, nivel + 1)}")
    raise TypeError(f"nó desconhecido: {no!r}")

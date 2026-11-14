"""Kinds de tipos de ordem superior: verificação e inferência (com
unificação de kinds e padrão * para variáveis não restritas)."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import count


@dataclass(frozen=True)
class Estrela:
    pass


@dataclass(frozen=True)
class KSeta:
    de: "Kind"
    para: "Kind"


@dataclass(frozen=True)
class KVar:
    id: int


Kind = Estrela | KSeta | KVar


@dataclass(frozen=True)
class TC:
    nome: str


@dataclass(frozen=True)
class TV:
    nome: str


@dataclass(frozen=True)
class TAp:
    f: "TipoK"
    a: "TipoK"


TipoK = TC | TV | TAp

STAR = Estrela()


class ErroKind(Exception):
    pass


def k(*partes: Kind) -> Kind:
    """k(A, B, C) = A -> B -> C"""
    r = partes[-1]
    for p in reversed(partes[:-1]):
        r = KSeta(p, r)
    return r


def ap(f: TipoK, *args: TipoK) -> TipoK:
    for a in args:
        f = TAp(f, a)
    return f


def fn(a: TipoK, b: TipoK) -> TipoK:
    return ap(TC("->"), a, b)


def kinds_padrao() -> dict[str, Kind]:
    return {
        "Int": STAR, "Bool": STAR, "Str": STAR,
        "Lista": k(STAR, STAR), "Maybe": k(STAR, STAR),
        "->": k(STAR, STAR, STAR), "Either": k(STAR, STAR, STAR),
        "Par": k(STAR, STAR, STAR),
    }


def mostrar(kd: Kind) -> str:
    if isinstance(kd, Estrela):
        return "*"
    if isinstance(kd, KVar):
        return f"k{kd.id}"
    esq = mostrar(kd.de)
    if isinstance(kd.de, KSeta):
        esq = f"({esq})"
    return f"{esq} -> {mostrar(kd.para)}"


class _Inferencia:
    def __init__(self, kcons: dict[str, Kind]) -> None:
        self.kcons = kcons
        self.s: dict[int, Kind] = {}
        self.ids = count()
        self.vars: dict[str, Kind] = {}

    def nova(self) -> KVar:
        return KVar(next(self.ids))

    def resolve(self, kd: Kind) -> Kind:
        while isinstance(kd, KVar) and kd.id in self.s:
            kd = self.s[kd.id]
        if isinstance(kd, KSeta):
            return KSeta(self.resolve(kd.de), self.resolve(kd.para))
        return kd

    def ocorre(self, i: int, kd: Kind) -> bool:
        kd = self.resolve(kd)
        if isinstance(kd, KVar):
            return kd.id == i
        if isinstance(kd, KSeta):
            return self.ocorre(i, kd.de) or self.ocorre(i, kd.para)
        return False

    def unir(self, a: Kind, b: Kind) -> None:
        a, b = self.resolve(a), self.resolve(b)
        if a == b:
            return
        if isinstance(a, KVar) or isinstance(b, KVar):
            v, o = (a, b) if isinstance(a, KVar) else (b, a)
            if self.ocorre(v.id, o):
                raise ErroKind("kind infinito (occurs check)")
            self.s[v.id] = o
            return
        if isinstance(a, KSeta) and isinstance(b, KSeta):
            self.unir(a.de, b.de)
            self.unir(a.para, b.para)
            return
        raise ErroKind(f"kinds incompatíveis: {mostrar(a)} e {mostrar(b)}")

    def inferir(self, t: TipoK) -> Kind:
        if isinstance(t, TC):
            if t.nome not in self.kcons:
                raise ErroKind(f"construtor de tipo desconhecido: {t.nome}")
            return self.kcons[t.nome]
        if isinstance(t, TV):
            if t.nome not in self.vars:
                self.vars[t.nome] = self.nova()
            return self.vars[t.nome]
        kf, ka = self.inferir(t.f), self.inferir(t.a)
        r = self.nova()
        self.unir(kf, KSeta(ka, r))
        return r

    def padrao(self, kd: Kind) -> Kind:
        """Resolve e troca variáveis de kind restantes por *."""
        kd = self.resolve(kd)
        if isinstance(kd, KVar):
            return STAR
        if isinstance(kd, KSeta):
            return KSeta(self.padrao(kd.de), self.padrao(kd.para))
        return kd


def kind_de(t: TipoK, kcons: dict[str, Kind],
            vars_: dict[str, Kind] | None = None) -> Kind:
    """Kind de t. Variáveis de `vars_` têm kind dado; as demais são inferidas."""
    inf = _Inferencia(kcons)
    inf.vars = dict(vars_ or {})
    return inf.padrao(inf.inferir(t))


def verificar_kind(t: TipoK, esperado: Kind, kcons: dict[str, Kind],
                   vars_: dict[str, Kind] | None = None) -> None:
    inf = _Inferencia(kcons)
    inf.vars = dict(vars_ or {})
    inf.unir(inf.inferir(t), esperado)


def declarar_dados(kcons: dict[str, Kind], nome: str, params: tuple[str, ...],
                   campos: list[TipoK]) -> Kind:
    """Infere o kind de um tipo de dados (possivelmente recursivo) a partir
    dos campos de seus construtores, e o registra em kcons."""
    inf = _Inferencia(kcons)
    kparams = [inf.nova() for _ in params]
    inf.vars = dict(zip(params, kparams))
    resultado = inf.nova()
    inf.kcons = {**kcons, nome: resultado}
    for c in campos:
        inf.unir(inf.inferir(c), STAR)
    inf.unir(resultado, k(*kparams, STAR))
    kd = inf.padrao(resultado)
    kcons[nome] = kd
    return kd

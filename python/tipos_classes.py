"""Type classes por passagem de dicionários: classes com superclasses e
métodos padrão, instâncias com contexto e resolução por tipo."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from tipos_unificacao import TCon, TVar, Tipo, mostrar


class ErroClasse(Exception):
    pass


class Dicionario:
    """Implementação de uma classe para um tipo concreto."""

    def __init__(self, classe: str, tipo: Tipo, metodos: dict[str, Any],
                 supers: dict[str, "Dicionario"]) -> None:
        self.classe = classe
        self.tipo = tipo
        self.metodos = metodos
        self.supers = supers

    def __getitem__(self, nome: str) -> Any:
        if nome in self.metodos:
            return self.metodos[nome]
        for s in self.supers.values():
            try:
                return s[nome]
            except KeyError:
                pass
        raise KeyError(f"{self.classe} não tem método {nome}")

    def __repr__(self) -> str:
        return f"<{self.classe} {mostrar(self.tipo)}>"


@dataclass
class Classe:
    nome: str
    metodos: tuple[str, ...]
    supers: tuple[str, ...] = ()
    # métodos padrão: recebem o dicionário final e devolvem a implementação
    padroes: dict[str, Callable[[Dicionario], Any]] = field(default_factory=dict)


@dataclass
class Instancia:
    classe: str
    ctor: str
    contexto: tuple[str | None, ...]   # classe exigida de cada argumento do tipo
    construir: Callable[..., dict[str, Any]]


class Sistema:
    def __init__(self) -> None:
        self.classes: dict[str, Classe] = {}
        self.instancias: dict[tuple[str, str], Instancia] = {}

    def classe(self, nome: str, metodos: tuple[str, ...], supers: tuple[str, ...] = (),
               padroes: dict[str, Callable[[Dicionario], Any]] | None = None) -> None:
        if nome in self.classes:
            raise ErroClasse(f"classe duplicada: {nome}")
        for s in supers:
            if s not in self.classes:
                raise ErroClasse(f"superclasse desconhecida: {s}")
        padroes = padroes or {}
        if set(padroes) - set(metodos):
            raise ErroClasse("método padrão fora da classe")
        self.classes[nome] = Classe(nome, metodos, supers, padroes)

    def instancia(self, classe: str, ctor: str, construir: Callable[..., dict[str, Any]],
                  contexto: tuple[str | None, ...] = ()) -> None:
        if classe not in self.classes:
            raise ErroClasse(f"classe desconhecida: {classe}")
        if (classe, ctor) in self.instancias:
            raise ErroClasse(f"instância duplicada: {classe} {ctor}")
        self.instancias[(classe, ctor)] = Instancia(classe, ctor, contexto, construir)

    def resolver(self, classe: str, tipo: Tipo) -> Dicionario:
        """Constrói (recursivamente) o dicionário de `classe` para `tipo`."""
        if classe not in self.classes:
            raise ErroClasse(f"classe desconhecida: {classe}")
        if isinstance(tipo, TVar):
            raise ErroClasse(f"tipo ambíguo: {mostrar(tipo)}")
        inst = self.instancias.get((classe, tipo.nome))
        if inst is None:
            raise ErroClasse(f"sem instância {classe} {mostrar(tipo)}")
        if len(inst.contexto) != len(tipo.args):
            raise ErroClasse(f"instância {classe} {tipo.nome}: aridade incompatível")
        ctx = [None if c is None else self.resolver(c, a)
               for c, a in zip(inst.contexto, tipo.args)]
        cls = self.classes[classe]
        supers = {s: self.resolver(s, tipo) for s in cls.supers}
        metodos = dict(inst.construir(*ctx))
        extras = set(metodos) - set(cls.metodos)
        if extras:
            raise ErroClasse(f"métodos fora da classe {classe}: {sorted(extras)}")
        d = Dicionario(classe, tipo, metodos, supers)
        for nome, padrao in cls.padroes.items():
            if nome not in metodos:
                metodos[nome] = padrao(d)
        faltam = set(cls.metodos) - set(metodos)
        if faltam:
            raise ErroClasse(f"instância {classe} {mostrar(tipo)} sem {sorted(faltam)}")
        return d


def sistema_padrao() -> Sistema:
    """Show, Eq, Ord (com Eq como superclasse) e Monoid para tipos usuais."""
    s = Sistema()
    s.classe("Show", ("mostrar",))
    s.classe("Eq", ("igual", "diferente"),
             padroes={"diferente": lambda d: lambda a, b: not d["igual"](a, b)})
    s.classe("Ord", ("menor_igual", "menor"), supers=("Eq",),
             padroes={"menor": lambda d: lambda a, b: d["menor_igual"](a, b)
                      and not d["igual"](a, b)})
    s.classe("Monoid", ("vazio", "somar"))

    for ctor, f in (("Int", str), ("Bool", lambda b: "verdadeiro" if b else "falso"),
                    ("Str", repr)):
        s.instancia("Show", ctor, lambda f=f: {"mostrar": f})
    s.instancia("Show", "List",
                lambda da: {"mostrar": lambda xs: "[" + ", ".join(map(da["mostrar"], xs)) + "]"},
                contexto=("Show",))
    s.instancia("Show", "*",
                lambda da, db: {"mostrar": lambda p: f"({da['mostrar'](p[0])}, {db['mostrar'](p[1])})"},
                contexto=("Show", "Show"))

    for ctor in ("Int", "Bool", "Str"):
        s.instancia("Eq", ctor, lambda: {"igual": lambda a, b: a == b})
        s.instancia("Ord", ctor, lambda: {"menor_igual": lambda a, b: a <= b})
    s.instancia("Eq", "List", lambda da: {"igual": lambda xs, ys: len(xs) == len(ys)
                and all(da["igual"](x, y) for x, y in zip(xs, ys))}, contexto=("Eq",))

    def ord_lista(da):
        def menor_igual(xs, ys):  # ordem lexicográfica
            for x, y in zip(xs, ys):
                if not da["igual"](x, y):
                    return da["menor_igual"](x, y)
            return len(xs) <= len(ys)
        return {"menor_igual": menor_igual}
    s.instancia("Ord", "List", ord_lista, contexto=("Ord",))

    s.instancia("Eq", "*", lambda da, db: {"igual": lambda p, q: da["igual"](p[0], q[0])
                and db["igual"](p[1], q[1])}, contexto=("Eq", "Eq"))
    s.instancia("Ord", "*", lambda da, db: {"menor_igual": lambda p, q: da["menor"](p[0], q[0])
                or (da["igual"](p[0], q[0]) and db["menor_igual"](p[1], q[1]))},
                contexto=("Ord", "Ord"))

    s.instancia("Monoid", "Int", lambda: {"vazio": 0, "somar": lambda a, b: a + b})
    s.instancia("Monoid", "Str", lambda: {"vazio": "", "somar": lambda a, b: a + b})
    s.instancia("Monoid", "List", lambda _: {"vazio": [], "somar": lambda a, b: a + b},
                contexto=(None,))
    return s


# Funções genéricas escritas contra dicionários (tradução de `Ord a => [a] -> [a]`).
def ordenar(d_ord: Dicionario, xs: list) -> list:
    r = list(xs)
    for i in range(1, len(r)):  # inserção estável
        x, j = r[i], i - 1
        while j >= 0 and not d_ord["menor_igual"](r[j], x):
            r[j + 1] = r[j]
            j -= 1
        r[j + 1] = x
    return r


def mconcat(d_monoid: Dicionario, xs: list) -> Any:
    acc = d_monoid["vazio"]
    for x in xs:
        acc = d_monoid["somar"](acc, x)
    return acc

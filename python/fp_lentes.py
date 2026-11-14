"""Lentes (get/set/over, composição) e prismas sobre dados imutáveis."""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any, Callable, Optional, Type


@dataclass(frozen=True)
class Lente:
    ver: Callable[[Any], Any]
    definir: Callable[[Any, Any], Any]  # (estrutura, novo_valor) -> estrutura

    def over(self, f: Callable[[Any], Any], s: Any) -> Any:
        return self.definir(s, f(self.ver(s)))

    def compor(self, interna: "Lente") -> "Lente":
        """self focaliza o externo; `interna` focaliza dentro do resultado."""
        return Lente(
            lambda s: interna.ver(self.ver(s)),
            lambda s, v: self.definir(s, interna.definir(self.ver(s), v)),
        )

    def __matmul__(self, interna: "Lente") -> "Lente":
        return self.compor(interna)


def lente_campo(nome: str) -> Lente:
    """Lente para atributo de dataclass (frozen) via dataclasses.replace."""
    return Lente(
        lambda s: getattr(s, nome),
        lambda s, v: dataclasses.replace(s, **{nome: v}),
    )


def lente_chave(chave: Any) -> Lente:
    """Lente para chave de dict; set devolve novo dict (cópia rasa)."""
    def definir(s: dict, v: Any) -> dict:
        novo = dict(s)
        novo[chave] = v
        return novo
    return Lente(lambda s: s[chave], definir)


def lente_indice(i: int) -> Lente:
    """Lente para posição de tupla ou lista; devolve o mesmo tipo."""
    def definir(s, v):
        copia = list(s)
        copia[i] = v
        return tuple(copia) if isinstance(s, tuple) else copia
    return Lente(lambda s: s[i], definir)


IDENTIDADE = Lente(lambda s: s, lambda s, v: v)


def compor_todas(*lentes: Lente) -> Lente:
    r = IDENTIDADE
    for l in lentes:
        r = r.compor(l)
    return r


@dataclass(frozen=True)
class Prisma:
    """Foco que pode não existir: preview devolve None se não casar."""
    preview: Callable[[Any], Optional[Any]]
    review: Callable[[Any], Any]

    def over(self, f: Callable[[Any], Any], s: Any) -> Any:
        v = self.preview(s)
        return s if v is None else self.review(f(v))

    def definir(self, s: Any, novo: Any) -> Any:
        return s if self.preview(s) is None else self.review(novo)

    def compor(self, interno: "Prisma") -> "Prisma":
        def preview(s):
            v = self.preview(s)
            return None if v is None else interno.preview(v)
        return Prisma(preview, lambda a: self.review(interno.review(a)))

    def compor_lente(self, lente: Lente) -> "Prisma":
        """Prisma seguido de lente (resulta em traversal parcial: set via over)."""
        def preview(s):
            v = self.preview(s)
            return None if v is None else lente.ver(v)

        def review(a):
            raise TypeError("prisma+lente não admite review")
        p = Prisma(preview, review)
        object.__setattr__(p, "over", lambda f, s: self._over_lente(lente, f, s))
        return p

    def _over_lente(self, lente: Lente, f: Callable[[Any], Any], s: Any) -> Any:
        v = self.preview(s)
        return s if v is None else self.review(lente.over(f, v))


def prisma_tipo(cls: Type) -> Prisma:
    """Casa se o valor é instância de cls."""
    return Prisma(lambda s: s if isinstance(s, cls) else None, lambda a: a)


def prisma_inteiro_de_texto() -> Prisma:
    """Texto <-> int: preview só casa se o texto for um inteiro canônico."""
    def preview(s):
        if not isinstance(s, str):
            return None
        try:
            n = int(s)
        except ValueError:
            return None
        return n if str(n) == s else None
    return Prisma(preview, str)

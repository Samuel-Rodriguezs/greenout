"""Zippers: navegação e edição persistente em listas e árvores binárias."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Callable, List, Optional, Tuple


# --- Zipper de lista ---------------------------------------------------------

@dataclass(frozen=True)
class ZipperLista:
    """esq guarda os elementos anteriores em ordem reversa (mais próximo primeiro)."""
    esq: Tuple[Any, ...]
    foco: Any
    dir: Tuple[Any, ...]

    @staticmethod
    def de_lista(itens) -> Optional["ZipperLista"]:
        xs = tuple(itens)
        if not xs:
            return None
        return ZipperLista((), xs[0], xs[1:])

    def esquerda(self) -> Optional["ZipperLista"]:
        if not self.esq:
            return None
        return ZipperLista(self.esq[1:], self.esq[0], (self.foco,) + self.dir)

    def direita(self) -> Optional["ZipperLista"]:
        if not self.dir:
            return None
        return ZipperLista((self.foco,) + self.esq, self.dir[0], self.dir[1:])

    def modificar(self, f: Callable[[Any], Any]) -> "ZipperLista":
        return replace(self, foco=f(self.foco))

    def definir(self, valor: Any) -> "ZipperLista":
        return replace(self, foco=valor)

    def inserir_esquerda(self, valor: Any) -> "ZipperLista":
        return replace(self, esq=(valor,) + self.esq)

    def inserir_direita(self, valor: Any) -> "ZipperLista":
        return replace(self, dir=(valor,) + self.dir)

    def remover(self) -> Optional["ZipperLista"]:
        """Remove o foco; novo foco é o vizinho da direita (ou da esquerda)."""
        if self.dir:
            return ZipperLista(self.esq, self.dir[0], self.dir[1:])
        if self.esq:
            return ZipperLista(self.esq[1:], self.esq[0], ())
        return None

    def inicio(self) -> "ZipperLista":
        z = self
        while z.esq:
            z = z.esquerda()
        return z

    def posicao(self) -> int:
        return len(self.esq)

    def para_lista(self) -> List[Any]:
        return list(reversed(self.esq)) + [self.foco] + list(self.dir)


# --- Zipper de árvore binária ---------------------------------------------------

@dataclass(frozen=True)
class Arv:
    valor: Any
    esq: Optional["Arv"] = None
    dir: Optional["Arv"] = None


@dataclass(frozen=True)
class Migalha:
    """Contexto deixado ao descer: de qual lado fomos, valor do pai e o irmão."""
    lado: str  # "esq" ou "dir"
    valor: Any
    irmao: Optional[Arv]


@dataclass(frozen=True)
class ZipperArvore:
    foco: Arv
    trilha: Tuple[Migalha, ...] = ()

    def descer_esq(self) -> Optional["ZipperArvore"]:
        if self.foco.esq is None:
            return None
        m = Migalha("esq", self.foco.valor, self.foco.dir)
        return ZipperArvore(self.foco.esq, (m,) + self.trilha)

    def descer_dir(self) -> Optional["ZipperArvore"]:
        if self.foco.dir is None:
            return None
        m = Migalha("dir", self.foco.valor, self.foco.esq)
        return ZipperArvore(self.foco.dir, (m,) + self.trilha)

    def subir(self) -> Optional["ZipperArvore"]:
        if not self.trilha:
            return None
        m, resto = self.trilha[0], self.trilha[1:]
        if m.lado == "esq":
            pai = Arv(m.valor, self.foco, m.irmao)
        else:
            pai = Arv(m.valor, m.irmao, self.foco)
        return ZipperArvore(pai, resto)

    def modificar_valor(self, f: Callable[[Any], Any]) -> "ZipperArvore":
        return ZipperArvore(replace(self.foco, valor=f(self.foco.valor)), self.trilha)

    def substituir(self, sub: Optional[Arv]) -> "ZipperArvore":
        """Troca a subárvore em foco (sub não pode ser None na raiz)."""
        if sub is None:
            raise ValueError("foco não pode ser vazio")
        return ZipperArvore(sub, self.trilha)

    def raiz(self) -> "ZipperArvore":
        z = self
        while z.trilha:
            z = z.subir()
        return z

    def para_arvore(self) -> Arv:
        return self.raiz().foco

    def profundidade(self) -> int:
        return len(self.trilha)

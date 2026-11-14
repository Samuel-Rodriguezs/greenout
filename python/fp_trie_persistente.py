"""Mapa persistente por trie de hash (estilo HAMT, 32 filhos por nó)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator, Optional, Tuple, Union

BITS = 5
LARGURA = 1 << BITS
MASCARA = LARGURA - 1
HASH_MASK = (1 << 64) - 1
BITS_HASH = 64


@dataclass(frozen=True)
class Folha:
    h: int
    chave: Any
    valor: Any


@dataclass(frozen=True)
class Colisao:
    """Chaves distintas com o mesmo hash completo."""
    h: int
    itens: Tuple[Tuple[Any, Any], ...]


@dataclass(frozen=True)
class No:
    filhos: Tuple[Any, ...]


Entrada = Union[Folha, Colisao, No, None]


def _hash(chave: Any) -> int:
    return hash(chave) & HASH_MASK


def _novo_no(filhos: list) -> No:
    return No(tuple(filhos))


def _mesclar(e1: Union[Folha, Colisao], e2: Union[Folha, Colisao], shift: int) -> No:
    """Cria subárvore que separa duas entradas com hashes possivelmente distintos."""
    i1, i2 = (e1.h >> shift) & MASCARA, (e2.h >> shift) & MASCARA
    filhos: list = [None] * LARGURA
    if i1 != i2:
        filhos[i1], filhos[i2] = e1, e2
    else:
        filhos[i1] = _mesclar(e1, e2, shift + BITS)
    return _novo_no(filhos)


def _inserir(no: No, h: int, shift: int, chave: Any, valor: Any) -> Tuple[No, bool]:
    idx = (h >> shift) & MASCARA
    e = no.filhos[idx]
    if e is None:
        novo, adicionou = Folha(h, chave, valor), True
    elif isinstance(e, No):
        novo, adicionou = _inserir(e, h, shift + BITS, chave, valor)
    elif e.h != h:
        novo, adicionou = _mesclar(e, Folha(h, chave, valor), shift + BITS), True
    elif isinstance(e, Folha):
        if e.chave == chave:
            novo, adicionou = Folha(h, chave, valor), False
        else:
            novo, adicionou = Colisao(h, ((e.chave, e.valor), (chave, valor))), True
    else:  # Colisao do mesmo hash
        itens = list(e.itens)
        for i, (k, _) in enumerate(itens):
            if k == chave:
                itens[i] = (chave, valor)
                novo, adicionou = Colisao(h, tuple(itens)), False
                break
        else:
            novo, adicionou = Colisao(h, e.itens + ((chave, valor),)), True
    filhos = list(no.filhos)
    filhos[idx] = novo
    return _novo_no(filhos), adicionou


def _buscar(no: No, h: int, chave: Any) -> Tuple[bool, Any]:
    shift = 0
    while True:
        e = no.filhos[(h >> shift) & MASCARA]
        if e is None:
            return False, None
        if isinstance(e, No):
            no, shift = e, shift + BITS
            continue
        if e.h != h:
            return False, None
        if isinstance(e, Folha):
            return (True, e.valor) if e.chave == chave else (False, None)
        for k, v in e.itens:
            if k == chave:
                return True, v
        return False, None


def _remover(no: No, h: int, shift: int, chave: Any) -> Tuple[Optional[No], bool]:
    idx = (h >> shift) & MASCARA
    e = no.filhos[idx]
    if e is None:
        return no, False
    if isinstance(e, No):
        novo, removeu = _remover(e, h, shift + BITS, chave)
        if not removeu:
            return no, False
    elif e.h != h:
        return no, False
    elif isinstance(e, Folha):
        if e.chave != chave:
            return no, False
        novo = None
    else:
        resto = tuple(it for it in e.itens if it[0] != chave)
        if len(resto) == len(e.itens):
            return no, False
        novo = Folha(h, *resto[0]) if len(resto) == 1 else Colisao(h, resto)
    filhos = list(no.filhos)
    filhos[idx] = novo
    if all(f is None for f in filhos):
        return None, True
    return _novo_no(filhos), True


def _percorrer(no: No) -> Iterator[Tuple[Any, Any]]:
    pilha = [no]
    while pilha:
        atual = pilha.pop()
        for e in reversed(atual.filhos):
            if e is None:
                continue
            if isinstance(e, No):
                pilha.append(e)
            elif isinstance(e, Folha):
                yield e.chave, e.valor
            else:
                yield from e.itens


_RAIZ_VAZIA = No((None,) * LARGURA)


class MapaPersistente:
    """Mapa imutável: `com` e `sem` devolvem novas versões compartilhando nós."""

    __slots__ = ("_raiz", "_tam")

    def __init__(self, _raiz: No = _RAIZ_VAZIA, _tam: int = 0):
        object.__setattr__(self, "_raiz", _raiz)
        object.__setattr__(self, "_tam", _tam)

    def __setattr__(self, nome: str, valor: Any) -> None:
        raise AttributeError("MapaPersistente é imutável")

    @staticmethod
    def de_dict(d: dict) -> "MapaPersistente":
        m = MapaPersistente()
        for k, v in d.items():
            m = m.com(k, v)
        return m

    def com(self, chave: Any, valor: Any) -> "MapaPersistente":
        raiz, adicionou = _inserir(self._raiz, _hash(chave), 0, chave, valor)
        return MapaPersistente(raiz, self._tam + (1 if adicionou else 0))

    def sem(self, chave: Any) -> "MapaPersistente":
        raiz, removeu = _remover(self._raiz, _hash(chave), 0, chave)
        if not removeu:
            return self
        return MapaPersistente(raiz if raiz is not None else _RAIZ_VAZIA, self._tam - 1)

    def get(self, chave: Any, padrao: Any = None) -> Any:
        achou, v = _buscar(self._raiz, _hash(chave), chave)
        return v if achou else padrao

    def __getitem__(self, chave: Any) -> Any:
        achou, v = _buscar(self._raiz, _hash(chave), chave)
        if not achou:
            raise KeyError(chave)
        return v

    def __contains__(self, chave: Any) -> bool:
        return _buscar(self._raiz, _hash(chave), chave)[0]

    def __len__(self) -> int:
        return self._tam

    def items(self) -> Iterator[Tuple[Any, Any]]:
        return _percorrer(self._raiz)

    def __iter__(self) -> Iterator[Any]:
        return (k for k, _ in self.items())

    def para_dict(self) -> dict:
        return dict(self.items())

    def __eq__(self, outro: object) -> bool:
        if not isinstance(outro, MapaPersistente):
            return NotImplemented
        return len(self) == len(outro) and self.para_dict() == outro.para_dict()

    __hash__ = None  # type: ignore[assignment]

    def __repr__(self) -> str:
        return "MapaPersistente(" + repr(self.para_dict()) + ")"

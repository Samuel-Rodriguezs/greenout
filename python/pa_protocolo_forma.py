"""typing.Protocol (tipagem estrutural) e funções genéricas sobre ele."""
import math
from dataclasses import dataclass
from typing import Iterable, Optional, Protocol, TypeVar, runtime_checkable


@runtime_checkable
class Forma(Protocol):
    def area(self) -> float: ...


@dataclass
class Retangulo:
    largura: float
    altura: float

    def area(self) -> float:
        return self.largura * self.altura


@dataclass
class Circulo:
    raio: float

    def area(self) -> float:
        return math.pi * self.raio ** 2


F = TypeVar("F", bound=Forma)


def maior_forma(formas: Iterable[F]) -> Optional[F]:
    """Forma de maior área; None se vazio."""
    return max(formas, key=lambda f: f.area(), default=None)


def area_total(formas: Iterable[Forma]) -> float:
    total = 0.0
    for f in formas:
        if not isinstance(f, Forma):
            raise TypeError(f"{f!r} não implementa Forma")
        total += f.area()
    return total

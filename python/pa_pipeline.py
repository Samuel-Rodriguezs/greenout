"""Pipeline preguiçoso de geradores com Generic."""
from typing import Callable, Generic, Iterable, Iterator, List, TypeVar

T = TypeVar("T")
U = TypeVar("U")


class Pipeline(Generic[T]):
    def __init__(self, fonte: Iterable[T]) -> None:
        self._fonte = fonte

    def mapear(self, f: Callable[[T], U]) -> "Pipeline[U]":
        return Pipeline(f(x) for x in self._fonte)

    def filtrar(self, pred: Callable[[T], bool]) -> "Pipeline[T]":
        return Pipeline(x for x in self._fonte if pred(x))

    def pegar(self, n: int) -> "Pipeline[T]":
        if n < 0:
            raise ValueError("n deve ser >= 0")

        def gen() -> Iterator[T]:
            if n == 0:
                return
            for i, x in enumerate(self._fonte, 1):
                yield x
                if i >= n:
                    return

        return Pipeline(gen())

    def achatar(self) -> "Pipeline":
        return Pipeline(y for x in self._fonte for y in x)  # type: ignore[attr-defined]

    def para_lista(self) -> List[T]:
        return list(self._fonte)

    def __iter__(self) -> Iterator[T]:
        return iter(self._fonte)

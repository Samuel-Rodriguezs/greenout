"""Futuro/Promessa próprios com callbacks e encadeamento."""
from __future__ import annotations

import threading
from typing import Any, Callable

_PENDENTE, _RESOLVIDO, _REJEITADO = "pendente", "resolvido", "rejeitado"


class Futuro:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._evento = threading.Event()
        self._estado = _PENDENTE
        self._valor: Any = None
        self._erro: BaseException | None = None
        self._callbacks: list[Callable[["Futuro"], None]] = []

    @property
    def estado(self) -> str:
        return self._estado

    def pronto(self) -> bool:
        return self._estado != _PENDENTE

    def _concluir(self, estado: str, valor: Any, erro: BaseException | None) -> None:
        with self._lock:
            if self._estado != _PENDENTE:
                raise RuntimeError("futuro já concluído")
            self._estado, self._valor, self._erro = estado, valor, erro
            cbs, self._callbacks = self._callbacks, []
        self._evento.set()
        for cb in cbs:
            cb(self)

    def resolver(self, valor: Any) -> None:
        self._concluir(_RESOLVIDO, valor, None)

    def rejeitar(self, erro: BaseException) -> None:
        self._concluir(_REJEITADO, None, erro)

    def resultado(self, timeout: float | None = None) -> Any:
        if not self._evento.wait(timeout):
            raise TimeoutError("futuro pendente")
        if self._erro is not None:
            raise self._erro
        return self._valor

    def ao_concluir(self, cb: Callable[["Futuro"], None]) -> None:
        with self._lock:
            if self._estado == _PENDENTE:
                self._callbacks.append(cb)
                return
        cb(self)

    def entao(self, fn: Callable[[Any], Any]) -> "Futuro":
        """Retorna novo futuro com fn aplicada ao valor (propaga erros)."""
        novo = Futuro()

        def tratar(f: "Futuro") -> None:
            if f._erro is not None:
                novo.rejeitar(f._erro)
                return
            try:
                novo.resolver(fn(f._valor))
            except BaseException as exc:  # noqa: BLE001
                novo.rejeitar(exc)

        self.ao_concluir(tratar)
        return novo

    def recuperar(self, fn: Callable[[BaseException], Any]) -> "Futuro":
        novo = Futuro()

        def tratar(f: "Futuro") -> None:
            if f._erro is None:
                novo.resolver(f._valor)
                return
            try:
                novo.resolver(fn(f._erro))
            except BaseException as exc:  # noqa: BLE001
                novo.rejeitar(exc)

        self.ao_concluir(tratar)
        return novo


def executar(fn: Callable[..., Any], *args: Any) -> Futuro:
    """Executa fn em uma thread e devolve o futuro."""
    f = Futuro()

    def alvo() -> None:
        try:
            f.resolver(fn(*args))
        except BaseException as exc:  # noqa: BLE001
            f.rejeitar(exc)

    threading.Thread(target=alvo, daemon=True).start()
    return f


def todos(futuros: list[Futuro]) -> Futuro:
    """Resolve com a lista de valores; rejeita no primeiro erro."""
    out = Futuro()
    if not futuros:
        out.resolver([])
        return out
    valores: list[Any] = [None] * len(futuros)
    restantes = [len(futuros)]
    lock = threading.Lock()

    def marcar(i: int) -> Callable[[Futuro], None]:
        def cb(f: Futuro) -> None:
            with lock:
                if out.pronto():
                    return
                if f._erro is not None:
                    out.rejeitar(f._erro)
                    return
                valores[i] = f._valor
                restantes[0] -= 1
                if restantes[0] == 0:
                    out.resolver(valores)

        return cb

    for i, f in enumerate(futuros):
        f.ao_concluir(marcar(i))
    return out

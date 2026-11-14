"""Injeção de dependências por assinatura (anotações de tipo ou nome do parâmetro)."""
from __future__ import annotations

import inspect
import typing
from typing import Any, Callable


class ErroInjecao(Exception):
    pass


class Container:
    """Registra provedores por tipo ou nome e resolve argumentos de funções/classes.

    Escopos: "singleton" (uma instância), "transiente" (nova a cada resolução),
    "requisicao" (uma por escopo criado com `novo_escopo`).
    """

    ESCOPOS = ("singleton", "transiente", "requisicao")

    def __init__(self, pai: "Container | None" = None) -> None:
        self._provedores: dict[Any, tuple[Callable[..., Any], str]] = {}
        self._singletons: dict[Any, Any] = {}
        self._escopo: dict[Any, Any] = {}
        self._pai = pai
        self._resolvendo: list[Any] = []

    def registrar(self, chave: Any, provedor: Callable[..., Any] | None = None,
                  escopo: str = "singleton", instancia: Any = None) -> None:
        if escopo not in self.ESCOPOS:
            raise ValueError(f"escopo inválido: {escopo}")
        if instancia is not None:
            self._singletons[chave] = instancia
            self._provedores[chave] = (lambda: instancia, "singleton")
            return
        if provedor is None:
            if not callable(chave):
                raise ValueError("informe um provedor ou use uma classe como chave")
            provedor = chave
        self._provedores[chave] = (provedor, escopo)

    def novo_escopo(self) -> "Container":
        """Escopo de requisição: compartilha registros e singletons, isola instâncias 'requisicao'."""
        return Container(pai=self)

    def _buscar(self, chave: Any) -> tuple["Container", tuple[Callable[..., Any], str]] | None:
        c: Container | None = self
        while c is not None:
            if chave in c._provedores:
                return c, c._provedores[chave]
            c = c._pai
        return None

    def resolver(self, chave: Any) -> Any:
        achado = self._buscar(chave)
        if achado is None:
            if inspect.isclass(chave):  # auto-wiring de classes concretas
                return self._com_ciclo(chave, lambda: self.chamar(chave))
            raise ErroInjecao(f"sem provedor para {getattr(chave, '__name__', chave)!r}")
        dono, (provedor, escopo) = achado
        if escopo == "singleton":
            if chave not in dono._singletons:
                dono._singletons[chave] = self._com_ciclo(chave, lambda: self.chamar(provedor))
            return dono._singletons[chave]
        if escopo == "requisicao":
            if chave not in self._escopo:
                self._escopo[chave] = self._com_ciclo(chave, lambda: self.chamar(provedor))
            return self._escopo[chave]
        return self._com_ciclo(chave, lambda: self.chamar(provedor))

    def _com_ciclo(self, chave: Any, criar: Callable[[], Any]) -> Any:
        raiz = self
        if chave in raiz._resolvendo:
            ciclo = " -> ".join(getattr(c, "__name__", str(c)) for c in raiz._resolvendo + [chave])
            raise ErroInjecao(f"dependência circular: {ciclo}")
        raiz._resolvendo.append(chave)
        try:
            return criar()
        finally:
            raiz._resolvendo.pop()

    def chamar(self, fn: Callable[..., Any], **explicitos: Any) -> Any:
        """Chama fn resolvendo parâmetros: explícitos > tipo anotado > nome > valor padrão."""
        try:
            dicas = typing.get_type_hints(fn.__init__ if inspect.isclass(fn) else fn)
        except Exception:
            dicas = {}
        sig = inspect.signature(fn)
        args: dict[str, Any] = {}
        for nome, p in sig.parameters.items():
            if p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD):
                continue
            if nome in explicitos:
                args[nome] = explicitos[nome]
                continue
            tipo = dicas.get(nome)
            if tipo is not None and self._buscar(tipo) is not None:
                args[nome] = self.resolver(tipo)
            elif self._buscar(nome) is not None:
                args[nome] = self.resolver(nome)
            elif tipo is not None and inspect.isclass(tipo) and tipo.__module__ != "builtins" \
                    and p.default is p.empty:
                args[nome] = self.resolver(tipo)
            elif p.default is not p.empty:
                continue
            else:
                raise ErroInjecao(f"não foi possível resolver o parâmetro {nome!r} de "
                                  f"{getattr(fn, '__name__', fn)}")
        return fn(**args)

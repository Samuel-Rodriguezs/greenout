"""Níveis de isolamento sobre um armazenamento chave-valor, para demonstrar anomalias.

READ_UNCOMMITTED : lê escritas pendentes de outras transações (leitura suja).
READ_COMMITTED   : lê o último valor comitado a cada leitura (não repetível, fantasmas).
REPEATABLE_READ  : lê de um snapshot do início; escrita-escrita concorrente aborta
                   (first-committer-wins), então não há atualização perdida; write skew é possível.
SERIALIZABLE     : como RR, mas valida no commit que tudo que a transação leu
                   (chaves e varreduras) não mudou desde o snapshot.
"""
from __future__ import annotations

from typing import Any, Callable, Optional

READ_UNCOMMITTED = "READ_UNCOMMITTED"
READ_COMMITTED = "READ_COMMITTED"
REPEATABLE_READ = "REPEATABLE_READ"
SERIALIZABLE = "SERIALIZABLE"
NIVEIS = (READ_UNCOMMITTED, READ_COMMITTED, REPEATABLE_READ, SERIALIZABLE)

_AUSENTE = object()


class ErroSerializacao(Exception):
    pass


class BancoIsolamento:
    def __init__(self, dados: Optional[dict[Any, Any]] = None) -> None:
        self.comitado: dict[Any, Any] = dict(dados or {})
        self.versao_chave: dict[Any, int] = {k: 0 for k in self.comitado}
        self.relogio = 0
        self.ativas: list["Tx"] = []

    def iniciar(self, nivel: str = READ_COMMITTED) -> "Tx":
        if nivel not in NIVEIS:
            raise ValueError(f"nível desconhecido: {nivel}")
        t = Tx(self, nivel)
        self.ativas.append(t)
        return t


class Tx:
    def __init__(self, banco: BancoIsolamento, nivel: str) -> None:
        self.banco = banco
        self.nivel = nivel
        self.snapshot = dict(banco.comitado)
        self.snapshot_ts = banco.relogio
        self.escritas: dict[Any, Any] = {}
        self.leituras: set[Any] = set()
        self.varreduras: list[tuple[Callable[[Any, Any], bool], frozenset]] = []
        self.ativa = True

    def _base(self) -> dict[Any, Any]:
        if self.nivel in (REPEATABLE_READ, SERIALIZABLE):
            return self.snapshot
        return self.banco.comitado

    def ler(self, chave: Any, padrao: Any = None) -> Any:
        if chave in self.escritas:
            v = self.escritas[chave]
            return padrao if v is _AUSENTE else v
        self.leituras.add(chave)
        if self.nivel == READ_UNCOMMITTED:
            for outra in reversed(self.banco.ativas):
                if outra is not self and chave in outra.escritas:
                    v = outra.escritas[chave]
                    return padrao if v is _AUSENTE else v
        return self._base().get(chave, padrao)

    def escrever(self, chave: Any, valor: Any) -> None:
        self.escritas[chave] = valor

    def apagar(self, chave: Any) -> None:
        self.escritas[chave] = _AUSENTE

    def varrer(self, predicado: Callable[[Any, Any], bool]) -> dict[Any, Any]:
        """SELECT ... WHERE predicado(chave, valor)."""
        visivel = dict(self._base())
        if self.nivel == READ_UNCOMMITTED:
            for outra in self.banco.ativas:
                if outra is not self:
                    for k, v in outra.escritas.items():
                        if v is _AUSENTE:
                            visivel.pop(k, None)
                        else:
                            visivel[k] = v
        for k, v in self.escritas.items():
            if v is _AUSENTE:
                visivel.pop(k, None)
            else:
                visivel[k] = v
        res = {k: v for k, v in visivel.items() if predicado(k, v)}
        lido = frozenset((k, v) for k, v in self._base().items() if predicado(k, v))
        self.varreduras.append((predicado, lido))
        return res

    def _encerrar(self) -> None:
        self.ativa = False
        if self in self.banco.ativas:
            self.banco.ativas.remove(self)

    def abortar(self) -> None:
        self.escritas.clear()
        self._encerrar()

    def commit(self) -> None:
        if not self.ativa:
            raise RuntimeError("transação encerrada")
        b = self.banco
        if self.nivel in (REPEATABLE_READ, SERIALIZABLE):
            for k in self.escritas:
                if b.versao_chave.get(k, 0) > self.snapshot_ts:
                    self._encerrar()
                    raise ErroSerializacao(f"escrita concorrente em {k!r}")
        if self.nivel == SERIALIZABLE:
            for k in self.leituras:
                if b.versao_chave.get(k, 0) > self.snapshot_ts:
                    self._encerrar()
                    raise ErroSerializacao(f"leitura de {k!r} ficou obsoleta")
            for pred, lido in self.varreduras:
                atual = frozenset((k, v) for k, v in b.comitado.items() if pred(k, v))
                if atual != lido:
                    self._encerrar()
                    raise ErroSerializacao("predicado lido foi alterado (fantasma)")
        if self.escritas:
            b.relogio += 1
        for k, v in self.escritas.items():
            if v is _AUSENTE:
                b.comitado.pop(k, None)
            else:
                b.comitado[k] = v
            b.versao_chave[k] = b.relogio
        self._encerrar()

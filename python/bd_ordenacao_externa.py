"""ORDER BY com ordenação externa por mesclagem (runs em arquivos temporários).

Fase 1: lê no máximo `tam_run` linhas por vez, ordena em memória e grava um run.
Fase 2: mescla até `fan_in` runs por passada (várias passadas se houver mais runs).
A ordenação é estável. Arquivos temporários são removidos mesmo em caso de erro.
"""
from __future__ import annotations

import heapq
import os
import pickle
import tempfile
from typing import Any, Callable, Iterable, Iterator, Optional


class _Reversor:
    """Inverte a ordem de um valor (para ORDER BY ... DESC com chaves compostas)."""
    __slots__ = ("v",)

    def __init__(self, v: Any) -> None:
        self.v = v

    def __lt__(self, o: "_Reversor") -> bool:
        return o.v < self.v

    def __eq__(self, o: object) -> bool:
        return isinstance(o, _Reversor) and self.v == o.v


def _ler_run(caminho: str) -> Iterator[Any]:
    with open(caminho, "rb") as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                return


class OrdenadorExterno:
    def __init__(self, tam_run: int = 1000, fan_in: int = 8,
                 chave: Optional[Callable[[Any], Any]] = None, decrescente: bool = False,
                 diretorio: Optional[str] = None) -> None:
        if tam_run < 1 or fan_in < 2:
            raise ValueError("tam_run >= 1 e fan_in >= 2")
        self.tam_run, self.fan_in = tam_run, fan_in
        self.chave = chave or (lambda x: x)
        self.decrescente = decrescente
        self.diretorio = diretorio
        self.runs_criados = 0
        self.passadas = 0

    def _k(self, x: Any) -> Any:
        return _Reversor(self.chave(x)) if self.decrescente else self.chave(x)

    def _gravar(self, d: str, itens: Iterable[Any]) -> str:
        caminho = os.path.join(d, f"run{self.runs_criados:06d}.bin")
        self.runs_criados += 1
        with open(caminho, "wb") as f:
            for it in itens:
                pickle.dump(it, f, protocol=pickle.HIGHEST_PROTOCOL)
        return caminho

    def ordenar(self, itens: Iterable[Any]) -> Iterator[Any]:
        """Gerador: os arquivos temporários vivem até o fim da iteração."""
        self.runs_criados = self.passadas = 0
        with tempfile.TemporaryDirectory(dir=self.diretorio) as d:
            runs: list[str] = []
            buf: list[Any] = []
            for it in itens:
                buf.append(it)
                if len(buf) >= self.tam_run:
                    buf.sort(key=self._k)
                    runs.append(self._gravar(d, buf))
                    buf = []
            if not runs:  # coube na memória: nem toca o disco
                buf.sort(key=self._k)
                yield from buf
                return
            if buf:
                buf.sort(key=self._k)
                runs.append(self._gravar(d, buf))
            while len(runs) > self.fan_in:
                self.passadas += 1
                proximos = []
                for i in range(0, len(runs), self.fan_in):
                    grupo = runs[i:i + self.fan_in]
                    if len(grupo) == 1:
                        proximos.append(grupo[0])
                        continue
                    proximos.append(self._gravar(d, heapq.merge(*(_ler_run(r) for r in grupo), key=self._k)))
                    for r in grupo:
                        os.remove(r)
                runs = proximos
            self.passadas += 1
            yield from heapq.merge(*(_ler_run(r) for r in runs), key=self._k)


def ordenar_externo(itens: Iterable[Any], **kw: Any) -> list[Any]:
    return list(OrdenadorExterno(**kw).ordenar(itens))

"""Context managers úteis: diretório de trabalho, transação e supressão com registro."""
import contextlib
import os
from typing import Any, Dict, Iterator, List


@contextlib.contextmanager
def diretorio_atual(caminho: str) -> Iterator[str]:
    """Muda o cwd e sempre o restaura, mesmo com erro."""
    anterior = os.getcwd()
    os.chdir(caminho)
    try:
        yield os.getcwd()
    finally:
        os.chdir(anterior)


class Transacao:
    """Aplica alterações a um dict; desfaz tudo se ocorrer exceção."""

    def __init__(self, dados: Dict[str, Any]) -> None:
        self._dados = dados
        self._copia: Dict[str, Any] = {}

    def __enter__(self) -> Dict[str, Any]:
        self._copia = dict(self._dados)
        return self._dados

    def __exit__(self, tipo, valor, tb) -> bool:
        if tipo is not None:
            self._dados.clear()
            self._dados.update(self._copia)
        return False


@contextlib.contextmanager
def suprimir_registrando(erros: List[BaseException], *tipos: type) -> Iterator[None]:
    """Suprime exceções dos tipos dados, guardando-as na lista."""
    try:
        yield
    except tipos as e:
        erros.append(e)

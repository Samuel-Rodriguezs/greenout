"""Algoritmos de junção como operadores Volcano: nested loop, hash join e merge join.

Todos suportam `tipo="inner"` e `tipo="left"` (LEFT OUTER, preenchendo NULLs à direita).
Chaves NULL nunca casam em equi-junções (semântica SQL).
"""
from __future__ import annotations

from typing import Any, Optional

from bd_sql_parser import Coluna
from bd_volcano import ErroExecucao, Operador, avaliar, resolver

TIPOS = ("inner", "left")


class _JuncaoBase(Operador):
    def __init__(self, esq: Operador, dir: Operador, tipo: str) -> None:
        if tipo not in TIPOS:
            raise ErroExecucao(f"tipo de junção desconhecido: {tipo}")
        self.esq, self.dir, self.tipo = esq, dir, tipo
        self.esquema = esq.esquema + dir.esquema
        self._saida: list[tuple] = []
        self._i = 0
        self.comparacoes = 0

    def _nulos(self) -> tuple:
        return (None,) * len(self.dir.esquema)

    def abrir(self) -> None:
        self.comparacoes = 0
        self._saida = list(self._produzir())
        self._i = 0

    def proximo(self) -> Optional[tuple]:
        if self._i >= len(self._saida):
            return None
        self._i += 1
        return self._saida[self._i - 1]

    def fechar(self) -> None:
        self._saida = []

    def _produzir(self):  # pragma: no cover - sobrescrito
        raise NotImplementedError


class LoopAninhado(_JuncaoBase):
    def __init__(self, esq: Operador, dir: Operador, condicao: Any = None, tipo: str = "inner") -> None:
        super().__init__(esq, dir, tipo)
        self.condicao = condicao

    def _produzir(self):
        direita = self.dir.todas()
        for l in self.esq:
            casou = False
            for r in direita:
                self.comparacoes += 1
                junta = l + r
                if self.condicao is None or avaliar(self.condicao, self.esquema, junta) is True:
                    casou = True
                    yield junta
            if not casou and self.tipo == "left":
                yield l + self._nulos()


class _Equi(_JuncaoBase):
    def __init__(self, esq: Operador, dir: Operador, chave_esq: Coluna, chave_dir: Coluna,
                 tipo: str = "inner") -> None:
        super().__init__(esq, dir, tipo)
        self.ie = resolver(esq.esquema, chave_esq)
        self.id = resolver(dir.esquema, chave_dir)


class JuncaoHash(_Equi):
    """Constrói a tabela hash do lado direito e sonda com o esquerdo (O(n + m))."""

    def _produzir(self):
        tabela: dict[Any, list[tuple]] = {}
        for r in self.dir:
            k = r[self.id]
            if k is not None:
                tabela.setdefault(k, []).append(r)
        for l in self.esq:
            k = l[self.ie]
            casados = tabela.get(k, []) if k is not None else []
            self.comparacoes += len(casados)
            for r in casados:
                yield l + r
            if not casados and self.tipo == "left":
                yield l + self._nulos()


class JuncaoMesclagem(_Equi):
    """Ordena os dois lados pela chave e percorre-os em paralelo, tratando grupos repetidos."""

    def _produzir(self):
        esq = [l for l in self.esq]
        dir_ = sorted((r for r in self.dir if r[self.id] is not None), key=lambda r: r[self.id])
        com_chave = sorted((l for l in esq if l[self.ie] is not None), key=lambda l: l[self.ie])
        sem_chave = [l for l in esq if l[self.ie] is None]
        i = j = 0
        while i < len(com_chave):
            l = com_chave[i]
            k = l[self.ie]
            while j < len(dir_) and dir_[j][self.id] < k:
                j += 1
                self.comparacoes += 1
            fim = j
            while fim < len(dir_) and dir_[fim][self.id] == k:
                fim += 1
                self.comparacoes += 1
            grupo = dir_[j:fim]
            for r in grupo:
                yield l + r
            if not grupo and self.tipo == "left":
                yield l + self._nulos()
            i += 1  # j fica no início do grupo: a próxima linha esquerda com a mesma chave o reutiliza
        if self.tipo == "left":
            for l in sem_chave:
                yield l + self._nulos()

"""Validação declarativa de formulários."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_VERDADEIRO = {"1", "true", "on", "sim", "yes"}
_FALSO = {"0", "false", "off", "nao", "não", "no"}


@dataclass
class Campo:
    tipo: str = "str"  # str, int, float, bool, email
    obrigatorio: bool = True
    minimo: float | None = None  # valor (int/float) ou tamanho (str)
    maximo: float | None = None
    padrao: Any = None
    regex: str | None = None
    escolhas: tuple[Any, ...] | None = None
    validador: Callable[[Any], str | None] | None = None
    aparar: bool = True


class Formulario:
    campos: dict[str, Campo] = {}

    def __init__(self, campos: dict[str, Campo] | None = None) -> None:
        if campos is not None:
            self.campos = campos
        for nome, c in self.campos.items():
            if c.tipo not in ("str", "int", "float", "bool", "email"):
                raise ValueError(f"tipo desconhecido em {nome}: {c.tipo}")

    def validar(self, dados: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
        limpos: dict[str, Any] = {}
        erros: dict[str, str] = {}
        for nome, c in self.campos.items():
            bruto = dados.get(nome)
            if isinstance(bruto, str) and c.aparar:
                bruto = bruto.strip()
            if bruto is None or bruto == "":
                if c.tipo == "bool" and bruto is None:
                    limpos[nome] = False if c.padrao is None else c.padrao
                elif c.obrigatorio and c.padrao is None:
                    erros[nome] = "campo obrigatório"
                else:
                    limpos[nome] = c.padrao
                continue
            try:
                valor = self._converter(c, bruto)
                self._checar(c, valor)
            except ValueError as e:
                erros[nome] = str(e)
                continue
            limpos[nome] = valor
        return (limpos, erros) if not erros else ({}, erros)

    @staticmethod
    def _converter(c: Campo, bruto: Any) -> Any:
        try:
            if c.tipo == "int":
                if isinstance(bruto, bool):
                    raise ValueError
                return int(bruto)
            if c.tipo == "float":
                return float(bruto)
        except (TypeError, ValueError):
            raise ValueError(f"deve ser {'inteiro' if c.tipo == 'int' else 'número'}") from None
        if c.tipo == "bool":
            s = str(bruto).lower()
            if s in _VERDADEIRO:
                return True
            if s in _FALSO:
                return False
            raise ValueError("deve ser booleano")
        s = str(bruto)
        if c.tipo == "email" and not _EMAIL.match(s):
            raise ValueError("e-mail inválido")
        return s

    @staticmethod
    def _checar(c: Campo, valor: Any) -> None:
        medida = len(valor) if isinstance(valor, str) else valor
        unidade = " caracteres" if isinstance(valor, str) else ""
        if c.minimo is not None and medida < c.minimo:
            raise ValueError(f"mínimo de {c.minimo:g}{unidade}")
        if c.maximo is not None and medida > c.maximo:
            raise ValueError(f"máximo de {c.maximo:g}{unidade}")
        if c.regex and not re.fullmatch(c.regex, str(valor)):
            raise ValueError("formato inválido")
        if c.escolhas is not None and valor not in c.escolhas:
            raise ValueError("valor não permitido")
        if c.validador:
            msg = c.validador(valor)
            if msg:
                raise ValueError(msg)

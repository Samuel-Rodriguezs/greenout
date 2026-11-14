"""Roteador com parâmetros de caminho tipados: /usuarios/<int:id>."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable

from web_http import Requisicao, Resposta

CONVERSORES: dict[str, tuple[str, Callable[[str], Any]]] = {
    "str": (r"[^/]+", str),
    "int": (r"[0-9]+", int),
    "float": (r"[0-9]+(?:\.[0-9]+)?", float),
    "slug": (r"[a-z0-9]+(?:-[a-z0-9]+)*", str),
    "path": (r".+", str),
    "uuid": (r"[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}", str),
}

_PARAM = re.compile(r"<(?:(\w+):)?(\w+)>")


class RotaNaoEncontrada(Exception):
    pass


class MetodoNaoPermitido(Exception):
    def __init__(self, permitidos: list[str]) -> None:
        super().__init__("método não permitido")
        self.permitidos = permitidos


@dataclass
class Rota:
    padrao: str
    metodos: frozenset[str]
    manipulador: Callable[..., Any]
    nome: str
    regex: re.Pattern[str]
    conversores: dict[str, Callable[[str], Any]]


def compilar(padrao: str) -> tuple[re.Pattern[str], dict[str, Callable[[str], Any]]]:
    if not padrao.startswith("/"):
        raise ValueError("o padrão deve começar com '/'")
    conv: dict[str, Callable[[str], Any]] = {}
    partes: list[str] = []
    pos = 0
    for m in _PARAM.finditer(padrao):
        tipo, nome = m.group(1) or "str", m.group(2)
        if tipo not in CONVERSORES:
            raise ValueError(f"conversor desconhecido: {tipo}")
        if nome in conv:
            raise ValueError(f"parâmetro duplicado: {nome}")
        er, fn = CONVERSORES[tipo]
        partes.append(re.escape(padrao[pos:m.start()]))
        partes.append(f"(?P<{nome}>{er})")
        conv[nome] = fn
        pos = m.end()
    partes.append(re.escape(padrao[pos:]))
    return re.compile("^" + "".join(partes) + "$"), conv


class Roteador:
    def __init__(self) -> None:
        self.rotas: list[Rota] = []

    def adicionar(self, padrao: str, manipulador: Callable[..., Any],
                  metodos: tuple[str, ...] = ("GET",), nome: str | None = None) -> Rota:
        regex, conv = compilar(padrao)
        rota = Rota(padrao, frozenset(m.upper() for m in metodos), manipulador,
                    nome or manipulador.__name__, regex, conv)
        self.rotas.append(rota)
        return rota

    def rota(self, padrao: str, metodos: tuple[str, ...] = ("GET",), nome: str | None = None):
        def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.adicionar(padrao, fn, metodos, nome)
            return fn
        return deco

    def resolver(self, metodo: str, caminho: str) -> tuple[Rota, dict[str, Any]]:
        permitidos: set[str] = set()
        for r in self.rotas:
            m = r.regex.match(caminho)
            if not m:
                continue
            if metodo.upper() not in r.metodos and not (
                    metodo.upper() == "HEAD" and "GET" in r.metodos):
                permitidos |= r.metodos
                continue
            try:
                params = {k: r.conversores[k](v) for k, v in m.groupdict().items()}
            except ValueError:
                continue
            return r, params
        if permitidos:
            raise MetodoNaoPermitido(sorted(permitidos))
        raise RotaNaoEncontrada(caminho)

    def url_para(self, nome: str, **valores: Any) -> str:
        for r in self.rotas:
            if r.nome == nome:
                faltando = set(r.conversores) - set(valores)
                if faltando:
                    raise KeyError(f"faltam parâmetros: {sorted(faltando)}")
                return _PARAM.sub(lambda m: str(valores[m.group(2)]), r.padrao)
        raise KeyError(nome)

    def despachar(self, req: Requisicao) -> Resposta:
        try:
            rota, params = self.resolver(req.metodo, req.caminho)
        except RotaNaoEncontrada:
            return Resposta.de_texto("Não encontrado", 404)
        except MetodoNaoPermitido as e:
            r = Resposta.de_texto("Método não permitido", 405)
            r.cabecalhos["Allow"] = ", ".join(e.permitidos)
            return r
        req.params = params
        return normalizar(rota.manipulador(req, **params))


def normalizar(resultado: Any) -> Resposta:
    if isinstance(resultado, Resposta):
        return resultado
    if resultado is None:
        return Resposta(204)
    if isinstance(resultado, str):
        return Resposta.de_texto(resultado, tipo="text/html")
    if isinstance(resultado, (dict, list)):
        return Resposta.de_json(resultado)
    if isinstance(resultado, tuple) and len(resultado) == 2:
        r = normalizar(resultado[0])
        r.status = int(resultado[1])
        return r
    raise TypeError(f"tipo de retorno não suportado: {type(resultado).__name__}")

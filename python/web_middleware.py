"""Pipeline de middlewares estilo cebola sobre um manipulador final."""
from __future__ import annotations

from typing import Callable

from web_http import Requisicao, Resposta

Manipulador = Callable[[Requisicao], Resposta]
Middleware = Callable[[Requisicao, Manipulador], Resposta]


class Pipeline:
    """Compõe middlewares: o primeiro adicionado é o mais externo."""

    def __init__(self, final: Manipulador) -> None:
        self.final = final
        self.middlewares: list[Middleware] = []

    def usar(self, mw: Middleware) -> "Pipeline":
        self.middlewares.append(mw)
        return self

    def __call__(self, req: Requisicao) -> Resposta:
        def construir(i: int) -> Manipulador:
            if i == len(self.middlewares):
                return self.final
            mw = self.middlewares[i]
            proximo = construir(i + 1)
            return lambda r: mw(r, proximo)
        return construir(0)(req)


def mw_tempo(relogio: Callable[[], float]) -> Middleware:
    """Adiciona X-Tempo-Ms com a duração medida pelo relógio injetado."""
    def mw(req: Requisicao, proximo: Manipulador) -> Resposta:
        ini = relogio()
        resp = proximo(req)
        resp.cabecalhos["X-Tempo-Ms"] = f"{(relogio() - ini) * 1000:.1f}"
        return resp
    return mw


def mw_capturar_erros(req: Requisicao, proximo: Manipulador) -> Resposta:
    """Converte exceções em respostas 500 sem vazar detalhes."""
    try:
        return proximo(req)
    except Exception:
        return Resposta.de_texto("Erro interno", 500)


def mw_log(registro: list[str]) -> Middleware:
    def mw(req: Requisicao, proximo: Manipulador) -> Resposta:
        resp = proximo(req)
        registro.append(f"{req.metodo} {req.caminho} {resp.status}")
        return resp
    return mw


def mw_exigir_cabecalho(nome: str, status: int = 400) -> Middleware:
    """Curto-circuita (não chama o próximo) se o cabeçalho faltar."""
    def mw(req: Requisicao, proximo: Manipulador) -> Resposta:
        if nome not in req.cabecalhos:
            return Resposta.de_texto(f"Cabeçalho obrigatório: {nome}", status)
        return proximo(req)
    return mw

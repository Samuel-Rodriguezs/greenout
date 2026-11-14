"""Tratamento de erros: ErroHttp, páginas 404/500 (HTML ou JSON conforme Accept) e middleware."""
from __future__ import annotations

import html
import traceback
from typing import Callable

from web_http import Requisicao, Resposta
from web_middleware import Manipulador, Middleware
from web_negociacao import escolher
from web_roteador import MetodoNaoPermitido, RotaNaoEncontrada

TITULOS = {400: "Requisição inválida", 401: "Não autorizado", 403: "Proibido",
           404: "Página não encontrada", 405: "Método não permitido", 409: "Conflito",
           422: "Entidade não processável", 429: "Muitas requisições", 500: "Erro interno do servidor"}


class ErroHttp(Exception):
    def __init__(self, status: int, mensagem: str | None = None,
                 cabecalhos: dict[str, str] | None = None) -> None:
        if not 400 <= status <= 599:
            raise ValueError("ErroHttp exige status 4xx ou 5xx")
        super().__init__(mensagem or TITULOS.get(status, "Erro"))
        self.status = status
        self.mensagem = mensagem or TITULOS.get(status, "Erro")
        self.cabecalhos = cabecalhos or {}


PAGINA = ("<!doctype html><html lang=\"pt-BR\"><head><meta charset=\"utf-8\"><title>{status} - {titulo}"
          "</title></head><body><h1>{status}</h1><p>{mensagem}</p>{detalhe}</body></html>")


def resposta_erro(req: Requisicao, status: int, mensagem: str | None = None,
                  detalhe: str | None = None,
                  cabecalhos: dict[str, str] | None = None) -> Resposta:
    titulo = TITULOS.get(status, "Erro")
    mensagem = mensagem or titulo
    tipo = escolher(req.cabecalhos.get("Accept"), ["text/html", "application/json", "text/plain"])
    if tipo == "application/json":
        corpo: dict = {"erro": {"status": status, "titulo": titulo, "mensagem": mensagem}}
        if detalhe:
            corpo["erro"]["detalhe"] = detalhe
        resp = Resposta.de_json(corpo, status)
    elif tipo == "text/plain":
        resp = Resposta.de_texto(f"{status} {mensagem}", status)
    else:  # html (padrão, inclusive quando nada é aceitável)
        det = f"<pre>{html.escape(detalhe)}</pre>" if detalhe else ""
        resp = Resposta.de_texto(PAGINA.format(status=status, titulo=html.escape(titulo),
                                               mensagem=html.escape(mensagem), detalhe=det),
                                 status, "text/html")
    for k, v in (cabecalhos or {}).items():
        resp.cabecalhos[k] = v
    resp.cabecalhos["Vary"] = "Accept"
    return resp


def mw_erros(debug: bool = False, ao_falhar: Callable[[Exception], None] | None = None) -> Middleware:
    """Converte ErroHttp, 404/405 do roteador e exceções inesperadas em respostas de erro.

    Em produção (debug=False) o 500 nunca vaza traceback ou mensagem da exceção.
    Respostas de erro 4xx/5xx sem corpo vindas do manipulador também ganham página.
    """
    def mw(req: Requisicao, proximo: Manipulador) -> Resposta:
        try:
            resp = proximo(req)
        except ErroHttp as e:
            return resposta_erro(req, e.status, e.mensagem, cabecalhos=e.cabecalhos)
        except RotaNaoEncontrada:
            return resposta_erro(req, 404)
        except MetodoNaoPermitido as e:
            return resposta_erro(req, 405, cabecalhos={"Allow": ", ".join(e.permitidos)})
        except Exception as e:
            if ao_falhar:
                ao_falhar(e)
            detalhe = "".join(traceback.format_exception(e)) if debug else None
            return resposta_erro(req, 500, detalhe=detalhe)
        if resp.status >= 400 and not resp.corpo:
            return resposta_erro(req, resp.status, cabecalhos=dict(resp.cabecalhos.itens()))
        return resp
    return mw

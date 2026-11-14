"""Aplicação WSGI mínima: converte environ em Requisicao e Resposta em resposta WSGI."""
from __future__ import annotations

import io
from http import HTTPStatus
from typing import Any, Callable, Iterable
from urllib.parse import parse_qs

from web_http import Cabecalhos, Requisicao, Resposta
from web_roteador import Roteador

LIMITE_CORPO = 1_000_000


def requisicao_de_environ(environ: dict[str, Any], limite: int = LIMITE_CORPO) -> Requisicao:
    cab = Cabecalhos()
    for k, v in environ.items():
        if k.startswith("HTTP_"):
            cab[k[5:].replace("_", "-").title()] = v
    if environ.get("CONTENT_TYPE"):
        cab["Content-Type"] = environ["CONTENT_TYPE"]
    if environ.get("CONTENT_LENGTH"):
        cab["Content-Length"] = environ["CONTENT_LENGTH"]
    try:
        tamanho = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        raise ValueError("Content-Length inválido") from None
    if tamanho < 0:
        raise ValueError("Content-Length inválido")
    if tamanho > limite:
        raise OverflowError("corpo grande demais")
    entrada = environ.get("wsgi.input")
    corpo = entrada.read(tamanho) if entrada and tamanho else b""
    caminho = environ.get("PATH_INFO", "") or "/"
    return Requisicao(environ.get("REQUEST_METHOD", "GET"), caminho,
                      parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=True), cab, corpo)


class AppWsgi:
    """Envolve um manipulador (Requisicao -> Resposta) ou um Roteador como app WSGI."""

    def __init__(self, alvo: Roteador | Callable[[Requisicao], Resposta]) -> None:
        self.manipulador = alvo.despachar if isinstance(alvo, Roteador) else alvo

    def __call__(self, environ: dict[str, Any], start_response: Callable[..., Any]) -> Iterable[bytes]:
        try:
            req = requisicao_de_environ(environ)
            resp = self.manipulador(req)
        except OverflowError:
            resp = Resposta.de_texto("Corpo grande demais", 413)
        except ValueError as e:
            resp = Resposta.de_texto(f"Requisição inválida: {e}", 400)
        except Exception:
            resp = Resposta.de_texto("Erro interno", 500)
        metodo = environ.get("REQUEST_METHOD", "GET").upper()
        corpo = b"" if metodo == "HEAD" or resp.status in (204, 304) or resp.status < 200 else resp.corpo
        cabecalhos = [(k, v) for k, v in resp.cabecalhos.itens()]
        if not any(k.lower() == "content-length" for k, _ in cabecalhos):
            cabecalhos.append(("Content-Length", str(len(resp.corpo if metodo == "HEAD" else corpo))))
        start_response(f"{resp.status} {resp.frase or HTTPStatus(500).phrase}", cabecalhos)
        return [corpo]


def montar_environ(metodo: str, url: str, corpo: bytes = b"", cabecalhos: dict[str, str] | None = None) -> dict[str, Any]:
    """Cria um environ falso (para testes e chamadas em processo)."""
    caminho, _, query = url.partition("?")
    environ: dict[str, Any] = {
        "REQUEST_METHOD": metodo.upper(), "PATH_INFO": caminho or "/", "QUERY_STRING": query,
        "SERVER_NAME": "localhost", "SERVER_PORT": "80", "SERVER_PROTOCOL": "HTTP/1.1",
        "wsgi.version": (1, 0), "wsgi.url_scheme": "http", "wsgi.input": io.BytesIO(corpo),
        "wsgi.errors": io.StringIO(), "wsgi.multithread": False, "wsgi.multiprocess": False,
        "wsgi.run_once": False, "CONTENT_LENGTH": str(len(corpo)),
    }
    for k, v in (cabecalhos or {}).items():
        if k.lower() == "content-type":
            environ["CONTENT_TYPE"] = v
        else:
            environ["HTTP_" + k.upper().replace("-", "_")] = v
    return environ


def chamar(app: Callable[..., Iterable[bytes]], metodo: str, url: str, corpo: bytes = b"",
           cabecalhos: dict[str, str] | None = None) -> tuple[str, list[tuple[str, str]], bytes]:
    """Executa a app com environ falso e devolve (status, cabecalhos, corpo)."""
    captura: dict[str, Any] = {}

    def start_response(status: str, headers: list[tuple[str, str]], exc_info: Any = None) -> None:
        captura["status"], captura["headers"] = status, headers

    partes = app(montar_environ(metodo, url, corpo, cabecalhos), start_response)
    try:
        dados = b"".join(partes)
    finally:
        fechar = getattr(partes, "close", None)
        if fechar:
            fechar()
    return captura["status"], captura["headers"], dados

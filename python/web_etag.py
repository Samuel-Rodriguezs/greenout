"""Cache condicional: ETag e If-None-Match (resposta 304)."""
from __future__ import annotations

import hashlib

from web_http import Requisicao, Resposta
from web_middleware import Manipulador, Middleware


def calcular_etag(corpo: bytes, fraco: bool = False) -> str:
    h = hashlib.sha256(corpo).hexdigest()[:20]
    return f'{"W/" if fraco else ""}"{h}"'


def _opaco(tag: str) -> str:
    tag = tag.strip()
    return tag[2:] if tag.startswith("W/") else tag


def corresponde_if_none_match(cabecalho: str | None, etag: str) -> bool:
    """Comparação fraca (RFC 9110): ignora o prefixo W/. '*' casa com qualquer etag."""
    if not cabecalho:
        return False
    cabecalho = cabecalho.strip()
    if cabecalho == "*":
        return True
    alvo = _opaco(etag)
    return any(_opaco(t) == alvo for t in cabecalho.split(",") if t.strip())


def corresponde_if_match(cabecalho: str | None, etag: str) -> bool:
    """Comparação forte, usada em If-Match (etags fracos nunca casam)."""
    if not cabecalho:
        return True
    if cabecalho.strip() == "*":
        return True
    if etag.startswith("W/"):
        return False
    return any(t.strip() == etag for t in cabecalho.split(","))


def aplicar_etag(req: Requisicao, resp: Resposta, max_age: int | None = None) -> Resposta:
    """Anexa ETag a respostas 200 de GET/HEAD e converte em 304 se o cliente já tem a versão."""
    if req.metodo not in ("GET", "HEAD") or resp.status != 200:
        return resp
    etag = resp.cabecalhos.get("ETag") or calcular_etag(resp.corpo)
    resp.cabecalhos["ETag"] = etag
    if max_age is not None:
        resp.cabecalhos["Cache-Control"] = f"max-age={max_age}"
    if corresponde_if_none_match(req.cabecalhos.get("If-None-Match"), etag):
        nova = Resposta(304, b"")
        for k in ("ETag", "Cache-Control"):
            v = resp.cabecalhos.get(k)
            if v:
                nova.cabecalhos[k] = v
        return nova
    return resp


def mw_etag(max_age: int | None = None) -> Middleware:
    def mw(req: Requisicao, proximo: Manipulador) -> Resposta:
        return aplicar_etag(req, proximo(req), max_age)
    return mw


def verificar_precondicao(req: Requisicao, etag_atual: str) -> Resposta | None:
    """Para PUT/DELETE: devolve 412 se If-Match não confere com o recurso atual."""
    cab = req.cabecalhos.get("If-Match")
    if cab is not None and not corresponde_if_match(cab, etag_atual):
        return Resposta.de_texto("Pré-condição falhou", 412)
    return None

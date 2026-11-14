"""Geração de documento OpenAPI 3.0 a partir de rotas decoradas do Roteador."""
from __future__ import annotations

import re
from typing import Any, Callable

from web_roteador import Roteador

_TIPOS_PARAM: dict[str, dict[str, Any]] = {
    "int": {"type": "integer"},
    "float": {"type": "number"},
    "str": {"type": "string"},
    "slug": {"type": "string", "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$"},
    "path": {"type": "string"},
    "uuid": {"type": "string", "format": "uuid"},
}
_PARAM = re.compile(r"<(?:(\w+):)?(\w+)>")


def documentar(resumo: str = "", descricao: str = "", tags: tuple[str, ...] = (),
               query: dict[str, dict[str, Any]] | None = None,
               corpo: dict[str, Any] | None = None,
               respostas: dict[int, str | dict[str, Any]] | None = None,
               deprecated: bool = False) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Anexa metadados OpenAPI ao manipulador.

    query: {nome: {"schema": {...}, "obrigatorio": bool, "descricao": str}}
    corpo: JSON Schema do corpo da requisição.
    respostas: {status: "descrição" | {"descricao": str, "schema": {...}}}
    """
    def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
        fn.__openapi__ = {  # type: ignore[attr-defined]
            "resumo": resumo, "descricao": descricao, "tags": list(tags), "query": query or {},
            "corpo": corpo, "respostas": respostas or {}, "deprecated": deprecated}
        return fn
    return deco


def _caminho_openapi(padrao: str) -> str:
    return _PARAM.sub(lambda m: "{" + m.group(2) + "}", padrao)


def _resposta(valor: str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(valor, str):
        return {"description": valor}
    r: dict[str, Any] = {"description": valor.get("descricao", "")}
    if "schema" in valor:
        r["content"] = {"application/json": {"schema": valor["schema"]}}
    return r


def gerar_openapi(roteador: Roteador, titulo: str, versao: str, descricao: str = "",
                  servidores: tuple[str, ...] = ()) -> dict[str, Any]:
    if not titulo or not versao:
        raise ValueError("título e versão são obrigatórios")
    doc: dict[str, Any] = {"openapi": "3.0.3", "info": {"title": titulo, "version": versao}, "paths": {}}
    if descricao:
        doc["info"]["description"] = descricao
    if servidores:
        doc["servers"] = [{"url": s} for s in servidores]
    vistos: set[tuple[str, str]] = set()
    for rota in roteador.rotas:
        caminho = _caminho_openapi(rota.padrao)
        meta = getattr(rota.manipulador, "__openapi__", None) or {}
        parametros: list[dict[str, Any]] = [
            {"name": m.group(2), "in": "path", "required": True,
             "schema": dict(_TIPOS_PARAM.get(m.group(1) or "str", {"type": "string"}))}
            for m in _PARAM.finditer(rota.padrao)]
        for nome, cfg in meta.get("query", {}).items():
            p: dict[str, Any] = {"name": nome, "in": "query",
                                 "required": bool(cfg.get("obrigatorio", False)),
                                 "schema": cfg.get("schema", {"type": "string"})}
            if cfg.get("descricao"):
                p["description"] = cfg["descricao"]
            parametros.append(p)
        for metodo in sorted(rota.metodos):
            if (caminho, metodo) in vistos:
                raise ValueError(f"operação duplicada: {metodo} {caminho}")
            vistos.add((caminho, metodo))
            op: dict[str, Any] = {"operationId": f"{rota.nome}_{metodo.lower()}"}
            if meta.get("resumo"):
                op["summary"] = meta["resumo"]
            descr = meta.get("descricao") or (rota.manipulador.__doc__ or "").strip()
            if descr:
                op["description"] = descr
            if meta.get("tags"):
                op["tags"] = meta["tags"]
            if meta.get("deprecated"):
                op["deprecated"] = True
            if parametros:
                op["parameters"] = parametros
            if meta.get("corpo") and metodo in ("POST", "PUT", "PATCH"):
                op["requestBody"] = {"required": True,
                                     "content": {"application/json": {"schema": meta["corpo"]}}}
            respostas = meta.get("respostas") or {200: "Sucesso"}
            op["responses"] = {str(k): _resposta(v) for k, v in sorted(respostas.items())}
            doc["paths"].setdefault(caminho, {})[metodo.lower()] = op
    return doc

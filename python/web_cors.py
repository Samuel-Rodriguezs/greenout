"""CORS: middleware com tratamento de preflight (OPTIONS)."""
from __future__ import annotations

from dataclasses import dataclass, field

from web_http import Requisicao, Resposta
from web_middleware import Manipulador, Middleware


@dataclass
class ConfigCors:
    origens: tuple[str, ...] = ("*",)
    metodos: tuple[str, ...] = ("GET", "POST", "PUT", "PATCH", "DELETE")
    cabecalhos_permitidos: tuple[str, ...] = ("Content-Type", "Authorization")
    cabecalhos_expostos: tuple[str, ...] = ()
    credenciais: bool = False
    max_age: int = 600

    def __post_init__(self) -> None:
        if self.credenciais and "*" in self.origens:
            raise ValueError("credenciais não podem ser usadas com origem '*'")

    def origem_permitida(self, origem: str) -> str | None:
        """Valor para Access-Control-Allow-Origin, ou None se não permitida."""
        if "*" in self.origens:
            return "*"
        return origem if origem in self.origens else None


def mw_cors(cfg: ConfigCors) -> Middleware:
    def mw(req: Requisicao, proximo: Manipulador) -> Resposta:
        origem = req.cabecalhos.get("Origin")
        if not origem:
            return proximo(req)  # não é requisição CORS
        permitida = cfg.origem_permitida(origem)
        preflight = req.metodo == "OPTIONS" and "Access-Control-Request-Method" in req.cabecalhos

        if preflight:
            if permitida is None:
                return Resposta.de_texto("Origem não permitida", 403)
            metodo = req.cabecalhos["Access-Control-Request-Method"].upper()
            if metodo not in cfg.metodos:
                return Resposta.de_texto("Método não permitido", 405)
            pedidos = [h.strip() for h in
                       (req.cabecalhos.get("Access-Control-Request-Headers") or "").split(",") if h.strip()]
            ok = {h.lower() for h in cfg.cabecalhos_permitidos}
            if any(h.lower() not in ok for h in pedidos):
                return Resposta.de_texto("Cabeçalho não permitido", 403)
            resp = Resposta(204)
            resp.cabecalhos["Access-Control-Allow-Methods"] = ", ".join(cfg.metodos)
            if pedidos:
                resp.cabecalhos["Access-Control-Allow-Headers"] = ", ".join(pedidos)
            resp.cabecalhos["Access-Control-Max-Age"] = str(cfg.max_age)
            _comum(resp, cfg, permitida)
            return resp

        resp = proximo(req)
        if permitida is not None:
            _comum(resp, cfg, permitida)
            if cfg.cabecalhos_expostos:
                resp.cabecalhos["Access-Control-Expose-Headers"] = ", ".join(cfg.cabecalhos_expostos)
        elif "*" not in cfg.origens:
            resp.cabecalhos["Vary"] = "Origin"
        return resp
    return mw


def _comum(resp: Resposta, cfg: ConfigCors, permitida: str) -> None:
    resp.cabecalhos["Access-Control-Allow-Origin"] = permitida
    if permitida != "*":
        resp.cabecalhos["Vary"] = "Origin"
    if cfg.credenciais:
        resp.cabecalhos["Access-Control-Allow-Credentials"] = "true"

"""Objetos Requisicao e Resposta do micro-framework web (sem sockets)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Any
from urllib.parse import parse_qs, urlsplit


class Cabecalhos:
    """Mapa de cabeçalhos HTTP com chaves insensíveis a maiúsculas."""

    def __init__(self, dados: dict[str, str] | None = None) -> None:
        self._d: dict[str, tuple[str, str]] = {}
        for k, v in (dados or {}).items():
            self[k] = v

    def __setitem__(self, chave: str, valor: str) -> None:
        self._d[chave.lower()] = (chave, str(valor))

    def __getitem__(self, chave: str) -> str:
        return self._d[chave.lower()][1]

    def __contains__(self, chave: object) -> bool:
        return isinstance(chave, str) and chave.lower() in self._d

    def __delitem__(self, chave: str) -> None:
        del self._d[chave.lower()]

    def __len__(self) -> int:
        return len(self._d)

    def get(self, chave: str, padrao: str | None = None) -> str | None:
        item = self._d.get(chave.lower())
        return item[1] if item else padrao

    def itens(self) -> list[tuple[str, str]]:
        return list(self._d.values())


@dataclass
class Requisicao:
    metodo: str
    caminho: str
    query: dict[str, list[str]] = field(default_factory=dict)
    cabecalhos: Cabecalhos = field(default_factory=Cabecalhos)
    corpo: bytes = b""
    params: dict[str, Any] = field(default_factory=dict)
    contexto: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.metodo = self.metodo.upper()
        if isinstance(self.cabecalhos, dict):
            self.cabecalhos = Cabecalhos(self.cabecalhos)

    @classmethod
    def de_url(cls, metodo: str, url: str, cabecalhos: dict[str, str] | None = None,
               corpo: bytes = b"") -> "Requisicao":
        partes = urlsplit(url)
        return cls(metodo, partes.path or "/", parse_qs(partes.query, keep_blank_values=True),
                   Cabecalhos(cabecalhos), corpo)

    def arg(self, nome: str, padrao: str | None = None) -> str | None:
        valores = self.query.get(nome)
        return valores[0] if valores else padrao

    def json(self) -> Any:
        if not self.corpo:
            raise ValueError("corpo vazio")
        try:
            return json.loads(self.corpo.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            raise ValueError(f"JSON inválido: {e}") from e


@dataclass
class Resposta:
    status: int = 200
    corpo: bytes = b""
    cabecalhos: Cabecalhos = field(default_factory=Cabecalhos)

    def __post_init__(self) -> None:
        if isinstance(self.corpo, str):
            self.corpo = self.corpo.encode("utf-8")
        if isinstance(self.cabecalhos, dict):
            self.cabecalhos = Cabecalhos(self.cabecalhos)
        if not 100 <= self.status <= 599:
            raise ValueError(f"status inválido: {self.status}")

    @property
    def frase(self) -> str:
        try:
            return HTTPStatus(self.status).phrase
        except ValueError:
            return ""

    @property
    def texto(self) -> str:
        return self.corpo.decode("utf-8")

    @classmethod
    def de_texto(cls, texto: str, status: int = 200, tipo: str = "text/plain") -> "Resposta":
        return cls(status, texto.encode("utf-8"),
                   Cabecalhos({"Content-Type": f"{tipo}; charset=utf-8"}))

    @classmethod
    def de_json(cls, dados: Any, status: int = 200) -> "Resposta":
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
        return cls(status, corpo, Cabecalhos({"Content-Type": "application/json"}))

    @classmethod
    def redirecionar(cls, destino: str, status: int = 302) -> "Resposta":
        if status not in (301, 302, 303, 307, 308):
            raise ValueError("status de redirecionamento inválido")
        return cls(status, b"", Cabecalhos({"Location": destino}))

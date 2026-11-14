"""Parser do cabeçalho Cookie e construtor/parser de Set-Cookie."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import format_datetime, parsedate_to_datetime
from urllib.parse import quote, unquote

_PROIBIDOS = set('()<>@,;:\\"/[]?={} \t')


def parse_cookie(cabecalho: str) -> dict[str, str]:
    """'a=1; b=2' -> {'a': '1', 'b': '2'}. Ignora pares malformados; a primeira ocorrência vence."""
    resultado: dict[str, str] = {}
    for par in cabecalho.split(";"):
        if "=" not in par:
            continue
        nome, _, valor = par.strip().partition("=")
        valor = valor.strip()
        if len(valor) >= 2 and valor[0] == valor[-1] == '"':
            valor = valor[1:-1]
        if nome and nome not in resultado:
            resultado[nome] = unquote(valor)
    return resultado


@dataclass
class SetCookie:
    nome: str
    valor: str
    max_age: int | None = None
    expira: datetime | None = None
    caminho: str | None = "/"
    dominio: str | None = None
    seguro: bool = False
    http_only: bool = False
    same_site: str | None = None

    def __post_init__(self) -> None:
        if not self.nome or any(c in _PROIBIDOS or ord(c) < 33 for c in self.nome):
            raise ValueError(f"nome de cookie inválido: {self.nome!r}")
        if self.same_site is not None:
            norm = self.same_site.capitalize()
            if norm not in ("Strict", "Lax", "None"):
                raise ValueError("SameSite deve ser Strict, Lax ou None")
            self.same_site = norm
            if norm == "None" and not self.seguro:
                raise ValueError("SameSite=None exige Secure")

    def serializar(self) -> str:
        partes = [f"{self.nome}={quote(self.valor, safe='')}"]
        if self.max_age is not None:
            partes.append(f"Max-Age={int(self.max_age)}")
        if self.expira is not None:
            exp = self.expira if self.expira.tzinfo else self.expira.replace(tzinfo=timezone.utc)
            partes.append("Expires=" + format_datetime(exp.astimezone(timezone.utc), usegmt=True))
        if self.caminho:
            partes.append(f"Path={self.caminho}")
        if self.dominio:
            partes.append(f"Domain={self.dominio}")
        if self.seguro:
            partes.append("Secure")
        if self.http_only:
            partes.append("HttpOnly")
        if self.same_site:
            partes.append(f"SameSite={self.same_site}")
        return "; ".join(partes)

    @classmethod
    def remover(cls, nome: str, caminho: str = "/") -> "SetCookie":
        return cls(nome, "", max_age=0, caminho=caminho,
                   expira=datetime(1970, 1, 1, tzinfo=timezone.utc))


def parse_set_cookie(linha: str) -> SetCookie:
    """Interpreta uma linha Set-Cookie de volta para SetCookie."""
    itens = [p.strip() for p in linha.split(";")]
    nome, sep, valor = itens[0].partition("=")
    if not sep:
        raise ValueError("Set-Cookie sem '='")
    c = SetCookie(nome.strip(), unquote(valor), caminho=None)
    for attr in itens[1:]:
        chave, _, v = attr.partition("=")
        k = chave.strip().lower()
        if k == "max-age":
            c.max_age = int(v)
        elif k == "expires":
            c.expira = parsedate_to_datetime(v)
        elif k == "path":
            c.caminho = v
        elif k == "domain":
            c.dominio = v
        elif k == "secure":
            c.seguro = True
        elif k == "httponly":
            c.http_only = True
        elif k == "samesite":
            c.same_site = v.capitalize()
    return c

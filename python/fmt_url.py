"""Parser de URL: esquema, usuário, host, porta, caminho, query e fragmento."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

PORTAS_PADRAO = {"http": 80, "https": 443, "ftp": 21, "ssh": 22, "ws": 80, "wss": 443}


class ErroUrl(ValueError):
    """URL malformada."""


@dataclass
class Url:
    esquema: str
    usuario: str | None = None
    senha: str | None = None
    host: str = ""
    porta: int | None = None
    caminho: str = ""
    query: dict[str, list[str]] = field(default_factory=dict)
    fragmento: str = ""

    @property
    def porta_efetiva(self) -> int | None:
        return self.porta if self.porta is not None else PORTAS_PADRAO.get(self.esquema)


def _decodificar(s: str, mais: bool = False) -> str:
    if mais:
        s = s.replace("+", " ")
    bruto = bytearray()
    i = 0
    while i < len(s):
        if s[i] == "%":
            hexa = s[i + 1:i + 3]
            if len(hexa) != 2 or not re.fullmatch(r"[0-9A-Fa-f]{2}", hexa):
                raise ErroUrl(f"escape percentual inválido em {s[i:i + 3]!r}")
            bruto.append(int(hexa, 16))
            i += 3
        else:
            bruto.extend(s[i].encode("utf-8"))
            i += 1
    return bruto.decode("utf-8", errors="strict")


def _parse_query(q: str) -> dict[str, list[str]]:
    res: dict[str, list[str]] = {}
    for par in q.split("&"):
        if not par:
            continue
        k, _, v = par.partition("=")
        res.setdefault(_decodificar(k, True), []).append(_decodificar(v, True))
    return res


def parse(texto: str) -> Url:
    """Faz o parse de uma URL absoluta com autoridade (esquema://host...)."""
    m = re.fullmatch(r"([A-Za-z][A-Za-z0-9+.\-]*)://([^/?#]*)([^?#]*)(?:\?([^#]*))?(?:#(.*))?", texto.strip())
    if not m:
        raise ErroUrl(f"URL inválida: {texto!r}")
    esquema, autoridade, caminho, query, frag = m.groups()
    usuario = senha = None
    if "@" in autoridade:
        info, autoridade = autoridade.rsplit("@", 1)
        u, sep, s = info.partition(":")
        usuario, senha = _decodificar(u), (_decodificar(s) if sep else None)
    porta = None
    if autoridade.startswith("["):
        fim = autoridade.find("]")
        if fim == -1:
            raise ErroUrl("IPv6 sem ']'")
        host, resto = autoridade[:fim + 1], autoridade[fim + 1:]
        if resto:
            if not resto.startswith(":"):
                raise ErroUrl("lixo após o host IPv6")
            autoridade_porta = resto[1:]
        else:
            autoridade_porta = ""
    else:
        host, sep, autoridade_porta = autoridade.partition(":")
        if not sep:
            autoridade_porta = ""
    if autoridade_porta:
        if not autoridade_porta.isdigit() or not 0 <= int(autoridade_porta) <= 65535:
            raise ErroUrl(f"porta inválida: {autoridade_porta!r}")
        porta = int(autoridade_porta)
    if not host and esquema.lower() != "file":
        raise ErroUrl("host ausente")
    return Url(esquema.lower(), usuario, senha, host.lower(), porta, caminho or "/" if host else caminho,
               _parse_query(query or ""), _decodificar(frag or ""))

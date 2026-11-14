"""Parser de requisição HTTP/1.x bruta (linha de requisição, cabeçalhos e corpo)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

METODOS = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "TRACE", "CONNECT"}


class ErroHttp(ValueError):
    """Requisição HTTP malformada."""


@dataclass
class Requisicao:
    metodo: str
    alvo: str
    versao: str
    cabecalhos: dict[str, str] = field(default_factory=dict)
    corpo: bytes = b""

    def cabecalho(self, nome: str) -> str | None:
        return self.cabecalhos.get(nome.lower())


def parse(dados: bytes | str) -> Requisicao:
    """Interpreta a requisição; respeita Content-Length e Transfer-Encoding: chunked."""
    if isinstance(dados, str):
        dados = dados.encode("utf-8")
    sep = dados.find(b"\r\n\r\n")
    if sep == -1:
        sep_len, sep = 2, dados.find(b"\n\n")
        if sep == -1:
            raise ErroHttp("fim dos cabeçalhos não encontrado")
        sep_len = 2
    else:
        sep_len = 4
    cabeca = dados[:sep].decode("latin-1")
    corpo = dados[sep + sep_len:]
    linhas = re.split(r"\r?\n", cabeca)
    m = re.fullmatch(r"([A-Z]+) (\S+) HTTP/(1\.[01]|2|3)", linhas[0])
    if not m:
        raise ErroHttp(f"linha de requisição inválida: {linhas[0]!r}")
    metodo, alvo, versao = m.groups()
    if metodo not in METODOS:
        raise ErroHttp(f"método desconhecido: {metodo}")
    cab: dict[str, str] = {}
    ultimo: str | None = None
    for l in linhas[1:]:
        if l[:1] in (" ", "\t"):
            if ultimo is None:
                raise ErroHttp("continuação sem cabeçalho anterior")
            cab[ultimo] += " " + l.strip()
            continue
        nome, dp, valor = l.partition(":")
        if not dp or not nome or nome != nome.strip() or " " in nome:
            raise ErroHttp(f"cabeçalho inválido: {l!r}")
        ultimo = nome.lower()
        cab[ultimo] = (cab[ultimo] + ", " if ultimo in cab else "") + valor.strip()
    if versao == "1.1" and "host" not in cab:
        raise ErroHttp("HTTP/1.1 exige cabeçalho Host")
    if "chunked" in cab.get("transfer-encoding", "").lower():
        corpo = _desfragmentar(corpo)
    elif "content-length" in cab:
        cl = cab["content-length"]
        if not cl.isdigit():
            raise ErroHttp(f"Content-Length inválido: {cl!r}")
        if len(corpo) < int(cl):
            raise ErroHttp("corpo menor que Content-Length")
        corpo = corpo[:int(cl)]
    return Requisicao(metodo, alvo, versao, cab, corpo)


def _desfragmentar(b: bytes) -> bytes:
    saida = bytearray()
    pos = 0
    while True:
        fim = b.find(b"\r\n", pos)
        if fim == -1:
            raise ErroHttp("chunk sem tamanho")
        try:
            tam = int(b[pos:fim].split(b";")[0], 16)
        except ValueError:
            raise ErroHttp("tamanho de chunk inválido") from None
        pos = fim + 2
        if tam == 0:
            return bytes(saida)
        if len(b) < pos + tam + 2:
            raise ErroHttp("chunk truncado")
        saida += b[pos:pos + tam]
        pos += tam + 2

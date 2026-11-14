"""Parser de log combinado Apache/Nginx e estatísticas."""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


class ErroLog(ValueError):
    """Linha de log malformada."""


@dataclass(frozen=True)
class Registro:
    ip: str
    usuario: str | None
    momento: datetime
    metodo: str
    caminho: str
    protocolo: str
    status: int
    bytes_: int
    referer: str | None
    user_agent: str | None


_PADRAO = re.compile(
    r'^(\S+) \S+ (\S+) \[([^\]]+)\] "((?:[^"\\]|\\.)*)" (\d{3}) (\d+|-)'
    r'(?: "((?:[^"\\]|\\.)*)" "((?:[^"\\]|\\.)*)")?\s*$'
)


def parse_linha(linha: str) -> Registro:
    m = _PADRAO.match(linha.strip())
    if not m:
        raise ErroLog(f"formato inválido: {linha!r}")
    ip, usuario, data, requisicao, status, tam, ref, ua = m.groups()
    try:
        momento = datetime.strptime(data, "%d/%b/%Y:%H:%M:%S %z")
    except ValueError as e:
        raise ErroLog(f"data inválida: {data!r}") from e
    partes = requisicao.split(" ")
    if len(partes) == 3:
        metodo, caminho, proto = partes
    elif requisicao == "-" or not requisicao:
        metodo, caminho, proto = "-", "-", "-"
    else:
        raise ErroLog(f"requisição inválida: {requisicao!r}")
    campo = lambda v: None if v in (None, "-") else v.replace('\\"', '"')
    return Registro(ip, campo(usuario), momento, metodo, caminho, proto, int(status),
                    0 if tam == "-" else int(tam), campo(ref), campo(ua))


def parse_log(linhas: Iterable[str], ignorar_invalidas: bool = False) -> list[Registro]:
    res: list[Registro] = []
    for linha in linhas:
        if not linha.strip():
            continue
        try:
            res.append(parse_linha(linha))
        except ErroLog:
            if not ignorar_invalidas:
                raise
    return res


def estatisticas(registros: list[Registro], top: int = 3) -> dict[str, object]:
    """Resumo: total, bytes, status por classe, mais acessados, IPs e taxa de erro."""
    if not registros:
        return {"total": 0, "bytes": 0, "por_classe": {}, "top_caminhos": [], "top_ips": [],
                "taxa_erro": 0.0, "ips_unicos": 0}
    classes = Counter(f"{r.status // 100}xx" for r in registros)
    erros = sum(1 for r in registros if r.status >= 400)
    return {
        "total": len(registros),
        "bytes": sum(r.bytes_ for r in registros),
        "por_classe": dict(sorted(classes.items())),
        "top_caminhos": Counter(r.caminho for r in registros).most_common(top),
        "top_ips": Counter(r.ip for r in registros).most_common(top),
        "taxa_erro": erros / len(registros),
        "ips_unicos": len({r.ip for r in registros}),
    }

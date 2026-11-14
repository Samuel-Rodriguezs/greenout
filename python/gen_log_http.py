"""Logs de acesso HTTP fictícios no formato combinado (Apache/Nginx combined)."""
from __future__ import annotations

import random
import re
from datetime import datetime, timedelta, timezone

CAMINHOS: tuple[str, ...] = (
    "/", "/login", "/produtos", "/produtos/42", "/carrinho", "/api/v1/pedidos",
    "/static/app.js", "/static/estilo.css", "/contato", "/favicon.ico",
)
METODOS: tuple[tuple[str, int], ...] = (("GET", 80), ("POST", 15), ("PUT", 3), ("DELETE", 2))
STATUS: tuple[tuple[int, int], ...] = ((200, 78), (304, 8), (301, 3), (404, 7), (500, 3), (403, 1))
AGENTES: tuple[str, ...] = (
    "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "curl/8.5.0",
)
REFERERS: tuple[str, ...] = ("-", "https://exemplo.com.br/", "https://busca.example/?q=loja")

LINHA_RE = re.compile(
    r'^(\S+) (\S+) (\S+) \[([^\]]+)\] "(\S+) (\S+) (\S+)" (\d{3}) (\d+|-) "([^"]*)" "([^"]*)"$'
)


def _ip(rng: random.Random) -> str:
    # faixa 203.0.113.0/24 e 198.51.100.0/24 são reservadas para documentação (RFC 5737)
    return f"{rng.choice(('203.0.113', '198.51.100'))}.{rng.randint(1, 254)}"


def formatar_data(t: datetime) -> str:
    """Ex.: 10/Mar/2025:13:55:36 -0300 (meses em inglês, independente de locale)."""
    meses = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
    off = t.utcoffset() or timedelta(0)
    minutos = int(off.total_seconds() // 60)
    sinal = "-" if minutos < 0 else "+"
    h, m = divmod(abs(minutos), 60)
    return f"{t.day:02d}/{meses[t.month - 1]}/{t.year}:{t:%H:%M:%S} {sinal}{h:02d}{m:02d}"


def gerar_linhas(seed: int, n: int, inicio: datetime | None = None) -> list[str]:
    rng = random.Random(seed)
    t = inicio or datetime(2025, 3, 10, 13, 0, 0, tzinfo=timezone(timedelta(hours=-3)))
    if t.tzinfo is None:
        raise ValueError("início deve ter fuso horário")
    metodos, pesos_m = zip(*METODOS)
    codigos, pesos_s = zip(*STATUS)
    linhas: list[str] = []
    for _ in range(n):
        t += timedelta(seconds=rng.randint(0, 5))
        metodo = rng.choices(metodos, pesos_m)[0]
        status = rng.choices(codigos, pesos_s)[0]
        tamanho = "-" if status == 304 else str(rng.randint(120, 90_000))
        usuario = rng.choice(("-", "-", "-", "ana", "bruno"))
        linhas.append(
            f'{_ip(rng)} - {usuario} [{formatar_data(t)}] '
            f'"{metodo} {rng.choice(CAMINHOS)} HTTP/1.1" {status} {tamanho} '
            f'"{rng.choice(REFERERS)}" "{rng.choice(AGENTES)}"'
        )
    return linhas


def interpretar_linha(linha: str) -> dict[str, str | int]:
    m = LINHA_RE.match(linha)
    if not m:
        raise ValueError(f"linha fora do formato combinado: {linha!r}")
    ip, _, usuario, data, metodo, caminho, versao, status, tamanho, referer, agente = m.groups()
    return {
        "ip": ip, "usuario": usuario, "data": data, "metodo": metodo, "caminho": caminho,
        "versao": versao, "status": int(status),
        "tamanho": 0 if tamanho == "-" else int(tamanho),
        "referer": referer, "agente": agente,
    }

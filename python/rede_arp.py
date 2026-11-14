"""ARP simulado (RFC 826): pacote, cache com TTL e resolução em um segmento LAN."""
from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Callable

OP_REQUISICAO, OP_RESPOSTA = 1, 2
MAC_ZERO = 0
MAC_BROADCAST = 0xFFFFFFFFFFFF


@dataclass(frozen=True)
class PacoteARP:
    operacao: int
    mac_origem: int
    ip_origem: int
    mac_destino: int
    ip_destino: int


def serializar(p: PacoteARP) -> bytes:
    """Ethernet (1) / IPv4 (0x0800), 28 bytes."""
    return (struct.pack("!HHBBH", 1, 0x0800, 6, 4, p.operacao)
            + p.mac_origem.to_bytes(6, "big") + struct.pack("!I", p.ip_origem)
            + p.mac_destino.to_bytes(6, "big") + struct.pack("!I", p.ip_destino))


def parse(dados: bytes) -> PacoteARP:
    if len(dados) != 28:
        raise ValueError("pacote ARP deve ter 28 bytes")
    htipo, ptipo, hlen, plen, op = struct.unpack("!HHBBH", dados[:8])
    if (htipo, ptipo, hlen, plen) != (1, 0x0800, 6, 4):
        raise ValueError("ARP suportado apenas para Ethernet/IPv4")
    if op not in (OP_REQUISICAO, OP_RESPOSTA):
        raise ValueError("operação ARP desconhecida")
    return PacoteARP(op, int.from_bytes(dados[8:14], "big"), struct.unpack("!I", dados[14:18])[0],
                     int.from_bytes(dados[18:24], "big"), struct.unpack("!I", dados[24:28])[0])


class CacheARP:
    """Mapeamento IP -> MAC com expiração; o relógio é injetável para testes."""

    def __init__(self, ttl: float = 300.0, relogio: Callable[[], float] | None = None) -> None:
        if ttl <= 0:
            raise ValueError("ttl deve ser positivo")
        self.ttl = ttl
        self._relogio = relogio or (lambda: 0.0)
        self._entradas: dict[int, tuple[int, float]] = {}

    def inserir(self, ip: int, mac: int) -> None:
        self._entradas[ip] = (mac, self._relogio() + self.ttl)

    def consultar(self, ip: int) -> int | None:
        item = self._entradas.get(ip)
        if item is None:
            return None
        mac, expira = item
        if self._relogio() >= expira:
            del self._entradas[ip]
            return None
        return mac

    def remover(self, ip: int) -> bool:
        return self._entradas.pop(ip, None) is not None

    def limpar_expirados(self) -> int:
        agora = self._relogio()
        vencidos = [ip for ip, (_, exp) in self._entradas.items() if agora >= exp]
        for ip in vencidos:
            del self._entradas[ip]
        return len(vencidos)

    def __len__(self) -> int:
        return len(self._entradas)


class SegmentoLAN:
    """Domínio de broadcast: entrega o pacote a todos, menos ao remetente."""

    def __init__(self) -> None:
        self.hosts: list[HostARP] = []
        self.pacotes_enviados = 0

    def anexar(self, host: "HostARP") -> None:
        self.hosts.append(host)
        host.segmento = self

    def transmitir(self, origem: "HostARP", dados: bytes) -> None:
        self.pacotes_enviados += 1
        for h in self.hosts:
            if h is not origem:
                h.receber(dados)


class HostARP:
    def __init__(self, ip: int, mac: int, cache: CacheARP | None = None) -> None:
        self.ip, self.mac = ip, mac
        self.cache = cache if cache is not None else CacheARP()
        self.segmento: SegmentoLAN | None = None

    def resolver(self, ip_alvo: int) -> int | None:
        """MAC do alvo; usa o cache e, se faltar, envia ARP request em broadcast."""
        if ip_alvo == self.ip:
            return self.mac
        mac = self.cache.consultar(ip_alvo)
        if mac is not None or self.segmento is None:
            return mac
        req = PacoteARP(OP_REQUISICAO, self.mac, self.ip, MAC_ZERO, ip_alvo)
        self.segmento.transmitir(self, serializar(req))
        return self.cache.consultar(ip_alvo)

    def receber(self, dados: bytes) -> None:
        p = parse(dados)
        if p.ip_origem != 0:
            if p.ip_destino == self.ip or self.cache.consultar(p.ip_origem) is not None:
                self.cache.inserir(p.ip_origem, p.mac_origem)  # aprende com o remetente
        if p.operacao == OP_REQUISICAO and p.ip_destino == self.ip and self.segmento:
            resp = PacoteARP(OP_RESPOSTA, self.mac, self.ip, p.mac_origem, p.ip_origem)
            self.segmento.transmitir(self, serializar(resp))

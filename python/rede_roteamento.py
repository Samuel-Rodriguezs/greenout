"""Tabela de roteamento IPv4 com longest prefix match (trie binária)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from rede_cidr import formatar_cidr, parse_cidr
from rede_ipv4 import mascara_de_prefixo


@dataclass(frozen=True)
class Rota:
    rede: int
    prefixo: int
    proximo_salto: str | None  # None = diretamente conectada
    interface: str
    metrica: int = 0

    def __str__(self) -> str:
        via = f"via {self.proximo_salto}" if self.proximo_salto else "direta"
        return f"{formatar_cidr(self.rede, self.prefixo)} {via} dev {self.interface} metric {self.metrica}"


class _No:
    __slots__ = ("filhos", "rota")

    def __init__(self) -> None:
        self.filhos: list[_No | None] = [None, None]
        self.rota: Rota | None = None


class TabelaRoteamento:
    def __init__(self) -> None:
        self._raiz = _No()
        self._qtd = 0

    def adicionar(self, cidr: str, proximo_salto: str | None, interface: str,
                  metrica: int = 0) -> Rota:
        """Insere/substitui a rota; em empate de prefixo mantém a de menor métrica."""
        ip, p = parse_cidr(cidr)
        rede = ip & mascara_de_prefixo(p)
        no = self._raiz
        for i in range(p):
            bit = (rede >> (31 - i)) & 1
            if no.filhos[bit] is None:
                no.filhos[bit] = _No()
            no = no.filhos[bit]  # type: ignore[assignment]
        nova = Rota(rede, p, proximo_salto, interface, metrica)
        if no.rota is None:
            self._qtd += 1
            no.rota = nova
        elif metrica <= no.rota.metrica:
            no.rota = nova
        return no.rota

    def remover(self, cidr: str) -> bool:
        ip, p = parse_cidr(cidr)
        rede = ip & mascara_de_prefixo(p)
        no: _No | None = self._raiz
        for i in range(p):
            no = no.filhos[(rede >> (31 - i)) & 1] if no else None
        if no is None or no.rota is None:
            return False
        no.rota = None
        self._qtd -= 1
        return True

    def buscar(self, ip: int) -> Rota | None:
        """Rota de prefixo mais longo que casa com o endereço."""
        no: _No | None = self._raiz
        melhor = no.rota if no else None
        for i in range(32):
            no = no.filhos[(ip >> (31 - i)) & 1] if no else None
            if no is None:
                break
            if no.rota is not None:
                melhor = no.rota
        return melhor

    def rotas(self) -> Iterator[Rota]:
        """Todas as rotas em ordem de rede e prefixo."""
        pilha = [self._raiz]
        achadas: list[Rota] = []
        while pilha:
            no = pilha.pop()
            if no.rota is not None:
                achadas.append(no.rota)
            pilha.extend(f for f in no.filhos if f is not None)
        yield from sorted(achadas, key=lambda r: (r.rede, r.prefixo))

    def __len__(self) -> int:
        return self._qtd

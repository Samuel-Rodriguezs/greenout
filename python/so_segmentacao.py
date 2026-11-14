"""Segmentação: tabela (base, limite, permissões), tradução, proteção e compactação."""
from __future__ import annotations

from dataclasses import dataclass


class FaltaDeSegmentacao(Exception):
    """Segmento inexistente, deslocamento além do limite ou permissão negada."""


class SemMemoria(Exception):
    pass


@dataclass
class Segmento:
    base: int
    limite: int
    perm: str = "rw"  # subconjunto de "rwx"

    @property
    def fim(self) -> int:
        return self.base + self.limite


class Segmentacao:
    def __init__(self, memoria: int) -> None:
        if memoria <= 0:
            raise ValueError("memória deve ser positiva")
        self.memoria = memoria
        self.tabela: dict[int, Segmento] = {}

    def registrar(self, seg: int, base: int, limite: int, perm: str = "rw") -> None:
        """Instala um segmento em posição explícita, recusando sobreposição."""
        if seg in self.tabela:
            raise ValueError(f"segmento {seg} já existe")
        if limite <= 0 or base < 0 or base + limite > self.memoria:
            raise ValueError("segmento fora da memória")
        if set(perm) - set("rwx"):
            raise ValueError("permissão inválida")
        for outro in self.tabela.values():
            if base < outro.fim and outro.base < base + limite:
                raise ValueError("sobreposição de segmentos")
        self.tabela[seg] = Segmento(base, limite, perm)

    def lacunas(self) -> list[tuple[int, int]]:
        """Lacunas livres como (início, tamanho), em ordem de endereço."""
        saida = []
        cursor = 0
        for s in sorted(self.tabela.values(), key=lambda s: s.base):
            if s.base > cursor:
                saida.append((cursor, s.base - cursor))
            cursor = s.fim
        if cursor < self.memoria:
            saida.append((cursor, self.memoria - cursor))
        return saida

    def alocar(self, seg: int, limite: int, perm: str = "rw") -> int:
        """First fit; devolve a base escolhida."""
        for inicio, tamanho in self.lacunas():
            if tamanho >= limite:
                self.registrar(seg, inicio, limite, perm)
                return inicio
        raise SemMemoria(f"sem lacuna contígua de {limite}")

    def liberar(self, seg: int) -> None:
        del self.tabela[seg]

    def livre_total(self) -> int:
        return sum(t for _, t in self.lacunas())

    def maior_lacuna(self) -> int:
        return max((t for _, t in self.lacunas()), default=0)

    def compactar(self) -> int:
        """Desliza os segmentos para o início; devolve quantos foram movidos."""
        movidos = 0
        cursor = 0
        for s in sorted(self.tabela.values(), key=lambda s: s.base):
            if s.base != cursor:
                s.base = cursor
                movidos += 1
            cursor = s.fim
        return movidos

    def traduzir(self, seg: int, deslocamento: int, acesso: str = "r") -> int:
        s = self.tabela.get(seg)
        if s is None:
            raise FaltaDeSegmentacao(f"segmento {seg} inexistente")
        if not 0 <= deslocamento < s.limite:
            raise FaltaDeSegmentacao(f"deslocamento {deslocamento} além do limite {s.limite}")
        if acesso not in s.perm:
            raise FaltaDeSegmentacao(f"acesso '{acesso}' negado no segmento {seg}")
        return s.base + deslocamento

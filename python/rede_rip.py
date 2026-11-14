"""Vetor de distância no estilo RIP: Bellman-Ford distribuído, infinito = 16."""
from __future__ import annotations

INFINITO = 16


class Roteador:
    def __init__(self, nome: str, split_horizon: bool = True) -> None:
        self.nome = nome
        self.split_horizon = split_horizon
        self.vizinhos: dict[str, int] = {}
        # destino -> (custo, próximo salto)
        self.tabela: dict[str, tuple[int, str | None]] = {nome: (0, None)}

    def custo(self, destino: str) -> int:
        return self.tabela.get(destino, (INFINITO, None))[0]

    def anunciar(self, para: str) -> dict[str, int]:
        """Vetor enviado ao vizinho `para`, com poison reverse se habilitado."""
        vetor = {}
        for dest, (c, via) in self.tabela.items():
            if self.split_horizon and via == para:
                vetor[dest] = INFINITO  # poison reverse
            else:
                vetor[dest] = c
        return vetor

    def receber(self, de: str, vetor: dict[str, int]) -> bool:
        """Processa um anúncio; devolve True se a tabela mudou."""
        if de not in self.vizinhos:
            raise ValueError(f"{de!r} não é vizinho de {self.nome!r}")
        mudou = False
        enlace = self.vizinhos[de]
        for dest, c in vetor.items():
            if dest == self.nome:
                continue
            novo = min(c + enlace, INFINITO)
            atual, via = self.tabela.get(dest, (INFINITO, None))
            if via == de:
                # notícias do próximo salto atual valem sempre (inclusive piores)
                if novo != atual:
                    if novo >= INFINITO:
                        self.tabela[dest] = (INFINITO, de)
                    else:
                        self.tabela[dest] = (novo, de)
                    mudou = True
            elif novo < atual:
                self.tabela[dest] = (novo, de)
                mudou = True
        return mudou

    def enlace_caiu(self, vizinho: str) -> None:
        self.vizinhos.pop(vizinho, None)
        for dest, (_, via) in list(self.tabela.items()):
            if via == vizinho:
                self.tabela[dest] = (INFINITO, vizinho)


class RedeRIP:
    def __init__(self, split_horizon: bool = True) -> None:
        self.roteadores: dict[str, Roteador] = {}
        self.split_horizon = split_horizon

    def adicionar_enlace(self, a: str, b: str, custo: int = 1) -> None:
        for n in (a, b):
            self.roteadores.setdefault(n, Roteador(n, self.split_horizon))
        self.roteadores[a].vizinhos[b] = custo
        self.roteadores[b].vizinhos[a] = custo

    def derrubar_enlace(self, a: str, b: str) -> None:
        self.roteadores[a].enlace_caiu(b)
        self.roteadores[b].enlace_caiu(a)

    def rodada(self) -> bool:
        """Todos anunciam ao mesmo tempo (síncrono). True se algo mudou."""
        anuncios = [(r, v, r.anunciar(v)) for r in self.roteadores.values() for v in list(r.vizinhos)]
        mudou = False
        for origem, destino, vetor in anuncios:
            if origem.nome in self.roteadores[destino].vizinhos:
                mudou |= self.roteadores[destino].receber(origem.nome, vetor)
        return mudou

    def convergir(self, max_rodadas: int = 100) -> int:
        """Roda até estabilizar; devolve o número de rodadas com mudança."""
        for n in range(max_rodadas):
            if not self.rodada():
                return n
        raise RuntimeError("não convergiu (contagem ao infinito?)")

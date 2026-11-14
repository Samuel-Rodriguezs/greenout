"""Jantar dos filósofos sem deadlock (hierarquia de recursos: garfo menor primeiro)."""
from __future__ import annotations

import threading


class Mesa:
    def __init__(self, n: int = 5) -> None:
        if n < 2:
            raise ValueError("são necessários ao menos 2 filósofos")
        self.n = n
        self.garfos = [threading.Lock() for _ in range(n)]
        self.refeicoes = [0] * n
        self._log_lock = threading.Lock()
        self.comendo: set[int] = set()
        self.violacoes = 0

    def garfos_de(self, i: int) -> tuple[int, int]:
        """Retorna (menor, maior) índice dos garfos do filósofo i."""
        a, b = i, (i + 1) % self.n
        return (a, b) if a < b else (b, a)

    def comer(self, i: int) -> None:
        primeiro, segundo = self.garfos_de(i)
        with self.garfos[primeiro]:
            with self.garfos[segundo]:
                with self._log_lock:
                    vizinhos = {(i - 1) % self.n, (i + 1) % self.n}
                    if self.comendo & vizinhos:
                        self.violacoes += 1
                    self.comendo.add(i)
                    self.refeicoes[i] += 1
                with self._log_lock:
                    self.comendo.discard(i)

    def jantar(self, rodadas: int, timeout: float = 5.0) -> bool:
        """Executa o jantar; retorna True se todos terminaram (sem deadlock)."""

        def filosofo(i: int) -> None:
            for _ in range(rodadas):
                self.comer(i)

        ts = [threading.Thread(target=filosofo, args=(i,), daemon=True) for i in range(self.n)]
        for t in ts:
            t.start()
        for t in ts:
            t.join(timeout)
        return not any(t.is_alive() for t in ts)

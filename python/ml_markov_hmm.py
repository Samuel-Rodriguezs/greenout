"""Cadeia de Markov e HMM simples: probabilidade de sequência (forward) e Viterbi."""
from __future__ import annotations


class CadeiaMarkov:
    def __init__(self, estados: list[str], transicao: dict[str, dict[str, float]],
                 inicial: dict[str, float] | None = None) -> None:
        for e in estados:
            if abs(sum(transicao[e].get(f, 0.0) for f in estados) - 1.0) > 1e-9:
                raise ValueError(f"linha de transição de {e!r} não soma 1")
        self.estados = estados
        self.transicao = transicao
        self.inicial = inicial or {e: 1 / len(estados) for e in estados}

    def prob_sequencia(self, seq: list[str]) -> float:
        p = self.inicial.get(seq[0], 0.0)
        for a, b in zip(seq, seq[1:]):
            p *= self.transicao[a].get(b, 0.0)
        return p

    def distribuicao_estacionaria(self, iteracoes: int = 1000) -> dict[str, float]:
        d = dict(self.inicial)
        for _ in range(iteracoes):
            d = {f: sum(d[e] * self.transicao[e].get(f, 0.0) for e in self.estados) for f in self.estados}
        return d

    @staticmethod
    def estimar(sequencias: list[list[str]], estados: list[str]) -> "CadeiaMarkov":
        """Estimativa por máxima verossimilhança (com suavização de Laplace)."""
        cont = {e: {f: 1.0 for f in estados} for e in estados}
        for seq in sequencias:
            for a, b in zip(seq, seq[1:]):
                cont[a][b] += 1
        trans = {e: {f: c / sum(cont[e].values()) for f, c in cont[e].items()} for e in estados}
        return CadeiaMarkov(estados, trans)


class HMM:
    def __init__(self, estados: list[str], inicial: dict[str, float],
                 transicao: dict[str, dict[str, float]], emissao: dict[str, dict[str, float]]) -> None:
        self.estados, self.inicial, self.transicao, self.emissao = estados, inicial, transicao, emissao

    def forward(self, obs: list[str]) -> float:
        """P(observações) somando sobre todos os caminhos."""
        if not obs:
            raise ValueError("observações vazias")
        alfa = {s: self.inicial[s] * self.emissao[s].get(obs[0], 0.0) for s in self.estados}
        for o in obs[1:]:
            alfa = {s: sum(alfa[r] * self.transicao[r].get(s, 0.0) for r in self.estados)
                    * self.emissao[s].get(o, 0.0) for s in self.estados}
        return sum(alfa.values())

    def viterbi(self, obs: list[str]) -> tuple[list[str], float]:
        """Caminho de estados mais provável e sua probabilidade conjunta."""
        if not obs:
            raise ValueError("observações vazias")
        v = [{s: self.inicial[s] * self.emissao[s].get(obs[0], 0.0) for s in self.estados}]
        voltar: list[dict[str, str]] = []
        for o in obs[1:]:
            atual, ptr = {}, {}
            for s in self.estados:
                melhor = max(self.estados, key=lambda r: v[-1][r] * self.transicao[r].get(s, 0.0))
                atual[s] = v[-1][melhor] * self.transicao[melhor].get(s, 0.0) * self.emissao[s].get(o, 0.0)
                ptr[s] = melhor
            v.append(atual)
            voltar.append(ptr)
        ultimo = max(self.estados, key=lambda s: v[-1][s])
        caminho = [ultimo]
        for ptr in reversed(voltar):
            caminho.append(ptr[caminho[-1]])
        caminho.reverse()
        return caminho, v[-1][ultimo]

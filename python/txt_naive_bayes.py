"""Classificador Naive Bayes multinomial (spam/ham) com dataset pequeno embutido."""
import math
import re
from collections import Counter, defaultdict

DATASET: list[tuple[str, str]] = [
    ("ganhe dinheiro rápido clique agora", "spam"),
    ("promoção imperdível compre agora grátis", "spam"),
    ("você ganhou um prêmio clique no link", "spam"),
    ("oferta exclusiva desconto grátis ganhe", "spam"),
    ("dinheiro fácil sem esforço ganhe agora", "spam"),
    ("reunião amanhã às dez na sala", "ham"),
    ("segue o relatório do projeto em anexo", "ham"),
    ("vamos almoçar juntos hoje", "ham"),
    ("obrigado pela ajuda com o trabalho", "ham"),
    ("lembrete da consulta marcada para sexta", "ham"),
]


def _tokens(texto: str) -> list[str]:
    return re.findall(r"[^\W\d_]+", texto.lower())


class NaiveBayes:
    def __init__(self, alfa: float = 1.0) -> None:
        self.alfa = alfa
        self.contagens: dict[str, Counter] = defaultdict(Counter)
        self.docs: Counter = Counter()
        self.vocab: set[str] = set()

    def treinar(self, exemplos: list[tuple[str, str]]) -> "NaiveBayes":
        for texto, classe in exemplos:
            toks = _tokens(texto)
            self.docs[classe] += 1
            self.contagens[classe].update(toks)
            self.vocab.update(toks)
        return self

    def log_probs(self, texto: str) -> dict[str, float]:
        if not self.docs:
            raise ValueError("modelo não treinado")
        total_docs = sum(self.docs.values())
        v = len(self.vocab)
        res = {}
        for classe, nd in self.docs.items():
            total = sum(self.contagens[classe].values())
            lp = math.log(nd / total_docs)
            for t in _tokens(texto):
                if t in self.vocab:
                    lp += math.log((self.contagens[classe][t] + self.alfa) / (total + self.alfa * v))
            res[classe] = lp
        return res

    def prever(self, texto: str) -> str:
        lp = self.log_probs(texto)
        return max(sorted(lp), key=lambda c: lp[c])


def classificador_padrao() -> NaiveBayes:
    return NaiveBayes().treinar(DATASET)

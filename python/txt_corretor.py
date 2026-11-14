"""Corretor ortográfico estilo Norvig com dicionário pequeno embutido."""
from collections import Counter

from txt_tokenizador import tokenizar

ALFABETO = "abcdefghijklmnopqrstuvwxyzáàâãçéêíóôõú"

DICIONARIO_PADRAO: dict[str, int] = {
    "casa": 50, "carro": 30, "cachorro": 20, "gato": 25, "livro": 40, "escola": 35,
    "amigo": 30, "amiga": 28, "tempo": 45, "água": 30, "comida": 22, "trabalho": 38,
    "brasil": 40, "obrigado": 33, "bom": 60, "dia": 70, "noite": 35, "tarde": 33,
    "manhã": 30, "feliz": 20, "família": 28, "coração": 15, "janela": 12, "porta": 18,
    "mesa": 17, "cadeira": 13, "computador": 14, "programa": 16, "teclado": 8,
    "palavra": 19, "texto": 21, "tudo": 50, "nada": 40, "sempre": 36, "nunca": 30,
    "também": 45,
}


class Corretor:
    def __init__(self, frequencias: dict[str, int] | None = None) -> None:
        self.freq: Counter = Counter(DICIONARIO_PADRAO if frequencias is None else frequencias)

    @classmethod
    def de_texto(cls, texto: str) -> "Corretor":
        return cls(dict(Counter(tokenizar(texto))))

    def conhecida(self, palavra: str) -> bool:
        return self.freq[palavra] > 0

    @staticmethod
    def edicoes1(palavra: str) -> set[str]:
        cortes = [(palavra[:i], palavra[i:]) for i in range(len(palavra) + 1)]
        remocoes = {e + d[1:] for e, d in cortes if d}
        trocas = {e + d[1] + d[0] + d[2:] for e, d in cortes if len(d) > 1}
        substituicoes = {e + c + d[1:] for e, d in cortes if d for c in ALFABETO}
        insercoes = {e + c + d for e, d in cortes for c in ALFABETO}
        return remocoes | trocas | substituicoes | insercoes

    def edicoes2(self, palavra: str) -> set[str]:
        return {e2 for e1 in self.edicoes1(palavra) for e2 in self.edicoes1(e1)}

    def candidatos(self, palavra: str) -> set[str]:
        if self.conhecida(palavra):
            return {palavra}
        e1 = {p for p in self.edicoes1(palavra) if self.conhecida(p)}
        if e1:
            return e1
        e2 = {p for p in self.edicoes2(palavra) if self.conhecida(p)}
        return e2 or {palavra}

    def corrigir(self, palavra: str) -> str:
        """Devolve a correção mais provável (a mais frequente; empate em ordem alfabética)."""
        if not palavra:
            return palavra
        minuscula = palavra.lower()
        melhor = min(self.candidatos(minuscula), key=lambda p: (-self.freq[p], p))
        return melhor.capitalize() if palavra[0].isupper() and melhor else melhor

import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from conc_map_reduce import (
    contar_palavras,
    contar_texto,
    dividir,
    mais_comuns,
    mapear,
    reduzir,
)


class TestMapReduce(unittest.TestCase):
    def test_mapear(self):
        self.assertEqual(mapear("O gato, o rato."), Counter({"o": 2, "gato": 1, "rato": 1}))

    def test_reduzir(self):
        self.assertEqual(reduzir(Counter(a=1), Counter(a=2, b=1)), Counter(a=3, b=1))

    def test_contar_documentos(self):
        docs = ["a b a", "b c", "a"]
        self.assertEqual(contar_palavras(docs), Counter(a=3, b=2, c=1))

    def test_texto_dividido_igual_a_sequencial(self):
        texto = " ".join(["um dois três quatro dois três três"] * 25)
        self.assertEqual(contar_texto(texto, 7), mapear(texto))

    def test_dividir_nao_quebra_palavras(self):
        partes = dividir("a b c d e", 2)
        self.assertEqual(partes, ["a b c", "d e"])
        self.assertEqual(dividir("", 3), [])

    def test_mais_comuns_desempate(self):
        c = Counter(b=2, a=2, z=5, k=1)
        self.assertEqual(mais_comuns(c, 3), [("z", 5), ("a", 2), ("b", 2)])

    def test_vazio_e_invalido(self):
        self.assertEqual(contar_palavras([]), Counter())
        with self.assertRaises(ValueError):
            dividir("a", 0)


if __name__ == "__main__":
    unittest.main()

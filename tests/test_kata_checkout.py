import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_checkout import Checkout, Promocao, total

PRECOS = {"A": 50, "B": 30, "C": 20, "D": 15}
PROMOS = {"A": Promocao(3, 130), "B": Promocao(2, 45)}


class TestKataCheckout(unittest.TestCase):
    def test_vazio(self):
        self.assertEqual(total(PRECOS, PROMOS, ""), 0)

    def test_itens_simples(self):
        self.assertEqual(total(PRECOS, PROMOS, "A"), 50)
        self.assertEqual(total(PRECOS, PROMOS, "AB"), 80)
        self.assertEqual(total(PRECOS, PROMOS, "CDBA"), 115)

    def test_sem_promocao(self):
        self.assertEqual(total(PRECOS, PROMOS, "CC"), 40)

    def test_promocao_a(self):
        self.assertEqual(total(PRECOS, PROMOS, "AA"), 100)
        self.assertEqual(total(PRECOS, PROMOS, "AAA"), 130)
        self.assertEqual(total(PRECOS, PROMOS, "AAAA"), 180)
        self.assertEqual(total(PRECOS, PROMOS, "AAAAA"), 230)
        self.assertEqual(total(PRECOS, PROMOS, "AAAAAA"), 260)

    def test_promocao_b(self):
        self.assertEqual(total(PRECOS, PROMOS, "BB"), 45)
        self.assertEqual(total(PRECOS, PROMOS, "BBB"), 75)
        self.assertEqual(total(PRECOS, PROMOS, "BBBB"), 90)

    def test_ordem_nao_importa(self):
        self.assertEqual(total(PRECOS, PROMOS, "DABABA"), 190)
        self.assertEqual(total(PRECOS, PROMOS, "AAABBD"), 130 + 45 + 15)

    def test_incremental(self):
        caixa = Checkout(PRECOS, PROMOS)
        self.assertEqual(caixa.total(), 0)
        caixa.scan("A")
        self.assertEqual(caixa.total(), 50)
        caixa.scan("B").scan("A")
        self.assertEqual(caixa.total(), 130)
        caixa.scan("A")
        self.assertEqual(caixa.total(), 160)
        caixa.scan("B")
        self.assertEqual(caixa.total(), 175)

    def test_leve_3_pague_2(self):
        caixa = Checkout({"X": 100}, leve_n_pague_m={"X": (3, 2)})
        for _ in range(7):
            caixa.scan("X")
        self.assertEqual(caixa.total(), 500)

    def test_item_desconhecido(self):
        with self.assertRaises(KeyError):
            Checkout(PRECOS).scan("Z")

    def test_preco_negativo(self):
        with self.assertRaises(ValueError):
            Checkout({"A": -1})


if __name__ == "__main__":
    unittest.main()

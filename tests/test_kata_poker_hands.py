import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_poker_hands import comparar, nome_da_mao


class TestKataPokerHands(unittest.TestCase):
    def test_categorias(self):
        casos = {
            "2H 3D 5S 9C KD": "Carta Alta",
            "2H 2D 5S 9C KD": "Par",
            "2H 2D 5S 5C KD": "Dois Pares",
            "2H 2D 2S 9C KD": "Trinca",
            "2H 3D 4S 5C 6D": "Sequência",
            "2H 4H 6H 8H TH": "Flush",
            "2H 2D 2S 9C 9D": "Full House",
            "2H 2D 2S 2C KD": "Quadra",
            "2H 3H 4H 5H 6H": "Straight Flush",
        }
        for mao, nome in casos.items():
            self.assertEqual(nome_da_mao(mao), nome, mao)

    def test_roda_as_baixo(self):
        self.assertEqual(nome_da_mao("AH 2D 3S 4C 5D"), "Sequência")
        self.assertEqual(comparar("AH 2D 3S 4C 5D", "2H 3D 4S 5C 6D"), 2)

    def test_as_alto_na_sequencia(self):
        self.assertEqual(nome_da_mao("TH JD QS KC AD"), "Sequência")

    def test_nao_faz_volta(self):
        self.assertEqual(nome_da_mao("QH KD AS 2C 3D"), "Carta Alta")

    def test_carta_alta_vence(self):
        self.assertEqual(comparar("2H 3D 5S 9C KD", "2C 3H 4S 8C AH"), 2)

    def test_carta_alta_desempate_sucessivo(self):
        self.assertEqual(comparar("2H 3D 5S 9C KD", "2C 3H 4S 9S KH"), 1)

    def test_categoria_maior_vence(self):
        self.assertEqual(comparar("2H 4S 4C 2D 4H", "2S 8S AS QS 3S"), 1)
        self.assertEqual(comparar("2H 3D 5S 9C KD", "2H 2D 5S 9C KD"), 2)

    def test_par_maior_vence(self):
        self.assertEqual(comparar("3H 3D 5S 9C KD", "2H 2D AS QC KD"), 1)

    def test_par_igual_kicker(self):
        self.assertEqual(comparar("4H 4D 5S 9C KD", "4S 4C 5H 9D QD"), 1)

    def test_dois_pares_desempate(self):
        self.assertEqual(comparar("KH KD 2S 2C 9D", "QH QD JS JC AD"), 1)
        self.assertEqual(comparar("KH KD 3S 3C 9D", "KS KC 2H 2D AD"), 1)

    def test_full_house_pela_trinca(self):
        self.assertEqual(comparar("3H 3D 3S 9C 9D", "2H 2D 2S AC AD"), 1)

    def test_empate(self):
        self.assertEqual(comparar("2H 3D 5S 9C KD", "2D 3H 5C 9S KH"), 0)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            nome_da_mao("2H 3D 5S 9C")
        with self.assertRaises(ValueError):
            nome_da_mao("2H 3D 5S 9C 1D")
        with self.assertRaises(ValueError):
            nome_da_mao("2H 2H 5S 9C KD")


if __name__ == "__main__":
    unittest.main()

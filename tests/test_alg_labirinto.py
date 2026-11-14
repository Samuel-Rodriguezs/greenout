import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from alg_labirinto import menor_caminho


class TesteLabirinto(unittest.TestCase):
    def test_linha_reta(self):
        self.assertEqual(menor_caminho(["S..E"]), 3)

    def test_com_desvio(self):
        self.assertEqual(
            menor_caminho([
                "S.#.",
                ".##.",
                "...E",
            ]),
            5,
        )

    def test_sem_caminho(self):
        self.assertEqual(menor_caminho(["S#E"]), -1)

    def test_adjacentes(self):
        self.assertEqual(menor_caminho(["SE"]), 1)

    def test_escolhe_o_mais_curto(self):
        self.assertEqual(
            menor_caminho([
                "S...",
                ".##.",
                "...E",
            ]),
            5,
        )

    def test_sem_entrada_ou_saida(self):
        with self.assertRaises(ValueError):
            menor_caminho(["...E"])
        with self.assertRaises(ValueError):
            menor_caminho([])

    def test_linhas_irregulares(self):
        self.assertEqual(menor_caminho(["S.", ".", "E"]), 2)


if __name__ == "__main__":
    unittest.main()

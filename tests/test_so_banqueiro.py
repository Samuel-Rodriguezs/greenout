import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from so_banqueiro import CONCEDIDO, ESPERA, INSEGURO, Banqueiro


def livro() -> Banqueiro:
    return Banqueiro(
        disponivel=[3, 3, 2],
        alocado=[[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]],
        maximo=[[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]],
    )


class TestBanqueiro(unittest.TestCase):
    def test_matriz_de_necessidade(self):
        b = livro()
        self.assertEqual(
            [b.necessidade(i) for i in range(5)],
            [[7, 4, 3], [1, 2, 2], [6, 0, 0], [0, 1, 1], [4, 3, 1]],
        )

    def test_sequencia_segura_do_livro(self):
        self.assertEqual(livro().sequencia_segura(), [1, 3, 4, 0, 2])

    def test_p1_pede_1_0_2_e_e_concedido(self):
        b = livro()
        self.assertEqual(b.requisitar(1, [1, 0, 2]), CONCEDIDO)
        self.assertEqual(b.disponivel, [2, 3, 0])
        self.assertEqual(b.alocado[1], [3, 0, 2])
        self.assertEqual(b.sequencia_segura(), [1, 3, 4, 0, 2])

    def test_p4_pede_3_3_0_espera_e_p0_pede_0_2_0_inseguro(self):
        b = livro()
        b.requisitar(1, [1, 0, 2])
        self.assertEqual(b.requisitar(4, [3, 3, 0]), ESPERA)
        antes = (list(b.disponivel), [l[:] for l in b.alocado])
        self.assertEqual(b.requisitar(0, [0, 2, 0]), INSEGURO)
        self.assertEqual((b.disponivel, b.alocado), antes)  # estado restaurado

    def test_estado_inseguro_detectado(self):
        b = Banqueiro([0], [[1], [1]], [[2], [2]])  # cada um precisa de mais 1; nada sobra
        self.assertIsNone(b.sequencia_segura())
        self.assertFalse(b.seguro())

    def test_liberar_devolve_recursos(self):
        b = livro()
        b.liberar(2)
        self.assertEqual(b.disponivel, [6, 3, 4])
        self.assertTrue(b.seguro())

    def test_excesso_sobre_o_maximo(self):
        with self.assertRaises(ValueError):
            livro().requisitar(1, [2, 0, 0])  # necessidade de P1 em A é 1

    def test_entradas_invalidas(self):
        with self.assertRaises(ValueError):
            Banqueiro([1, 1], [[1]], [[1]])
        with self.assertRaises(ValueError):
            Banqueiro([1], [[2]], [[1]])
        with self.assertRaises(ValueError):
            livro().requisitar(0, [-1, 0, 0])


if __name__ == "__main__":
    unittest.main()

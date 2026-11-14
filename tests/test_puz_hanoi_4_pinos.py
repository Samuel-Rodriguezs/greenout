import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from puz_hanoi_4_pinos import frame_stewart, resolver, simular


class TestHanoiKPinos(unittest.TestCase):
    def test_tres_pinos_classico(self):
        for n in range(8):
            self.assertEqual(frame_stewart(n, 3), 2 ** n - 1)

    def test_quatro_pinos_sequencia_conhecida(self):
        # OEIS A007664
        self.assertEqual([frame_stewart(n, 4) for n in range(11)],
                         [0, 1, 3, 5, 9, 13, 17, 25, 33, 41, 49])

    def test_cinco_pinos(self):
        # 5 pinos: 2F(k)+F(n-k, 4 pinos)
        self.assertEqual([frame_stewart(n, 5) for n in range(10)],
                         [0, 1, 3, 5, 7, 11, 15, 19, 23, 27])

    def test_impossiveis(self):
        self.assertIsNone(frame_stewart(2, 2))
        self.assertIsNone(frame_stewart(1, 1))
        self.assertEqual(frame_stewart(1, 2), 1)
        self.assertEqual(frame_stewart(0, 1), 0)
        with self.assertRaises(ValueError):
            resolver(3, 2)

    def test_resolver_tem_tamanho_otimo_e_e_valido(self):
        for pinos in (3, 4, 5, 6):
            for n in range(0, 10):
                movs = resolver(n, pinos)
                self.assertEqual(len(movs), frame_stewart(n, pinos), (n, pinos))
                final = simular(n, pinos, movs)
                self.assertEqual(final[-1], list(range(n, 0, -1)))
                self.assertTrue(all(not p for p in final[:-1]))

    def test_simular_rejeita_movimento_invalido(self):
        with self.assertRaises(ValueError):
            simular(2, 3, [(2, 0, 1)])  # disco 2 não está no topo
        with self.assertRaises(ValueError):
            simular(2, 3, [(1, 0, 1), (2, 0, 1)])  # grande sobre pequeno

    def test_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            frame_stewart(-1, 4)


if __name__ == "__main__":
    unittest.main()

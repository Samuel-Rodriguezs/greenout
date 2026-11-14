import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fp_fluxos import (
    FIBONACCI, NATURAIS, PRIMOS, Fluxo, a_partir, de_iteravel, enesimo, filtrar,
    iterar, mapear, pegar, pegar_enquanto, zip_com,
)


class TestFluxos(unittest.TestCase):
    def test_naturais_e_iterar(self):
        self.assertEqual(pegar(5, NATURAIS), [0, 1, 2, 3, 4])
        self.assertEqual(pegar(4, iterar(lambda x: x * 2, 1)), [1, 2, 4, 8])
        self.assertEqual(pegar(0, NATURAIS), [])

    def test_primos(self):
        self.assertEqual(pegar(10, PRIMOS), [2, 3, 5, 7, 11, 13, 17, 19, 23, 29])
        self.assertEqual(enesimo(99, PRIMOS), 541)

    def test_fibonacci(self):
        self.assertEqual(pegar(12, FIBONACCI), [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89])
        self.assertEqual(enesimo(90, FIBONACCI), 2880067194370816120)

    def test_preguica_nao_avalia_a_cauda(self):
        chamadas = []

        def mk(n):
            def cauda():
                chamadas.append(n)
                return mk(n + 1)
            return Fluxo(n, cauda)
        s = mk(0)
        self.assertEqual(chamadas, [])
        self.assertEqual(pegar(3, s), [0, 1, 2])
        self.assertEqual(chamadas, [0, 1])  # a 3a cabeça não exige sua cauda

    def test_memoizacao_da_cauda(self):
        n = []

        def cauda():
            n.append(1)
            return Fluxo(9, lambda: None)
        s = Fluxo(1, cauda)
        self.assertFalse(s.cauda_avaliada)
        a = s.cauda
        b = s.cauda
        self.assertIs(a, b)
        self.assertEqual(len(n), 1)
        self.assertEqual(list(s), [1, 9])
        self.assertEqual(len(n), 1)

    def test_mapear_filtrar_zip(self):
        pares_q = mapear(lambda x: x * x, filtrar(lambda x: x % 2 == 0, NATURAIS))
        self.assertEqual(pegar(4, pares_q), [0, 4, 16, 36])
        soma = zip_com(lambda a, b: a + b, NATURAIS, a_partir(10))
        self.assertEqual(pegar(3, soma), [10, 12, 14])

    def test_finitos_e_bordas(self):
        s = de_iteravel([1, 2, 3])
        self.assertEqual(list(s), [1, 2, 3])
        self.assertIsNone(de_iteravel([]))
        self.assertEqual(pegar(10, s), [1, 2, 3])
        self.assertIsNone(mapear(abs, None))
        self.assertIsNone(filtrar(lambda x: x > 5, de_iteravel([1, 2])))
        with self.assertRaises(IndexError):
            enesimo(5, de_iteravel([1, 2]))
        self.assertEqual(pegar_enquanto(lambda p: p < 20, PRIMOS), [2, 3, 5, 7, 11, 13, 17, 19])


if __name__ == "__main__":
    unittest.main()

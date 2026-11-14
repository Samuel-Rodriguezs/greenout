import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from pa_produtor_consumidor import processar_em_paralelo


class TestProdutorConsumidor(unittest.TestCase):
    def test_ordem_preservada(self):
        self.assertEqual(processar_em_paralelo(range(50), lambda x: x * 2), [x * 2 for x in range(50)])

    def test_vazio(self):
        self.assertEqual(processar_em_paralelo([], str), [])

    def test_aceita_gerador(self):
        r = processar_em_paralelo((i for i in range(5)), lambda x: x + 1, consumidores=1)
        self.assertEqual(r, [1, 2, 3, 4, 5])

    def test_usa_varias_threads(self):
        ids = set()
        barreira = threading.Barrier(2, timeout=5)

        def f(x):
            ids.add(threading.get_ident())
            barreira.wait()
            return x

        self.assertEqual(processar_em_paralelo([1, 2], f, consumidores=2), [1, 2])
        self.assertEqual(len(ids), 2)

    def test_erro_propagado(self):
        def f(x):
            if x == 3:
                raise ValueError("três")
            return x

        with self.assertRaises(ValueError):
            processar_em_paralelo(range(10), f)

    def test_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            processar_em_paralelo([1], str, consumidores=0)
        with self.assertRaises(ValueError):
            processar_em_paralelo([1], str, capacidade=0)

    def test_mais_itens_que_capacidade(self):
        r = processar_em_paralelo(range(100), lambda x: x, consumidores=2, capacidade=1)
        self.assertEqual(r, list(range(100)))


if __name__ == "__main__":
    unittest.main()

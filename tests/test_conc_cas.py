import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from conc_cas import ContadorAtomico, ReferenciaAtomica


class TestCAS(unittest.TestCase):
    def test_cas_sucesso_e_falha(self):
        r = ReferenciaAtomica(5)
        self.assertTrue(r.comparar_e_trocar(5, 6))
        self.assertFalse(r.comparar_e_trocar(5, 7))
        self.assertEqual(r.obter(), 6)
        self.assertEqual(r.falhas_cas, 1)

    def test_atualizar_refaz_apos_corrida(self):
        r = ReferenciaAtomica(0)
        chamadas = []

        def fn(v):
            chamadas.append(v)
            if len(chamadas) == 1:
                r.comparar_e_trocar(0, 100)  # outra "thread" interfere
            return v + 1

        self.assertEqual(r.atualizar(fn), 101)
        self.assertEqual(chamadas, [0, 100])

    def test_contador_concorrente(self):
        c = ContadorAtomico()

        def trabalhar():
            for _ in range(1000):
                c.incrementar()

        ts = [threading.Thread(target=trabalhar) for _ in range(4)]
        for t in ts:
            t.start()
        for t in ts:
            t.join(5)
        self.assertEqual(c.valor, 4000)

    def test_operacoes(self):
        c = ContadorAtomico(10)
        self.assertEqual(c.incrementar(5), 15)
        self.assertEqual(c.decrementar(), 14)
        self.assertEqual(c.obter_e_incrementar(), 14)
        self.assertEqual(c.valor, 15)

    def test_comparar_e_definir(self):
        c = ContadorAtomico(1)
        self.assertTrue(c.comparar_e_definir(1, 9))
        self.assertFalse(c.comparar_e_definir(1, 3))
        self.assertEqual(c.valor, 9)

    def test_maximo(self):
        c = ContadorAtomico(5)
        self.assertEqual(c.maximo(3), 5)
        self.assertEqual(c.maximo(8), 8)


if __name__ == "__main__":
    unittest.main()

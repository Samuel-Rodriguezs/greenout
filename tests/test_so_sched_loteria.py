import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from so_sched_loteria import Lcg, Loteria, Stride


class TestLoteria(unittest.TestCase):
    def test_intervalos_de_bilhetes(self):
        lot = Loteria()
        lot.adicionar("A", 75)
        lot.adicionar("B", 25)
        self.assertEqual(lot.total, 100)
        self.assertEqual(lot.sortear([0, 74, 75, 99, 100, 175]), ["A", "A", "B", "B", "A", "B"])

    def test_remover_muda_total(self):
        lot = Loteria()
        lot.adicionar("A", 1)
        lot.adicionar("B", 1)
        lot.remover("A")
        self.assertEqual(lot.sortear([0, 1, 2]), ["B", "B", "B"])

    def test_lcg_reprodutivel_e_proporcional(self):
        def corrida():
            lot = Loteria()
            lot.adicionar("A", 90)
            lot.adicionar("B", 10)
            g = Lcg(42)
            return lot.sortear(g.proximo() for _ in range(5000))

        a, b = corrida(), corrida()
        self.assertEqual(a, b)
        c = Counter(a)
        self.assertGreater(c["A"], 4300)
        self.assertLess(c["A"], 4700)

    def test_erros(self):
        lot = Loteria()
        with self.assertRaises(ValueError):
            lot.vencedor(1)
        with self.assertRaises(ValueError):
            lot.adicionar("A", 0)
        lot.adicionar("A", 1)
        with self.assertRaises(ValueError):
            lot.adicionar("A", 1)


class TestStride(unittest.TestCase):
    def _sched(self):
        s = Stride()
        s.adicionar("A", 100)  # passo 100
        s.adicionar("B", 50)  # passo 200
        s.adicionar("C", 250)  # passo 40
        return s

    def test_passos(self):
        s = self._sched()
        self.assertEqual(s.passo, {"A": 100, "B": 200, "C": 40})

    def test_sequencia_ate_o_primeiro_empate(self):
        seq = list(self._sched().rodar(8))
        self.assertEqual(seq, ["A", "B", "C", "C", "C", "A", "C", "C"])

    def test_proporcao_exata_por_periodo(self):
        s = self._sched()
        contagem = Counter(s.rodar(80))
        self.assertEqual(contagem, {"A": 20, "B": 10, "C": 50})

    def test_entrada_tardia_nao_monopoliza(self):
        s = self._sched()
        list(s.rodar(8))  # passagens: 200, 200, 200
        s.adicionar("D", 100)
        self.assertEqual(s.passagem["D"], 200)
        seq = list(s.rodar(4))
        self.assertEqual(Counter(seq)["D"], 1)

    def test_remover_e_vazio(self):
        s = Stride()
        with self.assertRaises(ValueError):
            s.proximo()
        s.adicionar("A", 10)
        s.remover("A")
        with self.assertRaises(ValueError):
            s.proximo()
        with self.assertRaises(ValueError):
            s.adicionar("B", 0)


if __name__ == "__main__":
    unittest.main()

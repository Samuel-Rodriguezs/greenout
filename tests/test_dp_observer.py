import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_observer import Acao, AlertaQueda


class TestObserver(unittest.TestCase):
    def test_notifica_mudanca(self):
        a = Acao("PETR4", 30.0)
        log = []
        a.assinar(lambda s, o, n: log.append((s, o, n)))
        a.preco = 31.0
        self.assertEqual(log, [("PETR4", 30.0, 31.0)])

    def test_sem_mudanca_nao_notifica(self):
        a = Acao("X", 1.0)
        log = []
        a.assinar(lambda *args: log.append(args))
        a.preco = 1.0
        self.assertEqual(log, [])

    def test_cancelar(self):
        a = Acao("X", 10.0)
        log = []
        cancelar = a.assinar(lambda *args: log.append(args))
        cancelar()
        cancelar()
        a.preco = 11.0
        self.assertEqual(log, [])

    def test_alerta_queda(self):
        a = Acao("VALE3", 100.0)
        alerta = AlertaQueda(5)
        a.assinar(alerta)
        a.preco = 98.0
        a.preco = 90.0
        self.assertEqual(alerta.alertas, ["VALE3 caiu 8.2%"])

    def test_varios_assinantes(self):
        a = Acao("X", 1.0)
        c1, c2 = [], []
        a.assinar(lambda *x: c1.append(x))
        a.assinar(lambda *x: c2.append(x))
        a.preco = 2.0
        self.assertEqual(len(c1), len(c2))
        self.assertEqual(len(c1), 1)


if __name__ == "__main__":
    unittest.main()

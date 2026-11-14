import sys
import threading
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from conc_semaforo_justo import SemaforoJusto


def esperar_ate(cond, limite=2.0):
    fim = time.monotonic() + limite
    while not cond():
        if time.monotonic() > fim:
            raise AssertionError("condição não atingida")
        time.sleep(0)


class TestSemaforoJusto(unittest.TestCase):
    def test_ordem_fifo(self):
        s = SemaforoJusto(0)
        ordem = []
        ts = []
        for i in range(5):
            def w(i=i):
                s.adquirir(2)
                ordem.append(i)

            t = threading.Thread(target=w)
            t.start()
            ts.append(t)
            esperar_ate(lambda: s.aguardando >= i + 1)  # garante ordem de chegada
        for k in range(5):
            s.liberar()
            esperar_ate(lambda: len(ordem) >= k + 1)
        for t in ts:
            t.join(2)
        self.assertEqual(ordem, [0, 1, 2, 3, 4])

    def test_valor_inicial(self):
        s = SemaforoJusto(2)
        self.assertTrue(s.adquirir())
        self.assertTrue(s.adquirir())
        self.assertFalse(s.adquirir(0.01))
        s.liberar()
        self.assertEqual(s.valor, 1)

    def test_timeout_remove_da_fila(self):
        s = SemaforoJusto(0)
        self.assertFalse(s.adquirir(0.01))
        self.assertEqual(s.aguardando, 0)

    def test_nao_fura_fila(self):
        s = SemaforoJusto(0)
        t = threading.Thread(target=lambda: s.adquirir(2))
        t.start()
        esperar_ate(lambda: s.aguardando >= 1)
        s.liberar()  # vai para quem espera, não incrementa valor
        t.join(2)
        self.assertEqual(s.valor, 0)

    def test_contexto(self):
        s = SemaforoJusto(1)
        with s:
            self.assertEqual(s.valor, 0)
        self.assertEqual(s.valor, 1)

    def test_invalido(self):
        with self.assertRaises(ValueError):
            SemaforoJusto(-1)


if __name__ == "__main__":
    unittest.main()

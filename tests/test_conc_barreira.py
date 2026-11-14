import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from conc_barreira import BarreiraReutilizavel


class TestBarreira(unittest.TestCase):
    def test_fases_sincronizadas(self):
        n, fases = 4, 5
        b = BarreiraReutilizavel(n)
        lock = threading.Lock()
        contagem = [0] * fases
        violacoes = []

        def worker():
            for f in range(fases):
                with lock:
                    contagem[f] += 1
                b.esperar(2)
                with lock:
                    # após a barreira, todos já devem ter registrado a fase f
                    if contagem[f] != n:
                        violacoes.append(f)
                b.esperar(2)

        ts = [threading.Thread(target=worker) for _ in range(n)]
        for t in ts:
            t.start()
        for t in ts:
            t.join(3)
        self.assertEqual(violacoes, [])
        self.assertEqual(contagem, [n] * fases)
        self.assertEqual(b.geracao, fases * 2)

    def test_acao_executada_uma_vez_por_ciclo(self):
        chamadas = []
        b = BarreiraReutilizavel(2, lambda: chamadas.append(1))

        def worker():
            for _ in range(3):
                b.esperar(2)

        ts = [threading.Thread(target=worker) for _ in range(2)]
        for t in ts:
            t.start()
        for t in ts:
            t.join(3)
        self.assertEqual(len(chamadas), 3)

    def test_timeout(self):
        b = BarreiraReutilizavel(2)
        with self.assertRaises(TimeoutError):
            b.esperar(0.01)
        self.assertEqual(b.geracao, 0)

    def test_uma_parte(self):
        b = BarreiraReutilizavel(1)
        b.esperar()
        b.esperar()
        self.assertEqual(b.geracao, 2)

    def test_invalida(self):
        with self.assertRaises(ValueError):
            BarreiraReutilizavel(0)


if __name__ == "__main__":
    unittest.main()

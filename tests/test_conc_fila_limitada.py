import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from conc_fila_limitada import FilaLimitada


class TestFilaLimitada(unittest.TestCase):
    def test_fifo(self):
        f = FilaLimitada(3)
        for i in range(3):
            f.colocar(i)
        self.assertEqual([f.retirar() for _ in range(3)], [0, 1, 2])

    def test_cheia_timeout(self):
        f = FilaLimitada(1)
        f.colocar(1)
        with self.assertRaises(TimeoutError):
            f.colocar(2, timeout=0.01)

    def test_vazia_timeout(self):
        with self.assertRaises(TimeoutError):
            FilaLimitada(1).retirar(timeout=0.01)

    def test_produtor_consumidor(self):
        f = FilaLimitada(2)
        recebidos = []

        def produtor():
            for i in range(50):
                f.colocar(i)
            f.fechar()

        def consumidor():
            while True:
                try:
                    recebidos.append(f.retirar(timeout=2))
                except EOFError:
                    return

        ts = [threading.Thread(target=produtor), threading.Thread(target=consumidor)]
        for t in ts:
            t.start()
        for t in ts:
            t.join(3)
        self.assertEqual(recebidos, list(range(50)))

    def test_fechar_acorda_consumidor(self):
        f = FilaLimitada(1)
        erro = []

        def consumir():
            try:
                f.retirar(timeout=2)
            except EOFError as e:
                erro.append(e)

        t = threading.Thread(target=consumir)
        t.start()
        f.fechar()
        t.join(2)
        self.assertEqual(len(erro), 1)

    def test_colocar_em_fechada(self):
        f = FilaLimitada(1)
        f.fechar()
        with self.assertRaises(RuntimeError):
            f.colocar(1)

    def test_capacidade_invalida(self):
        with self.assertRaises(ValueError):
            FilaLimitada(0)


if __name__ == "__main__":
    unittest.main()

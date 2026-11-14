import sys
import threading
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from conc_leitores_escritores import LockLeitoresEscritores


def esperar_ate(cond, limite=2.0):
    fim = time.monotonic() + limite
    while not cond():
        if time.monotonic() > fim:
            raise AssertionError("condição não atingida")
        time.sleep(0)


class TestLeitoresEscritores(unittest.TestCase):
    def test_leitores_simultaneos(self):
        lock = LockLeitoresEscritores()
        barreira = threading.Barrier(3, timeout=2)

        def leitor():
            with lock.leitura():
                barreira.wait()  # só passa se os 3 leem ao mesmo tempo

        ts = [threading.Thread(target=leitor) for _ in range(3)]
        for t in ts:
            t.start()
        for t in ts:
            t.join(3)
        self.assertFalse(barreira.broken)
        self.assertEqual(lock.leitores, 0)

    def test_escritor_exclusivo(self):
        lock = LockLeitoresEscritores()
        lock.adquirir_leitura()
        entrou = threading.Event()

        def escritor():
            with lock.escrita():
                entrou.set()

        t = threading.Thread(target=escritor)
        t.start()
        self.assertFalse(entrou.wait(0.05))
        lock.liberar_leitura()
        self.assertTrue(entrou.wait(2))
        t.join(2)

    def test_escritor_tem_preferencia(self):
        lock = LockLeitoresEscritores()
        lock.adquirir_leitura()
        ordem = []

        def escritor():
            with lock.escrita():
                ordem.append("e")

        def leitor_novo():
            with lock.leitura():
                ordem.append("l")

        te = threading.Thread(target=escritor)
        te.start()
        esperar_ate(lambda: lock._escritores_esperando == 1)
        tl = threading.Thread(target=leitor_novo)
        tl.start()
        time.sleep(0.02)
        self.assertEqual(ordem, [])  # leitor novo não fura o escritor
        lock.liberar_leitura()
        te.join(2)
        tl.join(2)
        self.assertEqual(ordem, ["e", "l"])

    def test_contador_protegido(self):
        lock = LockLeitoresEscritores()
        total = [0]

        def inc():
            for _ in range(200):
                with lock.escrita():
                    v = total[0]
                    total[0] = v + 1

        ts = [threading.Thread(target=inc) for _ in range(4)]
        for t in ts:
            t.start()
        for t in ts:
            t.join(3)
        self.assertEqual(total[0], 800)

    def test_liberar_sem_adquirir(self):
        lock = LockLeitoresEscritores()
        with self.assertRaises(RuntimeError):
            lock.liberar_leitura()
        with self.assertRaises(RuntimeError):
            lock.liberar_escrita()


if __name__ == "__main__":
    unittest.main()

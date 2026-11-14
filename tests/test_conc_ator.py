import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from conc_ator import Ator, contador


class TestAtor(unittest.TestCase):
    def test_mensagens_em_ordem(self):
        a = Ator(lambda estado, m: estado + [m], [])
        for i in range(20):
            a.enviar(i)
        self.assertEqual(a.parar(), list(range(20)))

    def test_contador_perguntar(self):
        c = contador()
        for _ in range(5):
            c.enviar("inc")
        c.enviar("dec")
        self.assertEqual(c.perguntar("valor"), 4)
        c.parar()

    def test_envios_concorrentes(self):
        c = contador()

        def spam():
            for _ in range(100):
                c.enviar("inc")

        ts = [threading.Thread(target=spam) for _ in range(4)]
        for t in ts:
            t.start()
        for t in ts:
            t.join(2)
        self.assertEqual(c.parar(), 400)

    def test_erro_nao_derruba_ator(self):
        c = contador()
        c.enviar("lixo")
        c.enviar("inc")
        self.assertEqual(c.parar(), 1)
        self.assertEqual(len(c.erros), 1)

    def test_enviar_apos_parar(self):
        c = contador()
        c.parar()
        with self.assertRaises(RuntimeError):
            c.enviar("inc")


if __name__ == "__main__":
    unittest.main()

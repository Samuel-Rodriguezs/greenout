import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ml_rede_xor import RedeNeural, treinar_xor, XOR_X, XOR_Y


class TestRedeXor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.treinada = treinar_xor(seed=1, epocas=4000)

    def test_resolve_xor(self):
        rede = self.treinada
        previsto = [round(rede.prever(x)) for x in XOR_X]
        self.assertEqual(previsto, [0, 1, 1, 0])

    def test_erro_diminui(self):
        rede = RedeNeural(seed=1)
        antes = sum(0.5 * (rede.prever(x) - a) ** 2 for x, a in zip(XOR_X, XOR_Y))
        depois = rede.treinar(XOR_X, XOR_Y, epocas=1500)
        self.assertLess(depois, antes)

    def test_saida_em_01(self):
        rede = RedeNeural(seed=3)
        for x in XOR_X:
            self.assertTrue(0.0 < rede.prever(x) < 1.0)

    def test_deterministico(self):
        a = treinar_xor(seed=2, epocas=200)
        b = treinar_xor(seed=2, epocas=200)
        self.assertEqual(a.w1, b.w1)

    def test_confianca_alta(self):
        rede = self.treinada
        self.assertLess(rede.prever([0, 0]), 0.2)
        self.assertGreater(rede.prever([0, 1]), 0.8)


if __name__ == "__main__":
    unittest.main()

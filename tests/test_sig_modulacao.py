import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import sig_modulacao as m
from sig_espectro import frequencia_dominante
from sig_ondas import senoidal

TAXA = 8000.0


class TestModulacao(unittest.TestCase):
    def test_am_sem_mensagem_e_portadora_pura(self):
        s = m.modular_am([0.0] * 8, 1000, TAXA)
        for n, v in enumerate(s):
            self.assertAlmostEqual(v, math.cos(2 * math.pi * 1000 * n / TAXA))

    def test_am_envelope_limitado(self):
        msg = senoidal(50, TAXA, 800)
        s = m.modular_am(msg, 1000, TAXA, indice=0.5)
        self.assertLessEqual(max(abs(v) for v in s), 1.5 + 1e-9)
        self.assertGreater(max(s), 1.4)

    def test_am_demodulacao_recupera_mensagem(self):
        msg = senoidal(20, TAXA, 1600, amp=1.0)
        s = m.modular_am(msg, 1000, TAXA, indice=0.5)
        env = m.demodular_am(s, 16)
        # envelope ~ 1 + 0.5 msg; a correlação com a mensagem deve ser alta
        e = [v - sum(env) / len(env) for v in env]
        num = sum(a * b for a, b in zip(e, msg))
        den = math.sqrt(sum(a * a for a in e) * sum(b * b for b in msg))
        self.assertGreater(num / den, 0.95)

    def test_am_espectro_tem_portadora(self):
        s = m.modular_am(senoidal(100, TAXA, 1024), 1000, TAXA)
        self.assertAlmostEqual(frequencia_dominante(s, TAXA), 1000, delta=10)

    def test_fm_mensagem_constante_desloca_frequencia(self):
        s = m.modular_fm([1.0] * 400, 1000, TAXA, desvio=500)
        f = m.frequencia_instantanea(s, TAXA)
        self.assertAlmostEqual(sum(f[5:100]) / len(f[5:100]), 1500, delta=5)

    def test_fm_sem_mensagem_mantem_portadora(self):
        s = m.modular_fm([0.0] * 100, 1000, TAXA, desvio=300)
        f = m.frequencia_instantanea(s, TAXA)
        self.assertAlmostEqual(f[10], 1000, delta=1)

    def test_fm_amplitude_constante(self):
        s = m.modular_fm(senoidal(30, TAXA, 500), 1500, TAXA, 200)
        self.assertTrue(all(abs(v) <= 1 + 1e-12 for v in s))

    def test_validacao(self):
        with self.assertRaises(ValueError):
            m.modular_am([0], 5000, TAXA)
        with self.assertRaises(ValueError):
            m.modular_fm([0], 1000, TAXA, -1)
        with self.assertRaises(ValueError):
            m.demodular_am([0], 0)

    def test_vazio(self):
        self.assertEqual(m.modular_am([], 1000, TAXA), [])
        self.assertEqual(m.frequencia_instantanea([1.0, 2.0], TAXA), [])


if __name__ == "__main__":
    unittest.main()

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import sig_notas as n


class TestNotas(unittest.TestCase):
    def test_a4(self):
        self.assertEqual(n.midi_para_frequencia(69), 440.0)
        self.assertEqual(n.frequencia_para_midi(440), 69.0)

    def test_do_central(self):
        self.assertAlmostEqual(n.midi_para_frequencia(60), 261.6256, places=3)
        self.assertEqual(n.nome_para_midi("C4"), 60)
        self.assertEqual(n.midi_para_nome(60), "C4")

    def test_oitava(self):
        self.assertAlmostEqual(n.midi_para_frequencia(81), 880.0)
        self.assertAlmostEqual(n.frequencia_para_midi(220), 57.0)

    def test_nomes_e_acidentes(self):
        self.assertEqual(n.midi_para_nome(61), "C#4")
        self.assertEqual(n.nome_para_midi("Db4"), 61)
        self.assertEqual(n.nome_para_midi("a4"), 69)
        self.assertEqual(n.nome_para_midi("C-1"), 0)
        self.assertEqual(n.nome_para_midi("G9"), 127)
        self.assertEqual(n.midi_para_nome(0), "C-1")

    def test_ida_e_volta_todas(self):
        for m in range(128):
            self.assertEqual(n.nome_para_midi(n.midi_para_nome(m)), m)
            self.assertAlmostEqual(n.frequencia_para_midi(n.midi_para_frequencia(m)), m)

    def test_nota_mais_proxima(self):
        nome, c = n.nota_mais_proxima(440)
        self.assertEqual(nome, "A4")
        self.assertAlmostEqual(c, 0.0, places=6)
        nome, c = n.nota_mais_proxima(446)
        self.assertEqual(nome, "A4")
        self.assertAlmostEqual(c, 23.46, places=1)
        self.assertEqual(n.nota_mais_proxima(430)[0], "A4")
        self.assertLess(n.nota_mais_proxima(430)[1], 0)

    def test_a4_alternativo(self):
        self.assertAlmostEqual(n.frequencia_do_nome("A4", a4=432), 432.0)
        self.assertAlmostEqual(n.frequencia_do_nome("A5"), 880.0)

    def test_cents(self):
        self.assertAlmostEqual(n.cents(440, 880), 1200)
        self.assertAlmostEqual(n.cents(440, 440 * 2 ** (1 / 12)), 100)

    def test_erros(self):
        for ruim in ("H4", "C", "", "C#", "C##4"):
            with self.assertRaises(ValueError):
                n.nome_para_midi(ruim)
        with self.assertRaises(ValueError):
            n.nome_para_midi("A9")
        with self.assertRaises(ValueError):
            n.midi_para_nome(128)
        with self.assertRaises(ValueError):
            n.frequencia_para_midi(0)
        with self.assertRaises(ValueError):
            n.cents(0, 1)


if __name__ == "__main__":
    unittest.main()

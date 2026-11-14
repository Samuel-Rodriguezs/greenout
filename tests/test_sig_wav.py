import os
import sys
import tempfile
import unittest
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import sig_wav as w
from sig_ondas import senoidal


class TestWav(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.caminho = os.path.join(self.dir.name, "t.wav")

    def tearDown(self):
        self.dir.cleanup()

    def test_ida_e_volta_mono(self):
        x = senoidal(440, 8000, 800, amp=0.8)
        w.escrever(self.caminho, x, 8000)
        y, taxa, canais = w.ler(self.caminho)
        self.assertEqual((taxa, canais, len(y)), (8000, 1, 800))
        for a, b in zip(x, y):
            self.assertAlmostEqual(a, b, delta=1 / 32767)

    def test_cabecalho(self):
        w.escrever(self.caminho, [0.0] * 100, 22050)
        with wave.open(self.caminho, "rb") as f:
            self.assertEqual(f.getsampwidth(), 2)
            self.assertEqual(f.getframerate(), 22050)
            self.assertEqual(f.getnframes(), 100)

    def test_estereo_e_separacao(self):
        inter = [0.5, -0.5, 0.25, -0.25]
        w.escrever(self.caminho, inter, 8000, canais=2)
        y, _, canais = w.ler(self.caminho)
        self.assertEqual(canais, 2)
        esq, dir_ = w.separar_canais(y, canais)
        self.assertAlmostEqual(esq[1], 0.25, places=4)
        self.assertAlmostEqual(dir_[0], -0.5, places=4)

    def test_saturacao(self):
        self.assertEqual(w.para_pcm16([2.0, -2.0, 1.0, 0.0]), [32767, -32768, 32767, 0])

    def test_de_pcm16(self):
        self.assertEqual(w.de_pcm16([32767, 0]), [1.0, 0.0])
        self.assertEqual(w.de_pcm16([-32768])[0], -1.0)

    def test_duracao(self):
        w.escrever(self.caminho, [0.0] * 4000, 8000)
        self.assertAlmostEqual(w.duracao(self.caminho), 0.5)

    def test_arquivo_vazio(self):
        w.escrever(self.caminho, [], 8000)
        self.assertEqual(w.ler(self.caminho)[0], [])

    def test_erros(self):
        with self.assertRaises(ValueError):
            w.escrever(self.caminho, [0.0] * 3, 8000, canais=2)
        with self.assertRaises(ValueError):
            w.escrever(self.caminho, [0.0], 0)

    def test_rejeita_8_bits(self):
        with wave.open(self.caminho, "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(1)
            f.setframerate(8000)
            f.writeframes(b"\x80\x80")
        with self.assertRaises(ValueError):
            w.ler(self.caminho)


if __name__ == "__main__":
    unittest.main()

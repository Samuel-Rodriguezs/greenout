import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from proj_semaforo import Semaforo, linha_do_tempo


class TestSemaforo(unittest.TestCase):
    def test_ciclo(self):
        s = Semaforo("verde")
        self.assertEqual([s.avancar() for _ in range(3)], ["amarelo", "vermelho", "verde"])

    def test_tick_troca_estado(self):
        s = Semaforo("verde")
        self.assertEqual(s.tick(29), "verde")
        self.assertEqual(s.restante, 1)
        self.assertEqual(s.tick(1), "amarelo")

    def test_tick_varios_estados(self):
        s = Semaforo("verde")
        self.assertEqual(s.tick(30 + 5 + 3), "vermelho")
        self.assertEqual(s.restante, 17)

    def test_pode_passar(self):
        self.assertTrue(Semaforo("verde").pode_passar())
        self.assertFalse(Semaforo("amarelo").pode_passar())

    def test_linha_do_tempo(self):
        self.assertEqual(
            linha_do_tempo("verde", 60),
            [("verde", 0), ("amarelo", 30), ("vermelho", 35), ("verde", 55)],
        )

    def test_erros(self):
        with self.assertRaises(ValueError):
            Semaforo("azul")
        with self.assertRaises(ValueError):
            Semaforo().tick(-1)


if __name__ == "__main__":
    unittest.main()

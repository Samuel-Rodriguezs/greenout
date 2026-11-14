import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_mars_rover import Rover


class TestKataMarsRover(unittest.TestCase):
    def test_sem_comandos(self):
        self.assertEqual(Rover(0, 0, "N").executar(""), "0:0:N")

    def test_girar(self):
        self.assertEqual(Rover(0, 0, "N").executar("R"), "0:0:E")
        self.assertEqual(Rover(0, 0, "N").executar("L"), "0:0:W")
        self.assertEqual(Rover(0, 0, "N").executar("RRRR"), "0:0:N")

    def test_avancar_e_recuar(self):
        self.assertEqual(Rover(0, 0, "N").executar("FF"), "0:2:N")
        self.assertEqual(Rover(5, 5, "E").executar("B"), "4:5:E")

    def test_wrap(self):
        self.assertEqual(Rover(0, 9, "N").executar("F"), "0:0:N")
        self.assertEqual(Rover(0, 0, "W").executar("F"), "9:0:W")
        self.assertEqual(Rover(0, 0, "S").executar("F"), "0:9:S")

    def test_percurso(self):
        self.assertEqual(Rover(0, 0, "N").executar("FFRFF"), "2:2:E")

    def test_obstaculo(self):
        r = Rover(0, 0, "N", obstaculos={(0, 2)})
        self.assertEqual(r.executar("FFF"), "O:0:1:N")

    def test_comando_invalido(self):
        with self.assertRaises(ValueError):
            Rover(0, 0, "N").executar("X")
        with self.assertRaises(ValueError):
            Rover(0, 0, "Z")


if __name__ == "__main__":
    unittest.main()

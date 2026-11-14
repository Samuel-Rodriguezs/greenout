import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dt_signo import ELEMENTOS, elemento, signo


class TestSigno(unittest.TestCase):
    def test_bordas(self) -> None:
        casos = [
            ((1, 19), "Capricórnio"), ((1, 20), "Aquário"),
            ((2, 18), "Aquário"), ((2, 19), "Peixes"),
            ((3, 20), "Peixes"), ((3, 21), "Áries"),
            ((4, 19), "Áries"), ((4, 20), "Touro"),
            ((5, 20), "Touro"), ((5, 21), "Gêmeos"),
            ((6, 20), "Gêmeos"), ((6, 21), "Câncer"),
            ((7, 22), "Câncer"), ((7, 23), "Leão"),
            ((8, 22), "Leão"), ((8, 23), "Virgem"),
            ((9, 22), "Virgem"), ((9, 23), "Libra"),
            ((10, 22), "Libra"), ((10, 23), "Escorpião"),
            ((11, 21), "Escorpião"), ((11, 22), "Sagitário"),
            ((12, 21), "Sagitário"), ((12, 22), "Capricórnio"),
            ((12, 31), "Capricórnio"), ((1, 1), "Capricórnio"),
        ]
        for (m, d), esperado in casos:
            with self.subTest(m=m, d=d):
                self.assertEqual(signo(mes=m, dia=d), esperado)

    def test_com_date(self) -> None:
        self.assertEqual(signo(date(2026, 11, 14)), "Escorpião")
        self.assertEqual(signo(date(2000, 2, 29)), "Peixes")

    def test_invalidos(self) -> None:
        with self.assertRaises(ValueError):
            signo()
        with self.assertRaises(ValueError):
            signo(mes=2, dia=30)
        with self.assertRaises(ValueError):
            signo(mes=13, dia=1)

    def test_elementos(self) -> None:
        self.assertEqual(len(ELEMENTOS), 12)
        self.assertEqual(elemento("Leão"), "Fogo")
        self.assertEqual(elemento(signo(mes=7, dia=1)), "Água")


if __name__ == "__main__":
    unittest.main()

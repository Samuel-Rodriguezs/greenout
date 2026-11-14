import subprocess
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash" / "temperatura.sh"


def executar(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


class TestTemperatura(unittest.TestCase):
    def converte(self, valor, de, para):
        r = executar(valor, de, para)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def test_celsius_para_fahrenheit(self):
        self.assertEqual(self.converte("100", "C", "F"), "212.00")
        self.assertEqual(self.converte("0", "C", "F"), "32.00")
        self.assertEqual(self.converte("-40", "C", "F"), "-40.00")

    def test_fahrenheit_para_celsius(self):
        self.assertEqual(self.converte("212", "F", "C"), "100.00")
        self.assertEqual(self.converte("32", "F", "C"), "0.00")

    def test_kelvin(self):
        self.assertEqual(self.converte("0", "C", "K"), "273.15")
        self.assertEqual(self.converte("273.15", "K", "C"), "0.00")
        self.assertEqual(self.converte("373.15", "K", "F"), "212.00")

    def test_mesma_escala_e_minusculas(self):
        self.assertEqual(self.converte("36.6", "c", "c"), "36.60")
        self.assertEqual(self.converte("100", "c", "f"), "212.00")

    def test_valor_invalido(self):
        for valor in ("abc", "1e3", "--5", ""):
            r = executar(valor, "C", "F")
            self.assertEqual(r.returncode, 2, repr(valor))
            self.assertIn("invalido", r.stderr)

    def test_escala_invalida(self):
        r = executar("10", "X", "C")
        self.assertEqual(r.returncode, 2)
        self.assertIn("escala invalida", r.stderr)

    def test_kelvin_negativo(self):
        r = executar("-1", "K", "C")
        self.assertEqual(r.returncode, 2)
        self.assertIn("Kelvin", r.stderr)

    def test_help_e_argumentos(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)
        self.assertEqual(executar("1", "C").returncode, 2)


if __name__ == "__main__":
    unittest.main()

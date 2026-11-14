import subprocess
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash" / "fizzbuzz.sh"


def executar(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


class TestFizzBuzzBash(unittest.TestCase):
    def test_primeiros_quinze(self):
        r = executar("15")
        self.assertEqual(r.returncode, 0, r.stderr)
        esperado = ["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz",
                    "Buzz", "11", "Fizz", "13", "14", "FizzBuzz"]
        self.assertEqual(r.stdout.splitlines(), esperado)

    def test_zero_nao_imprime_nada(self):
        r = executar("0")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout, "")

    def test_zeros_a_esquerda_nao_viram_octal(self):
        r = executar("09")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len(r.stdout.splitlines()), 9)

    def test_entrada_invalida(self):
        for valor in ("abc", "-1", "1.5", ""):
            r = executar(valor)
            self.assertEqual(r.returncode, 2, repr(valor))
            self.assertIn("inteiro", r.stderr)

    def test_help_e_sem_argumentos(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)
        self.assertEqual(executar().returncode, 2)


if __name__ == "__main__":
    unittest.main()

import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-lib" / "matematica.sh"


def executar(*args, entrada=None, env=None):
    return subprocess.run(["bash", str(SCRIPT), *args], input=entrada,
                          capture_output=True, text=True, env=env)


class TestMatematica(unittest.TestCase):
    def test_gcd_lcm(self):
        self.assertEqual(executar("gcd", "48", "18").stdout, "6\n")
        self.assertEqual(executar("lcm", "4", "6").stdout, "12\n")
        self.assertEqual(executar("gcd", "7", "0").stdout, "7\n")

    def test_primo(self):
        r = executar("primo", "97")
        self.assertEqual((r.returncode, r.stdout), (0, "sim\n"))
        r = executar("primo", "91")
        self.assertEqual((r.returncode, r.stdout), (1, "nao\n"))
        self.assertEqual(executar("primo", "1").returncode, 1)

    def test_primos_ate(self):
        self.assertEqual(executar("primos_ate", "20").stdout.split(), ["2", "3", "5", "7", "11", "13", "17", "19"])

    def test_fatorial(self):
        self.assertEqual(executar("fatorial", "0").stdout, "1\n")
        self.assertEqual(executar("fatorial", "10").stdout, "3628800\n")
        self.assertEqual(executar("fatorial", "20").stdout, "2432902008176640000\n")
        self.assertEqual(executar("fatorial", "21").returncode, 2)

    def test_converter(self):
        self.assertEqual(executar("converter", "255", "10", "16").stdout, "FF\n")
        self.assertEqual(executar("converter", "ff", "16", "2").stdout, "11111111\n")
        self.assertEqual(executar("converter", "0", "10", "2").stdout, "0\n")
        self.assertEqual(executar("converter", "zz", "36", "10").stdout, "1295\n")

    def test_source(self):
        r = subprocess.run(["bash", "-c", f'source "{SCRIPT}"; mat_gcd 12 8'], capture_output=True, text=True)
        self.assertEqual(r.stdout, "4\n")

    def test_help(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_erros(self):
        self.assertEqual(executar().returncode, 2)
        self.assertEqual(executar("foo").returncode, 2)
        self.assertEqual(executar("gcd", "a", "2").returncode, 2)
        self.assertEqual(executar("gcd", "2").returncode, 2)
        self.assertEqual(executar("converter", "9", "8", "2").returncode, 2)
        self.assertEqual(executar("converter", "1", "1", "2").returncode, 2)


if __name__ == "__main__":
    unittest.main()

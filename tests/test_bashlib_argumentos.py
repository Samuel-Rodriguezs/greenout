import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-lib" / "argumentos.sh"


def executar(*args, entrada=None, env=None):
    return subprocess.run(["bash", str(SCRIPT), *args], input=entrada,
                          capture_output=True, text=True, env=env)


class TestArgumentos(unittest.TestCase):
    def test_saudar(self):
        self.assertEqual(executar("saudar", "-n", "Ana").stdout, "Ola, Ana!\n")
        self.assertEqual(executar("saudar", "-n", "Ana", "-g", "Oi", "-u").stdout, "OI, ANA!\n")

    def test_somar(self):
        self.assertEqual(executar("somar", "1", "2", "3").stdout, "6\n")
        self.assertEqual(executar("somar", "-m", "2", "4", "9").stdout, "5\n")

    def test_inverter(self):
        self.assertEqual(executar("inverter", "abc").stdout, "cba\n")

    def test_verboso(self):
        r = executar("-v", "inverter", "x")
        self.assertEqual(r.returncode, 0)
        self.assertIn("[verbose] subcomando: inverter", r.stderr)

    def test_help(self):
        for flag in ("-h", "--help"):
            r = executar(flag)
            self.assertEqual(r.returncode, 0)
            self.assertIn("Subcomandos", r.stdout)

    def test_erros(self):
        self.assertEqual(executar().returncode, 2)
        self.assertEqual(executar("voar").returncode, 2)
        self.assertEqual(executar("-z", "somar", "1").returncode, 2)
        self.assertEqual(executar("saudar").returncode, 2)
        self.assertEqual(executar("saudar", "-n").returncode, 2)
        self.assertEqual(executar("saudar", "-x", "-n", "A").returncode, 2)
        self.assertEqual(executar("somar").returncode, 2)
        self.assertEqual(executar("somar", "1", "b").returncode, 2)
        self.assertEqual(executar("inverter", "a", "b").returncode, 2)


if __name__ == "__main__":
    unittest.main()

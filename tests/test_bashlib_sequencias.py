import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-lib" / "sequencias.sh"


def executar(*args, entrada=None, env=None):
    return subprocess.run(["bash", str(SCRIPT), *args], input=entrada,
                          capture_output=True, text=True, env=env)


class TestSequencias(unittest.TestCase):
    def test_fib(self):
        self.assertEqual(executar("fib", "10").stdout.split(), "0 1 1 2 3 5 8 13 21 34".split())
        self.assertEqual(executar("fib", "0").stdout, "")
        self.assertEqual(executar("fib", "90").stdout.split()[-1], "1779979416004714189")

    def test_collatz(self):
        self.assertEqual(executar("collatz", "6").stdout.split(), "6 3 10 5 16 8 4 2 1".split())
        self.assertEqual(executar("collatz", "1").stdout, "1\n")

    def test_triangulares(self):
        self.assertEqual(executar("triangulares", "6").stdout.split(), "1 3 6 10 15 21".split())

    def test_perfeitos(self):
        self.assertEqual(executar("perfeitos", "500").stdout.split(), ["6", "28", "496"])

    def test_source(self):
        r = subprocess.run(["bash", "-c", f'source "{SCRIPT}"; seq_triangulares 3'], capture_output=True, text=True)
        self.assertEqual(r.stdout.split(), ["1", "3", "6"])

    def test_help(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_erros(self):
        self.assertEqual(executar().returncode, 2)
        self.assertEqual(executar("zzz", "1").returncode, 2)
        self.assertEqual(executar("fib", "91").returncode, 2)
        self.assertEqual(executar("fib", "x").returncode, 2)
        self.assertEqual(executar("collatz", "0").returncode, 2)
        self.assertEqual(executar("fib").returncode, 2)


if __name__ == "__main__":
    unittest.main()

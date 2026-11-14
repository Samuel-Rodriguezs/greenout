import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-lib" / "arrays.sh"


def executar(*args, entrada=None, env=None):
    return subprocess.run(["bash", str(SCRIPT), *args], input=entrada,
                          capture_output=True, text=True, env=env)


class TestArrays(unittest.TestCase):
    def test_sum_max_min(self):
        self.assertEqual(executar("sum", "1", "2", "-3", "10").stdout, "10\n")
        self.assertEqual(executar("max", "3", "9", "-1").stdout, "9\n")
        self.assertEqual(executar("min", "3", "9", "-1").stdout, "-1\n")

    def test_sort_unique_reverse(self):
        self.assertEqual(executar("sort", "10", "2", "33").stdout, "2\n10\n33\n")
        self.assertEqual(executar("unique", "b", "a", "b", "c", "a").stdout, "b\na\nc\n")
        self.assertEqual(executar("reverse", "1", "2", "3").stdout, "3\n2\n1\n")

    def test_contains(self):
        self.assertEqual(executar("contains", "b", "a", "b").returncode, 0)
        self.assertEqual(executar("contains", "z", "a", "b").returncode, 1)

    def test_freq(self):
        r = executar("freq", "gato", "cao", "gato", "rato", "cao", "gato")
        self.assertEqual(r.stdout, "gato 3\ncao 2\nrato 1\n")

    def test_source(self):
        r = subprocess.run(["bash", "-c", f'source "{SCRIPT}"; arr_sum 1 2 3'], capture_output=True, text=True)
        self.assertEqual(r.stdout, "6\n")

    def test_help(self):
        r = executar("-h")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_erros(self):
        self.assertEqual(executar().returncode, 2)
        self.assertEqual(executar("xyz").returncode, 2)
        self.assertNotEqual(executar("sum", "a").returncode, 0)
        self.assertNotEqual(executar("max").returncode, 0)
        self.assertNotEqual(executar("freq").returncode, 0)


if __name__ == "__main__":
    unittest.main()

import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-lib" / "pascal.sh"


def executar(*args, entrada=None, env=None):
    return subprocess.run(["bash", str(SCRIPT), *args], input=entrada,
                          capture_output=True, text=True, env=env)


class TestPascal(unittest.TestCase):
    def test_cinco_linhas(self):
        r = executar("5")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout, "1\n1 1\n1 2 1\n1 3 3 1\n1 4 6 4 1\n")

    def test_linha_grande(self):
        linhas = executar("11").stdout.splitlines()
        self.assertEqual(linhas[-1], "1 10 45 120 210 252 210 120 45 10 1")

    def test_centralizado(self):
        linhas = executar("-c", "3").stdout.split("\n")
        self.assertEqual(linhas[:3], ["  1", " 1 1", "1 2 1"])

    def test_help(self):
        r = executar("-h")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_erros(self):
        for args in ([], ["0"], ["31"], ["abc"], ["-x", "3"], ["1", "2"]):
            self.assertEqual(executar(*args).returncode, 2, args)


if __name__ == "__main__":
    unittest.main()

import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-lib" / "rpn.sh"


def executar(*args, entrada=None, env=None):
    return subprocess.run(["bash", str(SCRIPT), *args], input=entrada,
                          capture_output=True, text=True, env=env)


class TestRpn(unittest.TestCase):
    def test_expressoes(self):
        casos = {"3 4 +": "7", "5 1 2 + 4 * + 3 -": "14", "2 10 ^": "1024",
                 "17 5 %": "2", "20 3 /": "6", "2 -3 *": "-6", "007 1 +": "8"}
        for expr, esperado in casos.items():
            r = executar(expr)
            self.assertEqual((r.returncode, r.stdout), (0, esperado + "\n"), expr)

    def test_tokens_em_varios_argumentos(self):
        self.assertEqual(executar("3", "4", "*").stdout, "12\n")

    def test_help(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_erros(self):
        self.assertEqual(executar().returncode, 2)
        for expr, trecho in (("1 0 /", "zero"), ("1 +", "pilha"), ("1 2", "sobraram"),
                             ("1 x +", "invalido"), ("2 -1 ^", "expoente"), ("5 0 %", "zero")):
            r = executar(expr)
            self.assertEqual(r.returncode, 1, expr)
            self.assertIn(trecho, r.stderr)


if __name__ == "__main__":
    unittest.main()

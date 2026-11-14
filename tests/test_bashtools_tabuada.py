import subprocess
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-tools" / "tabuada.sh"


def executar(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


class TestTabuada(unittest.TestCase):
    def test_tabuada_padrao(self):
        r = executar("7")
        self.assertEqual(r.returncode, 0, r.stderr)
        linhas = r.stdout.splitlines()
        self.assertEqual(len(linhas), 10)
        self.assertEqual(linhas[0], "7 x 1 = 7")
        self.assertEqual(linhas[-1], "7 x 10 = 70")

    def test_ate_personalizado_e_negativo(self):
        r = executar("-3", "4")
        self.assertEqual(r.stdout.splitlines()[-1], "-3 x 4 = -12")
        self.assertEqual(len(r.stdout.splitlines()), 4)

    def test_help(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_entrada_invalida(self):
        self.assertEqual(executar("abc").returncode, 1)
        self.assertEqual(executar("5", "0").returncode, 1)
        self.assertEqual(executar("5", "2000").returncode, 1)

    def test_sem_argumento(self):
        self.assertEqual(executar().returncode, 1)


if __name__ == "__main__":
    unittest.main()

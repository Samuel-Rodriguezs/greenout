import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-lib" / "forca.sh"


def executar(*args, entrada=None, env=None):
    return subprocess.run(["bash", str(SCRIPT), *args], input=entrada,
                          capture_output=True, text=True, env=env)


class TestForca(unittest.TestCase):
    def test_vitoria(self):
        r = executar("casa", entrada="c\na\ns\n")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Venceu! A palavra era casa", r.stdout)
        self.assertIn("Palavra: c a _ a", r.stdout)

    def test_derrota(self):
        r = executar("-v", "2", "casa", entrada="x\ny\nz\n")
        self.assertEqual(r.returncode, 1)
        self.assertIn("Perdeu! A palavra era casa", r.stdout)

    def test_palpite_inteiro(self):
        self.assertEqual(executar("casa", entrada="CASA\n").returncode, 0)
        r = executar("-v", "1", "casa", entrada="mesa\n")
        self.assertEqual(r.returncode, 1)

    def test_letra_repetida_nao_custa_vida(self):
        r = executar("-v", "1", "oi", entrada="x\n")
        self.assertEqual(r.returncode, 1)
        r = executar("-v", "2", "oi", entrada="o\no\n1\ni\n")
        self.assertEqual(r.returncode, 0)
        self.assertIn("ja tentada", r.stdout)
        self.assertIn("Entrada invalida", r.stdout)

    def test_entrada_incompleta(self):
        r = executar("casa", entrada="c\n")
        self.assertEqual(r.returncode, 3)

    def test_help(self):
        r = executar("-h")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_erros(self):
        self.assertEqual(executar(entrada="").returncode, 2)
        self.assertEqual(executar("ca5a", entrada="").returncode, 2)
        self.assertEqual(executar("-v", "0", "casa", entrada="").returncode, 2)
        self.assertEqual(executar("-z", "casa", entrada="").returncode, 2)


if __name__ == "__main__":
    unittest.main()

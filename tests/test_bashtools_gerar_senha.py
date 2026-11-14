import re
import subprocess
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-tools" / "gerar_senha.sh"


def executar(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


class TestGerarSenha(unittest.TestCase):
    def test_padrao_16_alfanumerica(self):
        r = executar()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertRegex(r.stdout.strip(), r"^[A-Za-z0-9]{16}$")

    def test_tamanho_e_quantidade(self):
        r = executar("-n", "8", "-c", "5")
        linhas = r.stdout.splitlines()
        self.assertEqual(len(linhas), 5)
        self.assertTrue(all(len(s) == 8 for s in linhas))
        self.assertGreater(len(set(linhas)), 1)

    def test_com_simbolos(self):
        r = executar("-n", "200", "-s")
        senha = r.stdout.strip()
        self.assertEqual(len(senha), 200)
        self.assertTrue(re.search(r"[^A-Za-z0-9]", senha))

    def test_help(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_tamanho_invalido(self):
        self.assertEqual(executar("-n", "2").returncode, 1)
        self.assertEqual(executar("-n", "abc").returncode, 1)

    def test_argumento_desconhecido(self):
        self.assertEqual(executar("--xyz").returncode, 1)

    def test_falta_valor(self):
        self.assertEqual(executar("-n").returncode, 1)


if __name__ == "__main__":
    unittest.main()

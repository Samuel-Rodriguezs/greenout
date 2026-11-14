import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-lib" / "menu.sh"


def executar(*args, entrada=None, env=None):
    return subprocess.run(["bash", str(SCRIPT), *args], input=entrada,
                          capture_output=True, text=True, env=env)


class TestMenu(unittest.TestCase):
    ITENS = ("Dizer oi:echo oi", "Soma:echo $((2+3))")

    def test_executa_opcoes_e_sai(self):
        r = executar(*self.ITENS, entrada="1\n2\n0\n")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1) Dizer oi", r.stdout)
        self.assertIn("\noi\n", r.stdout)
        self.assertIn("\n5\n", r.stdout)
        self.assertIn("Ate logo!", r.stdout)

    def test_titulo(self):
        r = executar("-t", "Principal", *self.ITENS, entrada="0\n")
        self.assertIn("== Principal ==", r.stdout)

    def test_opcao_invalida(self):
        r = executar(*self.ITENS, entrada="9\nabc\n0\n")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.count("Opcao invalida"), 2)

    def test_comando_com_falha(self):
        r = executar("Falha:exit 5", entrada="1\n0\n")
        self.assertEqual(r.returncode, 0)
        self.assertIn("terminou com codigo 5", r.stdout)

    def test_entrada_acaba(self):
        r = executar(*self.ITENS, entrada="1\n")
        self.assertEqual(r.returncode, 3)

    def test_help(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_erros(self):
        self.assertEqual(executar(entrada="0\n").returncode, 2)
        self.assertEqual(executar("semdoispontos", entrada="0\n").returncode, 2)
        self.assertEqual(executar(":cmd", entrada="0\n").returncode, 2)
        self.assertEqual(executar("-z", "a:b", entrada="0\n").returncode, 2)


if __name__ == "__main__":
    unittest.main()

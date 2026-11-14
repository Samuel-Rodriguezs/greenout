import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-lib" / "csv2tsv.sh"


def executar(*args, entrada=None, env=None):
    return subprocess.run(["bash", str(SCRIPT), *args], input=entrada,
                          capture_output=True, text=True, env=env)


class TestCsv2Tsv(unittest.TestCase):
    def test_simples(self):
        r = executar(entrada="a,b,c\n1,2,3\n")
        self.assertEqual((r.returncode, r.stdout), (0, "a\tb\tc\n1\t2\t3\n"))

    def test_aspas_e_virgulas(self):
        r = executar(entrada='nome,obs\n"Silva, Ana","disse ""oi"""\n')
        self.assertEqual(r.stdout, 'nome\tobs\nSilva, Ana\tdisse "oi"\n')

    def test_campos_vazios_e_tab_interno(self):
        r = executar(entrada='a,,c\n"x\ty",,\n')
        self.assertEqual(r.stdout, "a\t\tc\nx y\t\t\n")

    def test_arquivo_e_delimitador(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "in.csv"
            p.write_text("a;b\r\n1;2\r\n")
            r = executar("-d", ";", str(p))
            self.assertEqual(r.stdout, "a\tb\n1\t2\n")

    def test_help(self):
        r = executar("-h")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_erros(self):
        self.assertEqual(executar("/nao/existe.csv").returncode, 2)
        self.assertEqual(executar("-d", "ab", entrada="").returncode, 2)
        self.assertEqual(executar("-z").returncode, 2)
        r = executar(entrada='a,"aberta\n')
        self.assertEqual(r.returncode, 1)
        self.assertIn("aspas", r.stderr)


if __name__ == "__main__":
    unittest.main()

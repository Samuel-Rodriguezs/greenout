import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash" / "contar_arquivo.sh"


def executar(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


class TestContarArquivo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def arquivo(self, conteudo):
        p = self.dir / "a.txt"
        p.write_text(conteudo, encoding="utf-8")
        return str(p)

    def test_conta_linhas_e_palavras(self):
        r = executar(self.arquivo("um dois tres\nquatro cinco\n"))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout, "linhas: 2\npalavras: 5\n")

    def test_ultima_linha_sem_quebra(self):
        r = executar(self.arquivo("a b\nc"))
        self.assertEqual(r.stdout, "linhas: 2\npalavras: 3\n")

    def test_arquivo_vazio(self):
        r = executar(self.arquivo(""))
        self.assertEqual(r.stdout, "linhas: 0\npalavras: 0\n")

    def test_arquivo_inexistente(self):
        r = executar(str(self.dir / "nao_existe.txt"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("nao encontrado", r.stderr)

    def test_sem_argumentos(self):
        r = executar()
        self.assertEqual(r.returncode, 2)
        self.assertIn("Uso:", r.stderr)

    def test_help(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)


if __name__ == "__main__":
    unittest.main()

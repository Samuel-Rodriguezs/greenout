import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-tools" / "indice_markdown.sh"


def executar(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


class TestIndiceMarkdown(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name) / "docs"
        (self.dir / "sub").mkdir(parents=True)
        (self.dir / "a.txt").write_text("a")
        (self.dir / "sub" / "b.txt").write_text("b")

    def test_stdout(self):
        r = executar(str(self.dir))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.splitlines(),
                         ["# Índice de docs", "", "- [a.txt](a.txt)", "- [sub/b.txt](sub/b.txt)"])

    def test_grava_arquivo_sem_se_incluir(self):
        saida = self.dir / "INDEX.md"
        r = executar(str(self.dir), str(saida))
        self.assertEqual(r.returncode, 0, r.stderr)
        texto = saida.read_text()
        self.assertIn("[a.txt](a.txt)", texto)
        self.assertNotIn("INDEX.md", texto)

    def test_help(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_pasta_inexistente(self):
        self.assertEqual(executar(str(self.dir / "x")).returncode, 2)

    def test_sem_argumento(self):
        self.assertNotEqual(executar().returncode, 0)


if __name__ == "__main__":
    unittest.main()

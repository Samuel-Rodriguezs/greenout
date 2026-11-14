import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-tools" / "contar_linhas_codigo.sh"


def executar(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


class TestContarLinhasCodigo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        (self.dir / "sub").mkdir()
        (self.dir / "a.py").write_text("1\n2\n3\n")
        (self.dir / "sub" / "b.py").write_text("1\n2\n")
        (self.dir / "c.sh").write_text("x\n")

    def test_todas_extensoes(self):
        r = executar(str(self.dir))
        self.assertEqual(r.returncode, 0, r.stderr)
        linhas = r.stdout.splitlines()
        self.assertIn("py\t2\t5", linhas)
        self.assertIn("sh\t1\t1", linhas)
        self.assertIn("total\t6", linhas)

    def test_filtro_por_extensao(self):
        r = executar(str(self.dir), "sh")
        self.assertEqual(r.stdout.splitlines(), ["sh\t1\t1", "total\t1"])

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

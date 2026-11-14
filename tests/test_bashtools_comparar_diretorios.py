import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-tools" / "comparar_diretorios.sh"


def executar(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


class TestCompararDiretorios(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.d1 = base / "d1"
        self.d2 = base / "d2"
        self.d1.mkdir()
        self.d2.mkdir()

    def test_identicos(self):
        (self.d1 / "a.txt").write_text("x")
        (self.d2 / "a.txt").write_text("x")
        r = executar(str(self.d1), str(self.d2))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("identicos", r.stdout)

    def test_diferencas(self):
        (self.d1 / "a.txt").write_text("1")
        (self.d2 / "a.txt").write_text("2")
        (self.d1 / "so1.txt").write_text("x")
        (self.d2 / "so2.txt").write_text("y")
        r = executar(str(self.d1), str(self.d2))
        self.assertEqual(r.returncode, 3)
        self.assertIn("diferente: a.txt", r.stdout)
        self.assertIn(f"so em {self.d1}: so1.txt", r.stdout)
        self.assertIn(f"so em {self.d2}: so2.txt", r.stdout)

    def test_help(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_diretorio_inexistente(self):
        self.assertEqual(executar(str(self.d1), str(self.d1 / "x")).returncode, 2)

    def test_argumentos_faltando(self):
        self.assertEqual(executar(str(self.d1)).returncode, 1)


if __name__ == "__main__":
    unittest.main()

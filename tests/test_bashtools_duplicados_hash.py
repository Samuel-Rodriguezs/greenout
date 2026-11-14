import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-tools" / "duplicados_hash.sh"


def executar(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


class TestDuplicadosHash(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def test_encontra_duplicados(self):
        (self.dir / "a.txt").write_text("igual")
        (self.dir / "b.txt").write_text("igual")
        (self.dir / "c.txt").write_text("outro")
        r = executar(str(self.dir))
        self.assertEqual(r.returncode, 3)
        self.assertIn("a.txt", r.stdout)
        self.assertIn("b.txt", r.stdout)
        self.assertNotIn("c.txt", r.stdout)

    def test_sem_duplicados(self):
        (self.dir / "a.txt").write_text("1")
        (self.dir / "b.txt").write_text("2")
        r = executar(str(self.dir))
        self.assertEqual(r.returncode, 0)
        self.assertIn("nenhum duplicado", r.stdout)

    def test_help(self):
        r = executar("-h")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_pasta_inexistente(self):
        self.assertEqual(executar(str(self.dir / "x")).returncode, 2)

    def test_sem_argumento(self):
        self.assertNotEqual(executar().returncode, 0)


if __name__ == "__main__":
    unittest.main()

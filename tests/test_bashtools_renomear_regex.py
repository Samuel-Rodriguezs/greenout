import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-tools" / "renomear_regex.sh"


def executar(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


class TestRenomearRegex(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def nomes(self):
        return sorted(p.name for p in self.dir.iterdir())

    def test_renomeia(self):
        (self.dir / "IMG_001.jpg").write_text("1")
        (self.dir / "IMG_002.jpg").write_text("2")
        (self.dir / "outro.txt").write_text("3")
        r = executar(str(self.dir), "s/IMG_([0-9]+)/foto-\\1/")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.nomes(), ["foto-001.jpg", "foto-002.jpg", "outro.txt"])
        self.assertIn("total: 2", r.stdout)

    def test_dry_run(self):
        (self.dir / "a.txt").write_text("1")
        r = executar("--dry-run", str(self.dir), "s/a/b/")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(self.nomes(), ["a.txt"])
        self.assertIn("[dry-run] a.txt -> b.txt", r.stdout)

    def test_conflito(self):
        (self.dir / "a.txt").write_text("1")
        (self.dir / "b.txt").write_text("2")
        r = executar(str(self.dir), "s/^a/b/")
        self.assertEqual(r.returncode, 4)
        self.assertEqual(self.nomes(), ["a.txt", "b.txt"])

    def test_help(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_pasta_inexistente(self):
        self.assertEqual(executar(str(self.dir / "x"), "s/a/b/").returncode, 2)

    def test_expressao_invalida(self):
        self.assertEqual(executar(str(self.dir), "s/a").returncode, 1)

    def test_sem_argumento(self):
        self.assertNotEqual(executar().returncode, 0)


if __name__ == "__main__":
    unittest.main()

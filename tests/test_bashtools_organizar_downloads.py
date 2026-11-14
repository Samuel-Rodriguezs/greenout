import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-tools" / "organizar_downloads.sh"


def executar(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


class TestOrganizarDownloads(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def test_organiza_por_extensao(self):
        (self.dir / "a.PDF").write_text("1")
        (self.dir / "b.txt").write_text("2")
        (self.dir / "LEIAME").write_text("3")
        r = executar(str(self.dir))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.dir / "pdf" / "a.PDF").exists())
        self.assertTrue((self.dir / "txt" / "b.txt").exists())
        self.assertTrue((self.dir / "sem_extensao" / "LEIAME").exists())
        self.assertIn("total: 3", r.stdout)

    def test_dry_run_nao_move(self):
        (self.dir / "a.txt").write_text("x")
        r = executar("--dry-run", str(self.dir))
        self.assertEqual(r.returncode, 0)
        self.assertIn("[dry-run] a.txt -> txt/", r.stdout)
        self.assertTrue((self.dir / "a.txt").exists())
        self.assertFalse((self.dir / "txt").exists())

    def test_help(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_pasta_inexistente(self):
        r = executar(str(self.dir / "nao_existe"))
        self.assertEqual(r.returncode, 2)

    def test_sem_argumento(self):
        self.assertNotEqual(executar().returncode, 0)


if __name__ == "__main__":
    unittest.main()

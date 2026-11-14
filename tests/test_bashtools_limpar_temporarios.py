import os
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-tools" / "limpar_temporarios.sh"


def executar(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


class TestLimparTemporarios(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.velho = self.dir / "velho.tmp"
        self.novo = self.dir / "novo.tmp"
        self.normal = self.dir / "velho.txt"
        for f in (self.velho, self.novo, self.normal):
            f.write_text("x")
        antigo = time.time() - 10 * 86400
        for f in (self.velho, self.normal):
            os.utime(f, (antigo, antigo))

    def test_remove_somente_temporarios_antigos(self):
        r = executar(str(self.dir), "5")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(self.velho.exists())
        self.assertTrue(self.novo.exists())
        self.assertTrue(self.normal.exists())
        self.assertIn("total: 1", r.stdout)

    def test_dry_run(self):
        r = executar("--dry-run", str(self.dir), "5")
        self.assertEqual(r.returncode, 0)
        self.assertTrue(self.velho.exists())
        self.assertIn("[dry-run]", r.stdout)

    def test_help(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_pasta_inexistente(self):
        self.assertEqual(executar(str(self.dir / "x"), "5").returncode, 2)

    def test_dias_invalido(self):
        self.assertEqual(executar(str(self.dir), "abc").returncode, 1)

    def test_sem_argumento(self):
        self.assertNotEqual(executar().returncode, 0)


if __name__ == "__main__":
    unittest.main()

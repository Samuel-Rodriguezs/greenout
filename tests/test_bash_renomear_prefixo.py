import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash" / "renomear_prefixo.sh"


def executar(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


class TestRenomearPrefixo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        (self.dir / "a.txt").write_text("A")
        (self.dir / "b.txt").write_text("B")
        (self.dir / "sub").mkdir()
        (self.dir / "sub" / "c.txt").write_text("C")

    def nomes(self):
        return sorted(p.name for p in self.dir.iterdir())

    def test_renomeia(self):
        r = executar("novo_", str(self.dir))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, "a.txt -> novo_a.txt\nb.txt -> novo_b.txt\n")
        self.assertEqual(self.nomes(), ["novo_a.txt", "novo_b.txt", "sub"])
        self.assertEqual((self.dir / "novo_a.txt").read_text(), "A")
        # nao recursivo
        self.assertTrue((self.dir / "sub" / "c.txt").exists())

    def test_dry_run_nao_altera(self):
        r = executar("--dry-run", "x_", str(self.dir))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, "a.txt -> x_a.txt\nb.txt -> x_b.txt\n")
        self.assertEqual(self.nomes(), ["a.txt", "b.txt", "sub"])

    def test_nao_sobrescreve(self):
        (self.dir / "x_a.txt").write_text("existente")
        r = executar("x_", str(self.dir))
        self.assertEqual(r.returncode, 1)
        self.assertIn("ja existe", r.stderr)
        self.assertEqual((self.dir / "x_a.txt").read_text(), "existente")
        self.assertTrue((self.dir / "a.txt").exists())

    def test_diretorio_inexistente(self):
        r = executar("p_", str(self.dir / "nada"))
        self.assertEqual(r.returncode, 1)

    def test_prefixo_invalido(self):
        self.assertEqual(executar("a/b", str(self.dir)).returncode, 2)
        self.assertEqual(executar("", str(self.dir)).returncode, 2)

    def test_uso_e_help(self):
        self.assertEqual(executar().returncode, 2)
        self.assertEqual(executar("--foo", "p", str(self.dir)).returncode, 2)
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)


if __name__ == "__main__":
    unittest.main()

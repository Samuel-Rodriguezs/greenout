import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-tools" / "rotacao_logs.sh"


def executar(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


class TestRotacaoLogs(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.log = Path(self.tmp.name) / "app.log"

    def test_primeira_rotacao(self):
        self.log.write_text("v1")
        r = executar(str(self.log))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.log.read_text(), "")
        self.assertEqual(Path(str(self.log) + ".1").read_text(), "v1")

    def test_descarta_mais_antigo(self):
        for versao in ("v1", "v2", "v3", "v4"):
            self.log.write_text(versao)
            self.assertEqual(executar(str(self.log), "2").returncode, 0)
        self.assertEqual(Path(str(self.log) + ".1").read_text(), "v4")
        self.assertEqual(Path(str(self.log) + ".2").read_text(), "v3")
        self.assertFalse(Path(str(self.log) + ".3").exists())

    def test_help(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_arquivo_inexistente(self):
        self.assertEqual(executar(str(self.log)).returncode, 2)

    def test_max_invalido(self):
        self.log.write_text("x")
        self.assertEqual(executar(str(self.log), "abc").returncode, 1)

    def test_sem_argumento(self):
        self.assertNotEqual(executar().returncode, 0)


if __name__ == "__main__":
    unittest.main()

import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-tools" / "gerar_gitignore.sh"


def executar(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


class TestGerarGitignore(unittest.TestCase):
    def test_python_stdout(self):
        r = executar("python")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("__pycache__/", r.stdout.splitlines())

    def test_node_em_arquivo(self):
        with tempfile.TemporaryDirectory() as d:
            alvo = Path(d) / ".gitignore"
            r = executar("node", str(alvo))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("node_modules/", alvo.read_text().splitlines())

    def test_help(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Tipos:", r.stdout)

    def test_tipo_desconhecido(self):
        r = executar("cobol")
        self.assertEqual(r.returncode, 2)
        self.assertIn("desconhecido", r.stderr)

    def test_sem_argumento(self):
        self.assertNotEqual(executar().returncode, 0)


if __name__ == "__main__":
    unittest.main()

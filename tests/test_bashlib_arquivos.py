import fcntl
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-lib" / "arquivos.sh"


def executar(*args, entrada=None, env=None):
    return subprocess.run(["bash", str(SCRIPT), *args], input=entrada,
                          capture_output=True, text=True, env=env)


class TestArquivos(unittest.TestCase):
    def test_tmprun_cria_e_remove(self):
        r = executar("tmprun", "bash", "-c", 'echo "$ARQ_TMPDIR"; touch "$ARQ_TMPDIR/x"; stat -c %a "$ARQ_TMPDIR"')
        self.assertEqual(r.returncode, 0, r.stderr)
        caminho, modo = r.stdout.split()
        self.assertEqual(modo, "700")
        self.assertFalse(Path(caminho).exists())

    def test_tmprun_limpa_mesmo_com_falha(self):
        r = executar("tmprun", "bash", "-c", 'echo "$ARQ_TMPDIR"; exit 7')
        self.assertEqual(r.returncode, 7)
        self.assertFalse(Path(r.stdout.strip()).exists())

    def test_lock_livre(self):
        with tempfile.TemporaryDirectory() as d:
            r = executar("lock", str(Path(d) / "l.lock"), "echo", "dentro")
            self.assertEqual((r.returncode, r.stdout), (0, "dentro\n"))

    def test_lock_ocupado(self):
        with tempfile.TemporaryDirectory() as d:
            arq = Path(d) / "l.lock"
            with open(arq, "w") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                r = executar("lock", str(arq), "echo", "nao")
                self.assertEqual(r.returncode, 75)
                self.assertNotIn("nao", r.stdout)
            r = executar("lock", str(arq), "echo", "sim")
            self.assertEqual(r.returncode, 0)

    def test_lock_propaga_codigo(self):
        with tempfile.TemporaryDirectory() as d:
            r = executar("lock", str(Path(d) / "l"), "bash", "-c", "exit 4")
            self.assertEqual(r.returncode, 4)

    def test_source(self):
        r = subprocess.run(["bash", "-c", f'source "{SCRIPT}"; arq_criar_tempdir; test -d "$ARQ_TMPDIR" && echo "$ARQ_TMPDIR"'],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(Path(r.stdout.strip()).exists())

    def test_help(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_erros(self):
        self.assertEqual(executar().returncode, 2)
        self.assertEqual(executar("tmprun").returncode, 2)
        self.assertEqual(executar("lock", "x").returncode, 2)
        self.assertEqual(executar("outro").returncode, 2)


if __name__ == "__main__":
    unittest.main()
